# -*- coding: utf-8 -*-
from abm_mercados import AgenteBase, MundoBase, Simulacao
import random, math

try:
    from .validation_utils import save_all_outputs, ensure_dir
except ImportError:
    from validation_utils import save_all_outputs, ensure_dir


# Mundo geral: tendência lenta + mean-reversion + ordens
class MundoGeral(MundoBase):
    def __init__(
        self, preco_inicial=100.0, drift=0.0002, mean_rev=0.02, depth=300.0, seed=21
    ):
        super().__init__()
        random.seed(seed)
        self.preco = float(preco_inicial)
        self.drift = float(drift)
        self.k_mr = float(mean_rev)
        self.depth = float(depth)
        self._ordens = []
        self.h_preco = []
        self.h_flow = []
        self.ciclo = 0
        self._media = self.preco

    def enviar_ordem(self, agente_id: int, qtd: float):
        if not isinstance(qtd, (int, float)) or qtd == 0.0:
            return
        self._ordens.append((agente_id, float(qtd)))

    def step(self):
        # média móvel simples
        alpha = 0.02
        self._media = (1 - alpha) * self._media + alpha * self.preco

        desequilibrio = sum(q for _, q in self._ordens) if self._ordens else 0.0
        impacto = desequilibrio / max(1.0, self.depth)
        mr = self.k_mr * (self._media - self.preco) / max(1e-9, self._media)
        ruido = random.gauss(0, 0.003)

        # log-preço: drift + mean-reversion + impacto + ruído
        self.preco *= math.exp(self.drift + mr + 0.02 * impacto + ruido)

        self.h_preco.append(self.preco)
        self.h_flow.append(desequilibrio)
        self._ordens.clear()
        self.ciclo += 1


class AgenteTendencia(AgenteBase):
    def __init__(self, id_ag, caixa=5_000.0, pos=0.0, k=0.1):
        super().__init__(id_ag)
        self.caixa = float(caixa)
        self.pos = float(pos)
        self.k = float(k)
        self._ult_preco = None

    def decidir(self, amb: MundoGeral):
        if self._ult_preco is None:
            self._ult_preco = amb.preco
            return
        ret = amb.preco / self._ult_preco - 1.0
        s = self.k * ret
        if s > 0 and self.caixa > 0:
            qtd = max(1.0, s * self.caixa / amb.preco)
            custo = qtd * amb.preco
            if custo <= self.caixa:
                self.caixa -= custo
                self.pos += qtd
                amb.enviar_ordem(self.id, +qtd)
        elif s < 0 and self.pos > 0:
            qtd = min(self.pos, max(1.0, -s * self.pos))
            self.caixa += qtd * amb.preco
            self.pos -= qtd
            amb.enviar_ordem(self.id, -qtd)
        self._ult_preco = amb.preco


class AgenteContrarian(AgenteBase):
    def __init__(self, id_ag, caixa=5_000.0, pos=0.0, k=0.1):
        super().__init__(id_ag)
        self.caixa = float(caixa)
        self.pos = float(pos)
        self.k = float(k)
        self._ult_preco = None

    def decidir(self, amb: MundoGeral):
        if self._ult_preco is None:
            self._ult_preco = amb.preco
            return
        ret = amb.preco / self._ult_preco - 1.0
        s = -self.k * ret  # contrarian
        if s > 0 and self.caixa > 0:
            qtd = max(1.0, s * self.caixa / amb.preco)
            custo = qtd * amb.preco
            if custo <= self.caixa:
                self.caixa -= custo
                self.pos += qtd
                amb.enviar_ordem(self.id, +qtd)
        elif s < 0 and self.pos > 0:
            qtd = min(self.pos, max(1.0, -s * self.pos))
            self.caixa += qtd * amb.preco
            self.pos -= qtd
            amb.enviar_ordem(self.id, -qtd)
        self._ult_preco = amb.preco


def _criar() -> MundoGeral:
    m = MundoGeral(
        preco_inicial=100.0, drift=0.0002, mean_rev=0.03, depth=300.0, seed=21
    )
    for i in range(8):
        m.adicionar_agente(AgenteTendencia(10 + i, caixa=6_000.0, pos=0.0, k=0.12))
    for j in range(8):
        m.adicionar_agente(AgenteContrarian(100 + j, caixa=6_000.0, pos=0.0, k=0.10))
    return m


def _run(m, ciclos=252):
    try:
        sim = Simulacao(m, ciclos)
        sim.executar()
    except TypeError:
        sim = Simulacao(m)
        for fn in ("executar", "run", "rodar", "start"):
            f = getattr(sim, fn, None)
            if not f:
                continue
            try:
                f()
                break
            except TypeError:
                try:
                    f(ciclos)
                    break
                except TypeError:
                    continue
    return m


if __name__ == "__main__":
    m = _criar()
    m = _run(m, 252)
    outdir = ensure_dir("./outputs/mercado_geral")
    met, pasta = save_all_outputs(
        "MERCADO_GERAL",
        outdir,
        m.h_preco,
        m.h_flow,
        extras={"drift": m.drift, "mean_rev": m.k_mr, "depth": m.depth},
    )
    print("Saída Mercado Geral:", pasta, "\nMétricas:", met)

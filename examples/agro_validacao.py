# -*- coding: utf-8 -*-
from abm import AgenteBase, MundoBase, Simulacao
import random, math

try:
    from .validation_utils import save_all_outputs, ensure_dir
except ImportError:
    from validation_utils import save_all_outputs, ensure_dir


# Mundo Agro: preço afetado por oferta/colheita sazonal + ordens
class MundoAgro(MundoBase):
    def __init__(
        self, preco_inicial=50.0, sazonal_amp=0.10, k_ajuste=0.015, depth=200.0, seed=11
    ):
        super().__init__()
        random.seed(seed)
        self.preco = float(preco_inicial)
        self.saz_amp = float(sazonal_amp)
        self.k = float(k_ajuste)
        self.depth = float(depth)
        self._ordens = []
        self.h_preco = []
        self.h_demanda = []
        self.ciclo = 0

    def enviar_ordem(self, agente_id: int, qtd: float):
        if not isinstance(qtd, (int, float)) or qtd == 0.0:
            return
        self._ordens.append((agente_id, float(qtd)))

    def _sazonal(self):
        # componente senoidal simples (colheitas/entressafra)
        return self.saz_amp * math.sin(2 * math.pi * (self.ciclo % 252) / 252.0)

    def step(self):
        desequilibrio = sum(q for _, q in self._ordens) if self._ordens else 0.0
        impacto = self.k * (desequilibrio / max(1.0, self.depth))
        saz = self._sazonal()
        ruido = random.gauss(0, 0.003)
        self.preco *= math.exp(impacto + saz + ruido)
        self.h_preco.append(self.preco)
        self.h_demanda.append(desequilibrio)
        self._ordens.clear()
        self.ciclo += 1


class Produtor(AgenteBase):
    def __init__(self, id_ag, custo_medio=45.0, estoque=100.0, hedge_frac=0.3):
        super().__init__(id_ag)
        self.custo = float(custo_medio)
        self.estoque = float(estoque)
        self.hedge = float(hedge_frac)

    def decidir(self, ambiente: MundoAgro):
        # vende quando preço >> custo; recompõe estoque quando << custo (simples)
        if ambiente.preco > 1.1 * self.custo and self.estoque > 0:
            q = min(self.estoque * self.hedge, self.estoque)
            self.estoque -= q
            ambiente.enviar_ordem(self.id, -q)
        elif ambiente.preco < 0.95 * self.custo:
            q = max(1.0, self.estoque * 0.05)
            self.estoque += q  # comprou insumos? simplificação
            ambiente.enviar_ordem(self.id, +q)


class Comerciante(AgenteBase):
    def __init__(self, id_ag, caixa=10_000.0, alvo_estoque=200.0, k_repos=0.1):
        super().__init__(id_ag)
        self.caixa = float(caixa)
        self.est = 0.0
        self.alvo = float(alvo_estoque)
        self.k = float(k_repos)

    def decidir(self, ambiente: MundoAgro):
        gap = self.alvo - self.est
        q = self.k * gap
        if q > 0:
            custo = q * ambiente.preco
            if custo <= self.caixa:
                self.caixa -= custo
                self.est += q
                ambiente.enviar_ordem(self.id, +q)
        else:
            qv = abs(q)
            if qv <= self.est:
                self.caixa += qv * ambiente.preco
                self.est -= qv
                ambiente.enviar_ordem(self.id, -qv)


def _criar() -> MundoAgro:
    m = MundoAgro()
    m.adicionar_agente(Produtor(1, custo_medio=45.0, estoque=300.0, hedge_frac=0.25))
    m.adicionar_agente(Produtor(2, custo_medio=48.0, estoque=200.0, hedge_frac=0.30))
    m.adicionar_agente(
        Comerciante(10, caixa=20_000.0, alvo_estoque=400.0, k_repos=0.08)
    )
    m.adicionar_agente(
        Comerciante(11, caixa=12_000.0, alvo_estoque=250.0, k_repos=0.12)
    )
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
    outdir = ensure_dir("./outputs/agro")
    met, pasta = save_all_outputs(
        "AGRO",
        outdir,
        m.h_preco,
        m.h_demanda,
        extras={"sazonal_amp": m.saz_amp, "k_ajuste": m.k},
    )
    print("Saída AGRO:", pasta, "\nMétricas:", met)

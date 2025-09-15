# -*- coding: utf-8 -*-
from abm import AgenteBase, MundoBase, Simulacao
import random, math

# utilitários (compatível: python -m examples.fii_validacao)
try:
    from .validation_utils import save_all_outputs, ensure_dir
except ImportError:
    from validation_utils import save_all_outputs, ensure_dir


# ===================== Mundo FII =====================
class MundoFII(MundoBase):
    """
    Mundo simples de FII:
      - preço ajusta por desequilíbrio de ordens + ruído
      - paga dividendo proporcional ao yield anual
    """

    def __init__(
        self,
        preco_inicial=100.0,
        ciclos_por_ano=252,
        k_ajuste=0.02,
        seed=42,
        depth=250.0,
        div_yield_anual=0.10,
    ):
        super().__init__()
        random.seed(seed)
        self.preco = float(preco_inicial)
        self.ciclos_por_ano = int(ciclos_por_ano)
        self.k = float(k_ajuste)  # ganho do ajuste de preço (impacto)
        self.depth = float(depth)  # “profundidade” de livro
        self.div_yield_anual = float(div_yield_anual)

        # buffer de ordens do ciclo corrente
        self.ordens = []  # cada item: {"agent_id": int, "qtd": float}

        # históricos
        self.h_preco = [self.preco]  # já guarda o preço inicial
        self.h_demanda_liquida = []
        self.h_dividendo = []

        self.ciclo = 0

    def registrar_ordem(self, agent_id: int, qtd: float) -> None:
        """Chamado pelos agentes em .agir(ambiente). Apenas acumula ordens."""
        if qtd is None or qtd == 0.0:
            return
        self.ordens.append({"agent_id": int(agent_id), "qtd": float(qtd)})

    def _paga_dividendo(self) -> float:
        dy = self.div_yield_anual / self.ciclos_por_ano  # yield por ciclo
        return self.preco * dy

    def atualizar_ambiente(self) -> None:
        """
        Chamado pelo framework ao final de cada ciclo, depois que todos
        os agentes executaram .agir(ambiente).
        Agrega ordens -> ajusta preço -> paga dividendos -> loga históricos.
        """
        # 1) agrega o desequilíbrio
        desequilibrio = sum(o["qtd"] for o in self.ordens) if self.ordens else 0.0
        # 2) impacto (linear) + ruído pequeno
        ruido = random.gauss(0.0, 0.002)
        impacto = self.k * (desequilibrio / max(1.0, self.depth))
        self.preco *= math.exp(impacto + ruido)

        # 3) paga dividendo proporcional ao preço atual
        d = self._paga_dividendo()
        for ag in self.agentes:
            # se o agente implementa receber_dividendo, repassa
            rec = getattr(ag, "receber_dividendo", None)
            if callable(rec):
                rec(d)

        # 4) registra e limpa buffers
        self.h_demanda_liquida.append(desequilibrio)
        self.h_dividendo.append(d)
        self.h_preco.append(self.preco)
        self.ordens.clear()
        self.ciclo += 1

    # >>> ALIASES DE COMPATIBILIDADE (muito importante):
    def step(self) -> None:
        """Alguns frameworks chamam `step()` no mundo ao fim do ciclo."""
        self.atualizar_ambiente()


    def atualizar(self) -> None:
        """Outros chamam `atualizar()`; delega para o mesmo núcleo."""
        self.atualizar_ambiente()


# ===================== Agentes =====================
class AgenteFundamentalista(AgenteBase):
    def __init__(
        self,
        id_ag,
        caixa=2_000.0,
        pos=0.0,
        valor_intrinseco=110.0,
        toler=0.03,
        prop=0.15,
    ):
        super().__init__(id_ag)
        self.caixa = float(caixa)
        self.pos = float(pos)
        self.valor = float(valor_intrinseco)
        self.toler = float(toler)
        self.prop = float(prop)

    # O framework chama .decidir(); aqui apenas delegamos para .agir().
    def decidir(self, ambiente: "MundoFII"):
        self.agir(ambiente)

    # ÚNICO lugar com a lógica de negociação
    def agir(self, ambiente: "MundoFII") -> None:
        diff = (self.valor - ambiente.preco) / max(1e-9, self.valor)
        if diff > self.toler and self.caixa > 0:
            # compra
            qtd = max(1.0, self.prop * self.caixa / ambiente.preco)
            custo = qtd * ambiente.preco
            if custo <= self.caixa:
                self.caixa -= custo
                self.pos += qtd
                ambiente.registrar_ordem(self.id, +qtd)
        elif diff < -self.toler and self.pos > 0:
            # venda
            qtd = max(1.0, self.prop * self.pos)
            qtd = min(qtd, self.pos)
            self.caixa += qtd * ambiente.preco
            self.pos -= qtd
            ambiente.registrar_ordem(self.id, -qtd)

    def receber_dividendo(self, d_por_cota):
        if self.pos > 0:
            self.caixa += d_por_cota * self.pos


class NoiseTrader(AgenteBase):
    def __init__(self, id_ag, caixa=1_000.0, pos=0.0, max_lote=4.0, prob_compra=0.55):
        super().__init__(id_ag)
        self.caixa = float(caixa)
        self.pos = float(pos)
        self.max_lote = float(max_lote)
        self.prob_compra = float(prob_compra)

    # Delegação para compatibilidade com o framework
    def decidir(self, ambiente: "MundoFII"):
        self.agir(ambiente)

    def agir(self, ambiente: "MundoFII") -> None:
        lado = +1 if random.random() < self.prob_compra else -1  # <- usa prob_compra
        qtd = random.uniform(0.0, self.max_lote) * lado

        # restrições simples
        if qtd > 0 and (qtd * ambiente.preco) > self.caixa:
            return
        if qtd < 0 and abs(qtd) > self.pos:
            return

        # efetiva e registra
        if qtd > 0:
            self.caixa -= qtd * ambiente.preco
            self.pos += qtd
        else:
            self.caixa += abs(qtd) * ambiente.preco
            self.pos -= abs(qtd)

        ambiente.registrar_ordem(self.id, qtd)

    def receber_dividendo(self, d_por_cota):
        if self.pos > 0:
            self.caixa += d_por_cota * self.pos


# ===================== Runner =====================
def _criar_mundo_e_agentes() -> MundoFII:
    mundo = MundoFII(
        preco_inicial=100.0,
        ciclos_por_ano=252,
        k_ajuste=0.02,
        depth=250.0,
        div_yield_anual=0.10,
        seed=7,
    )
    # fundamentalistas heterogêneos
    base_vals = [95, 105, 115, 125, 135]
    for i in range(15):
        val = base_vals[i % len(base_vals)]
        mundo.adicionar_agente(
            AgenteFundamentalista(
                id_ag=i,
                caixa=2_000.0,
                pos=0.0,
                valor_intrinseco=val,
                toler=0.03,
                prop=0.15,
            )
        )
    # noise traders
    for j in range(10):
        mundo.adicionar_agente(
            NoiseTrader(
                id_ag=100 + j, caixa=1_000.0, pos=0.0, max_lote=4.0, prob_compra=0.55
            )
        )
    return mundo


def _rodar_simulacao(mundo: MundoFII, ciclos=252):
    # Construção compatível com diferentes assinaturas
    try:
        sim = Simulacao(mundo, ciclos)  # muitos frameworks aceitam (ambiente, n)
        try:
            sim.executar()  # sem argumento
        except TypeError:
            # fallback para nomes alternativos
            for fn in ("run", "rodar", "start", "executar"):
                m = getattr(sim, fn, None)
                if not m:
                    continue
                try:
                    m()
                    break
                except TypeError:
                    try:
                        m(ciclos)
                        break
                    except TypeError:
                        continue
    except TypeError:
        # construtor só com (ambiente)
        sim = Simulacao(mundo)
        # agora tentamos executar
        ran = False
        for callsig in (
            lambda: sim.executar(),
            lambda: sim.run(),
            lambda: sim.rodar(),
            lambda: sim.start(),
            lambda: sim.executar(ciclos),
            lambda: sim.run(ciclos),
            lambda: sim.rodar(ciclos),
            lambda: sim.start(ciclos),
        ):
            try:
                callsig()
                ran = True
                break
            except Exception:
                continue
        if not ran:
            raise RuntimeError(
                "Não foi possível executar a simulação com as assinaturas conhecidas."
            )
    return mundo


if __name__ == "__main__":
    mundo = _criar_mundo_e_agentes()
    mundo = _rodar_simulacao(mundo, ciclos=252)
    outdir = ensure_dir("./outputs/fii")
    met, pasta = save_all_outputs(
        tag="FII",
        outdir=outdir,
        precos=mundo.h_preco,
        demanda_liquida=mundo.h_demanda_liquida,
        extras={
            "div_yield_anual": mundo.div_yield_anual,
            "k_ajuste": mundo.k,
            "depth": mundo.depth,
        },
    )
    print("Saída FII salva em:", pasta)
    print("Métricas:", met)

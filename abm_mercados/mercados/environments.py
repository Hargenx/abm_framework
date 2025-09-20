from __future__ import annotations
import math, random
from typing import Optional, List
from ..core.world import MundoBase
from ..core.orderbook import OrderBookIngenuo


class MercadoSimples(MundoBase):
    """Mercado de um ativo com ajuste por desequilíbrio + ruído + (opcional) dividendo."""

    def __init__(
        self,
        preco_inicial: float = 100.0,
        ciclos_por_ano: int = 252,
        k_impacto: float = 0.02,
        depth: float = 250.0,
        seed: int = 7,
        dy_anual: float = 0.0,  # FII => >0
        choques: Optional[List[float]] = None,  # ex.: sazonais no Agro
    ) -> None:
        super().__init__()
        random.seed(seed)
        self.preco = float(preco_inicial)
        self.ciclos_por_ano = int(ciclos_por_ano)
        self.k = float(k_impacto)
        self.depth = float(depth)
        self.dy_anual = float(dy_anual)
        self.choques = choques or []
        self.book = OrderBookIngenuo()

        self.h_preco = [self.preco]  # loga o inicial
        self.h_deseq = []
        self.h_div = []

    def _dividendo(self) -> float:
        if self.dy_anual <= 0.0:
            return 0.0
        return self.preco * (self.dy_anual / self.ciclos_por_ano)

    def atualizar_ambiente(self) -> None:
        desequilibrio = self.book.agregar(self.ordens)
        ruido = random.gauss(0.0, 0.002)
        choque = self.choques[self.ciclo] if self.ciclo < len(self.choques) else 0.0
        impacto = self.k * (desequilibrio / max(1.0, self.depth)) + choque
        self.preco *= math.exp(impacto + ruido)

        d = self._dividendo()
        self.h_div.append(d)
        for inv in self.investidores:
            rec = getattr(inv, "receber_dividendo", None)
            if callable(rec) and getattr(inv, "pos", 0.0) > 0.0:
                inv.receber_dividendo(d)

        self.h_deseq.append(desequilibrio)
        self.h_preco.append(self.preco)
        self.ordens.clear()
        self.ciclo += 1

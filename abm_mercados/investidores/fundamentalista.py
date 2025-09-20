from __future__ import annotations
from dataclasses import dataclass
from ..core.investidor import InvestidorBase


@dataclass
class InvestidorFundamentalista(InvestidorBase):
    caixa: float = 2_000.0
    pos: float = 0.0
    valor_intrinseco: float = 110.0
    toler: float = 0.03
    prop: float = 0.15

    def receber_dividendo(self, d_por_cota: float) -> None:
        if self.pos > 0:
            self.caixa += d_por_cota * self.pos

    def agir(self, ambiente) -> None:
        v, p = self.valor_intrinseco, ambiente.preco
        diff = (v - p) / max(1e-9, v)

        if diff > self.toler and self.caixa > 0:
            qtd = max(1.0, self.prop * self.caixa / p)
            custo = qtd * p
            if custo <= self.caixa:
                self.caixa -= custo
                self.pos += qtd
                ambiente.registrar_ordem(self.id, +qtd)

        elif diff < -self.toler and self.pos > 0:
            qtd = max(1.0, self.prop * self.pos)
            qtd = min(qtd, self.pos)
            self.caixa += qtd * p
            self.pos -= qtd
            ambiente.registrar_ordem(self.id, -qtd)

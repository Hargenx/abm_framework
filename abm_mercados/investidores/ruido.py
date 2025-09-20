from __future__ import annotations
from dataclasses import dataclass
import random
from ..core.investidor import InvestidorBase


@dataclass
class InvestidorRuido(InvestidorBase):
    caixa: float = 1_000.0
    pos: float = 0.0
    max_lote: float = 4.0
    prob_compra: float = 0.55

    def receber_dividendo(self, d_por_cota: float) -> None:
        if self.pos > 0:
            self.caixa += d_por_cota * self.pos

    def agir(self, ambiente) -> None:
        lado = +1 if random.random() < self.prob_compra else -1
        qtd = random.uniform(0.0, self.max_lote) * lado

        if qtd > 0:
            custo = qtd * ambiente.preco
            if custo <= self.caixa:
                self.caixa -= custo
                self.pos += qtd
                ambiente.registrar_ordem(self.id, +qtd)
        elif abs(qtd) <= self.pos and abs(qtd) > 0:
            self.caixa += abs(qtd) * ambiente.preco
            self.pos -= abs(qtd)
            ambiente.registrar_ordem(self.id, qtd)

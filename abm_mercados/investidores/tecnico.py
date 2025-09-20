from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from ..core.investidor import InvestidorBase


@dataclass
class InvestidorTendencia(InvestidorBase):
    caixa: float = 1_500.0
    pos: float = 0.0
    janela: int = 15
    alav: float = 0.2

    def agir(self, ambiente) -> None:
        h = ambiente.h_preco
        if len(h) <= self.janela:
            return
        r = np.diff(np.log(np.asarray(h[-self.janela - 1 :])))
        sinal = np.sign(np.sum(r))
        qtd = (
            max(
                1.0,
                self.alav * (self.caixa + self.pos * ambiente.preco) / ambiente.preco,
            )
            * sinal
        )

        if qtd > 0:
            custo = qtd * ambiente.preco
            if custo <= self.caixa:
                self.caixa -= custo
                self.pos += qtd
                ambiente.registrar_ordem(self.id, +qtd)
        elif qtd < 0 and abs(qtd) <= self.pos:
            self.caixa += abs(qtd) * ambiente.preco
            self.pos -= abs(qtd)
            ambiente.registrar_ordem(self.id, qtd)

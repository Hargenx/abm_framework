from __future__ import annotations
from typing import Optional

from abm_mercados.core.world import MundoBase


class Simulacao:
    def __init__(self, mundo: "MundoBase") -> None:
        self.mundo = mundo

    def executar(self, n_ciclos: Optional[int] = None) -> None:
        if n_ciclos is None:
            n_ciclos = 1
        for _ in range(n_ciclos):
            self.mundo._step_start()
            for inv in self.mundo.investidores:
                inv.agir(self.mundo)
            self.mundo.atualizar_ambiente()
            self.mundo._step_end()

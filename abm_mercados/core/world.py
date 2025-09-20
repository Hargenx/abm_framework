from __future__ import annotations
from typing import Any, Dict, List, Callable, Optional
import numpy as np
import random


class MundoBase:
    """
    Extensão-padrão:
      - Subclasse e implemente .atualizar_ambiente()
      - Use .registrar_ordem(investidor_id, qtd) nas ações
      - Callbacks (antes/depois do ciclo) para instrumentação
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self.investidores: List[Any] = []
        self.ordens: List[Dict[str, float]] = []
        self.ciclo: int = 0
        self.random = random.Random(seed)
        np.random.seed(seed if seed is not None else 0)
        self._on_step_start: List[Callable[["MundoBase"], None]] = []
        self._on_step_end: List[Callable[["MundoBase"], None]] = []

    # extensibilidade
    def on_step_start(self, cb: Callable[["MundoBase"], None]) -> None:
        self._on_step_start.append(cb)

    def on_step_end(self, cb: Callable[["MundoBase"], None]) -> None:
        self._on_step_end.append(cb)

    def adicionar_investidor(self, inv: Any) -> None:
        self.investidores.append(inv)

    def registrar_ordem(self, investidor_id: int, qtd: float) -> None:
        if not qtd:
            return
        self.ordens.append({"investidor_id": int(investidor_id), "qtd": float(qtd)})

    def atualizar_ambiente(self) -> None:
        raise NotImplementedError

    # ganchos do loop
    def _step_start(self):  # interno
        for cb in self._on_step_start:
            cb(self)

    def _step_end(self):
        for cb in self._on_step_end:
            cb(self)

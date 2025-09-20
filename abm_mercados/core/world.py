from __future__ import annotations
from typing import Any, Dict, List


class MundoBase:
    def __init__(self) -> None:
        self.investidores: List[Any] = []
        self.ordens: List[Dict[str, float]] = []  # {"investidor_id":int,"qtd":float}
        self.ciclo: int = 0

    def adicionar_investidor(self, inv: Any) -> None:
        self.investidores.append(inv)

    def registrar_ordem(self, investidor_id: int, qtd: float) -> None:
        if not qtd:
            return
        self.ordens.append({"investidor_id": int(investidor_id), "qtd": float(qtd)})

    def atualizar_ambiente(self) -> None:
        """Processar ordens, atualizar preço/estado, pagar dividendos, logar."""
        raise NotImplementedError

from __future__ import annotations


class OrderBookIngenuo:
    """
    Placeholder: agrega ordens líquidas e devolve desequilíbrio.
    Você pode expandir para CDA (continuous double auction) depois.
    """

    def __init__(self) -> None:
        pass

    def agregar(self, ordens):
        return sum(o["qtd"] for o in (ordens or []))

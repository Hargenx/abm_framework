from __future__ import annotations
from ..core.metrics import painel_estilizados


def validar_fatos(precos: list[float]) -> dict:
    return painel_estilizados(precos)

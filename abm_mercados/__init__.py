# API pública (estável)
from .core.investidor import InvestidorBase
from .core.world import MundoBase
from .core.simulation import Simulacao
from .core.orderbook import OrderBookIngenuo
from .core.metrics import painel_estilizados

# compatibilidade (se alguém usar "AgenteBase")
AgenteBase = InvestidorBase

__all__ = [
    "InvestidorBase",
    "AgenteBase",
    "MundoBase",
    "Simulacao",
    "OrderBookIngenuo",
    "painel_estilizados",
]

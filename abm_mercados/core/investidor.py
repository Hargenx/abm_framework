from __future__ import annotations
from dataclasses import dataclass

from abm_mercados.core.world import MundoBase

@dataclass
class InvestidorBase:
    id: int

    def reset(self, ambiente: "MundoBase") -> None:
        pass

    def agir(self, ambiente: "MundoBase") -> None:
        """Cada investidor decide e registra ordens no ambiente."""
        raise NotImplementedError

# Só use se instalar torch; caso contrário, ignore este arquivo.
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

try:
    import torch
    import torch.nn as nn
except Exception:
    torch = None
from ..core.investidor import AgenteBase


class _MLP(nn.Module):
    def __init__(self, dim_in, dim_out):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim_in, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, dim_out),
        )

    def forward(self, x):
        return self.net(x)


@dataclass
class AgenteDRL(AgenteBase):
    caixa: float = 2_000.0
    pos: float = 0.0
    tamanho_max: float = 5.0

    def __post_init__(self):
        if torch is None:
            raise RuntimeError("Instale torch para usar AgenteDRL (pip install torch).")
        self.model = _MLP(4, 1).eval()  # estado mínimo: [p_t, ret_1, ret_5, pos_norm]

    def _estado(self, ambiente) -> np.ndarray:
        p = ambiente.preco
        h = ambiente.h_preco
        r1 = 0.0 if len(h) < 2 else math.log(h[-1] / h[-2])
        r5 = 0.0 if len(h) < 6 else math.log(h[-1] / h[-6])
        pos_norm = self.pos / max(1.0, (self.caixa / max(1e-9, p)))
        return np.array([p, r1, r5, pos_norm], dtype=np.float32)

    def agir(self, ambiente) -> None:
        s = self._estado(ambiente)
        with torch.no_grad():
            a = float(self.model(torch.from_numpy(s)).squeeze().cpu().numpy())
        a = max(-1.0, min(1.0, a))  # [-1,1]
        qtd = a * self.tamanho_max

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

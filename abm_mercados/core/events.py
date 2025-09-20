from dataclasses import dataclass


@dataclass
class Choque:
    t: int
    magnitude: float
    tipo: str = "sentimento"  # ou "noticia", "policy", etc.

from __future__ import annotations
import os, json
import pandas as pd
from datetime import datetime
from ..core.metrics import painel_estilizados


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def save_run(
    tag: str,
    outdir: str,
    precos: list[float],
    desequil: list[float],
    extras: dict | None = None,
):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    pasta = ensure_dir(os.path.join(outdir, f"{tag}_{ts}"))
    pd.Series(precos).to_csv(
        os.path.join(pasta, "precos.csv"), index=False, header=False
    )
    pd.Series(desequil).to_csv(
        os.path.join(pasta, "desequilibrio.csv"), index=False, header=False
    )
    met = painel_estilizados(precos)
    if extras:
        met.update(extras)
    with open(os.path.join(pasta, "metricas.json"), "w", encoding="utf-8") as f:
        json.dump(met, f, ensure_ascii=False, indent=2)
    return met, pasta

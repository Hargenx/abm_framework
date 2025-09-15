# -*- coding: utf-8 -*-
"""
Utilitários comuns de validação: métricas, diretórios e gráficos.
Funciona com séries de preço (list/np.array/pd.Series) e demanda_liquida (opcional).
"""

# -*- coding: utf-8 -*-
import os, json, csv
from datetime import datetime


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def save_series_csv(filepath: str, series, header="valor"):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["idx", header])
        for i, v in enumerate(series):
            w.writerow([i, v])


def save_json(filepath: str, data: dict):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def plot_series(filepath: str, series, title="", ylabel=""):
    try:
        import matplotlib.pyplot as plt

        fig = plt.figure()
        plt.plot(series)
        plt.title(title)
        plt.xlabel("ciclo")
        plt.ylabel(ylabel)
        plt.tight_layout()
        fig.savefig(filepath, dpi=150)
        plt.close(fig)
    except Exception as e:
        # Sem matplotlib? Apenas ignore o gráfico.
        pass


def compute_basic_metrics(prices):
    if not prices or len(prices) < 2:
        return {"n": len(prices)}
    import math

    rets = [(prices[i] / prices[i - 1] - 1.0) for i in range(1, len(prices))]
    m = sum(rets) / len(rets)
    var = sum((r - m) ** 2 for r in rets) / max(1, (len(rets) - 1))
    vol = math.sqrt(var)
    return {
        "n": len(prices),
        "ret_medio": m,
        "vol_diaria": vol,
        "ret_acumulado": prices[-1] / prices[0] - 1.0,
    }


def save_all_outputs(
    tag: str, outdir: str, precos, demanda_liquida=None, extras: dict = None
):
    outdir = ensure_dir(os.path.join(outdir, f"{tag}_{_timestamp()}"))
    # CSV
    save_series_csv(os.path.join(outdir, "precos.csv"), precos, header="preco")
    if demanda_liquida is not None:
        save_series_csv(
            os.path.join(outdir, "demanda_liquida.csv"), demanda_liquida, header="qtd"
        )
    # PNG
    plot_series(
        os.path.join(outdir, "precos.png"),
        precos,
        title=f"Preços - {tag}",
        ylabel="preço",
    )
    if demanda_liquida is not None:
        plot_series(
            os.path.join(outdir, "demanda_liquida.png"),
            demanda_liquida,
            title=f"Demanda líquida - {tag}",
            ylabel="qtd",
        )
    # Métricas
    met = compute_basic_metrics(precos)
    if extras:
        met.update(extras)
    save_json(os.path.join(outdir, "metricas.json"), met)
    return met, outdir

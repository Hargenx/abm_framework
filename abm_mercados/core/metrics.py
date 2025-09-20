import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf


def retornos_log(precos: list[float]) -> np.ndarray:
    p = np.asarray(precos, dtype=float)
    return np.diff(np.log(p))


def painel_estilizados(precos: list[float]) -> dict:
    r = retornos_log(precos)
    if r.size == 0:
        return {}
    acf_r = acf(r, fft=True, nlags=min(50, len(r) - 1), missing="drop")
    acf_abs = acf(np.abs(r), fft=True, nlags=min(50, len(r) - 1), missing="drop")
    return {
        "n": int(len(precos)),
        "ret_medio": float(np.mean(r)),
        "vol_diaria": float(np.std(r, ddof=1)),
        "curtose": float(pd.Series(r).kurtosis(fisher=False)),
        "assimetria": float(pd.Series(r).skew()),
        "acf_r_1": float(acf_r[1]) if len(acf_r) > 1 else np.nan,
        "acf_abs_1": float(acf_abs[1]) if len(acf_abs) > 1 else np.nan,
    }

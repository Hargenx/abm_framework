import argparse
import yaml
import importlib
from .plugins import listar_plugins
from .core.simulation import Simulacao


def _cls_from_str(path: str):
    # suporte "pacote.modulo:Classe"
    mod, cls = path.split(":")
    return getattr(importlib.import_module(mod), cls)


def run_config(cfg_path: str):
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # 1) ambiente
    env_spec = cfg["environment"]
    env_cls = env_spec["cls"]
    if isinstance(env_cls, str):
        if ":" in env_cls:  # caminho explícito
            Env = _cls_from_str(env_cls)
        else:  # plugin name
            Env = listar_plugins()[env_cls]
    else:
        raise ValueError("environment.cls deve ser string")

    env = Env(**(env_spec.get("params") or {}))

    # 2) investidores
    for spec in cfg.get("investors", []):
        cls_str = spec["cls"]
        if ":" in cls_str:
            Inv = _cls_from_str(cls_str)
        else:
            Inv = listar_plugins()[cls_str]
        env.adicionar_investidor(Inv(**(spec.get("params") or {})))

    # 3) simulação
    steps = int(cfg.get("steps", 252))
    sim = Simulacao(env)
    sim.executar(steps)

    # 4) saída (opcional)
    out = cfg.get("output")
    if out:
        from .utils.io import ensure_dir, save_run
        from .utils.plotting import plot_series

        met, pasta = save_run(
            out.get("tag", "RUN"),
            ensure_dir(out.get("dir", "./outputs/run")),
            env.h_preco,
            getattr(env, "h_deseq", []),
            extras=out.get("extras"),
        )
        print("Saída:", pasta)
        print("Métricas:", met)
        if out.get("plot", True):
            plot_series(
                env.h_preco, getattr(env, "h_deseq", []), titulo=out.get("tag", "RUN")
            )


def main():
    ap = argparse.ArgumentParser(prog="abm-mercado")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Executa a simulação a partir de um arquivo YAML")
    r.add_argument("config", help="Caminho para config.yaml")

    args = ap.parse_args()
    if args.cmd == "run":
        run_config(args.config)

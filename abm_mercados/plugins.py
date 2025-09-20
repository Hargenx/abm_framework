from importlib.metadata import entry_points


def listar_plugins(group: str = "abm_mercado.plugins"):
    eps = entry_points().select(group=group)
    return {ep.name: ep.load() for ep in eps}

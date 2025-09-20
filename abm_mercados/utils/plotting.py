import matplotlib.pyplot as plt


def plot_series(precos, desequil, titulo="Mercado"):
    plt.figure(figsize=(10, 5))
    plt.plot(precos)
    plt.title(f"Preços - {titulo}")
    plt.xlabel("ciclo")
    plt.ylabel("preço")
    plt.figure(figsize=(10, 5))
    plt.plot(desequil)
    plt.title(f"Desequilíbrio - {titulo}")
    plt.xlabel("ciclo")
    plt.ylabel("qtd")
    plt.show()

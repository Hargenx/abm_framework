import random, numpy as np


def set_seed(seed: int = 7):
    random.seed(seed)
    np.random.seed(seed)

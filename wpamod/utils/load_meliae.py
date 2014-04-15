from functools32 import lru_cache
from meliae import loader


@lru_cache(maxsize=20)
def load_meliae(filename):
    om = loader.load(filename)
    om.remove_expensive_references()
    return om
from pathlib import Path
from swiplserver import prolog_args

PL_UTILS_DIR = Path(__file__).parent / "pl-utils"
PREPROCESS_QUERY = "preprocess({app_name}, Compatibles)"
DEPLOYED_QUERY = "deployed({app}, {placement})"


def parse_compatibles(r):
    compatibles = {}
    for t in r:
        name, comps = prolog_args(t)
        compatibles[name] = {}
        for c in comps:
            n, cost = prolog_args(c)
            compatibles[name][n] = round(float(cost), 4)
    return compatibles

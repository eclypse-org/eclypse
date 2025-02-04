from ray import tune
from ray.tune.search.variant_generator import generate_variants

search_space = {
    "timeout": 3600,
    "max_ticks": 30,
    "application_id": tune.grid_search(
        [
            "speakToMe",
            "arFarming",
            "distSecurity",
        ]
    ),
    "kill_prob": 0.02,
    # "kill_prob": tune.grid_search(
    #     [
    #         0.01,
    #         0.02,
    #         0.05,
    #     ]
    # ),
    "seed": tune.grid_search(
        [
            3997,
            151195,
            300425,
        ]
    ),
    "topology": tune.grid_search(
        [
            "ER",
            "BA",
            "IAG",
        ]
    ),
    "declarative": tune.grid_search([False, True]),
    "preprocess": tune.grid_search([False, True]),
    # "cr": tune.grid_search([False, True]),
    "cr": tune.sample_from(
        lambda spec: (
            tune.grid_search[False, True] if spec.config["preprocess"] else False
        )
    ),
    "nodes": tune.grid_search([2**i for i in range(4, 11)]),
}

variants = list(generate_variants(search_space))
print(len(variants))
print(list(variants))

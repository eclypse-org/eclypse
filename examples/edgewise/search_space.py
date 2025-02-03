from ray import tune

search_space = {
    "timeout": 2700,
    "max_ticks": 30,
    "application_id": tune.grid_search(
        [
            "speakToMe",
            "arFarming",
            "distSecurity",
        ]
    ),
    "kill_prob": tune.grid_search(
        [
            0.01,
            0.02,
            0.05,
        ]
    ),
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
    "preprocess": tune.grid_search([False, True]),
    "declarative": tune.grid_search([False, True]),
    "cr": tune.grid_search([False, True]),
    "nodes": tune.grid_search([2**i for i in range(4, 11)]),
}

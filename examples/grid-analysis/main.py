from pathlib import Path
from time import time

import ray
from applications import get_apps
from eclypse.placement.strategies import (
    BestFitStrategy,
    FirstFitStrategy,
    RandomStrategy,
)
from eclypse.simulation import Simulation
from eclypse.simulation.config import SimulationConfig
from eclypse.utils import DEFAULT_SIM_PATH
from infrastructure import get_infrastructure
from metrics import get_metrics
from ray import train, tune
from strategy import EnergyMinimizationStrategy


def eclypse_grid(config):
    print("Running with config: ", config)
    stg = train.get_context().get_storage()
    path = (
        Path(stg.storage_fs_path)
        / stg.experiment_dir_name
        / str(stg.trial_dir_name)
        / "output"
    )
    print("PATH: ", path)

    sim_config = SimulationConfig(
        seed=config["seed"],
        max_ticks=config["max_ticks"],
        path=path,
        include_default_callbacks=False,
        callbacks=get_metrics(),
        log_level="CRITICAL",
    )

    apps = get_apps(seed=config["seed"])
    infr = get_infrastructure(config, apps)
    sim = Simulation(infrastructure=infr, simulation_config=sim_config)

    for app in apps:
        sim.register(app, get_strategy(config))
    sim.start()
    sim.wait()

    print("End of simulation")


def get_strategy(config):
    if config["strategy"] == "random":
        return RandomStrategy(config["seed"])
    elif config["strategy"] == "best-fit":
        return BestFitStrategy()
    elif config["strategy"] == "first-fit":
        return FirstFitStrategy()
    elif config["strategy"] == "min-energy":
        return EnergyMinimizationStrategy()

    raise ValueError(f"Invalid strategy '{config['strategy']}'")


# Define the search space
search_space = {
    "max_ticks": 600,
    "load": tune.grid_search(
        [
            0,
            0.25,
            0.5,
            0.75,
        ]
    ),
    "nodes": tune.grid_search(
        [
            50,
            100,
            300,
        ]
    ),
    "seed": tune.grid_search(
        [
            42,
            3997,
            151195,
        ]
    ),
    "policy": tune.grid_search(
        [
            ("degrade", 0.4),
            ("degrade", 0.5),
            ("degrade", 0.6),
            ("kill", 0.01),
            ("kill", 0.05),
            ("kill", 0.1),
            ("ensure",),
        ]
    ),
    "strategy": tune.grid_search(
        [
            # "random",
            # "first-fit",
            # "best-fit",
            "min-energy",
        ]
    ),
    "topology": tune.grid_search(
        [
            ("hierarchical",),
            ("star",),
            # ("random", 0.25),
            ("random", 0.5),
            # ("random", 0.75),
        ]
    ),
}

if __name__ == "__main__":
    config_example = {
        "max_ticks": 10,
        "load": 0,
        "nodes": 50,
        "seed": 42,
        "policy": ("kill", 0.1),
        "strategy": "min-energy",
        "topology": ("hierarchical",),
    }

    ray.init(address="auto")

    start_time = time()
    run_config = train.RunConfig(storage_path=(DEFAULT_SIM_PATH).resolve())
    tuner = tune.Tuner(
        # tune.with_resources(eclypse_grid, {"cpu": 0.5}),
        eclypse_grid,
        param_space=search_space,
        run_config=run_config,
    )
    tuner.fit()
    print("Elapsed time: ", time() - start_time)

from pathlib import Path
from time import time

import ray
from ray import (
    train,
    tune,
)
from swiplserver import PrologMQI

from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)
from eclypse.utils import DEFAULT_SIM_PATH
from examples.edgewise.applications import get_application
from examples.edgewise.assets import (
    get_edge_assets,
    get_node_assets,
    get_path_aggregators,
)
from examples.edgewise.infrastructures import get_infrastructure
from examples.edgewise.metrics import get_metrics
from examples.edgewise.policy import kill_policy
from examples.edgewise.search_space import search_space
from examples.edgewise.strategy import get_strategy


def edgewise_grid(config):
    stg = train.get_context().get_storage()
    path = (
        Path(stg.storage_fs_path)
        / stg.experiment_dir_name
        / str(stg.trial_dir_name)
        / "output"
    )

    sim_config = SimulationConfig(
        seed=config["seed"],
        max_ticks=config["max_ticks"],
        include_default_callbacks=False,
        callbacks=get_metrics(),
        path=path,
        # path=DEFAULT_SIM_PATH / "edgewise",
        # log_level="CRITICAL",
    )

    app = get_application(
        application_id=config["application_id"],
        node_assets=get_node_assets(),
        edge_assets=get_edge_assets(),
        seed=config["seed"],
    )

    node_update_policy = kill_policy(config["kill_prob"])

    infr = get_infrastructure(
        n=config["nodes"],
        seed=config["seed"],
        topology=config["topology"],
        node_assets=get_node_assets(config["preprocess"], is_app=False),
        edge_assets=get_edge_assets(),
        path_assets_aggregators=get_path_aggregators(),
        node_update_policy=node_update_policy,
    )

    mqi = PrologMQI()
    prolog = mqi.create_thread()
    sim = Simulation(infrastructure=infr, simulation_config=sim_config)

    sim.register(app, get_strategy(prolog=prolog, **config))

    sim.start()
    sim.wait()

    prolog.stop()
    mqi.stop()


if __name__ == "__main__":
    config_example = {
        "timeout": 5,
        "application_id": "distSecurity",
        "max_ticks": 3,
        "kill_prob": 0.02,
        "preprocess": True,
        "declarative": False,
        "cr": True,
        "topology": "ER",
        "nodes": 128,
        "seed": 3997,
    }

    # edgewise_grid(config_example)

    ray.init(address="auto")

    start_time = time()
    run_config = train.RunConfig(storage_path=(DEFAULT_SIM_PATH).resolve())
    tuner = tune.Tuner(
        # tune.with_resources(eclypse_grid, {"cpu": 0.5}),
        edgewise_grid,
        param_space=search_space,
        run_config=run_config,
    )
    tuner.fit()
    print("Elapsed time: ", time() - start_time)

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
from examples.edgewise.policy import kill_policy
from examples.edgewise.strategies import EdgeWiseStrategy


def edgewise_grid(config):
    # stg = train.get_context().get_storage()
    # path = (
    #     Path(stg.storage_fs_path)
    #     / stg.experiment_dir_name
    #     / str(stg.trial_dir_name)
    #     / "output"
    # )

    sim_config = SimulationConfig(
        seed=config["seed"],
        max_ticks=config["max_ticks"],
        # path=path,
        path=DEFAULT_SIM_PATH / "edgewise",
        include_default_callbacks=False,
    )

    app = get_application(
        application_id=config["application_id"],
        node_assets=get_node_assets(),
        edge_assets=get_edge_assets(),
        seed=config["seed"],
    )

    node_update_policy, edge_update_policy = kill_policy(config["kill_prob"])

    infr = get_infrastructure(
        n=config["nodes"],
        seed=config["seed"],
        topology=config["topology"],
        node_assets=get_node_assets(is_app=False),
        edge_assets=get_edge_assets(),
        path_assets_aggregators=get_path_aggregators(),
        node_update_policy=node_update_policy,
        edge_update_policy=edge_update_policy,
    )

    mqi = PrologMQI()
    prolog = mqi.create_thread()
    sim = Simulation(infrastructure=infr, simulation_config=sim_config)

    sim.register(app, EdgeWiseStrategy(prolog=prolog, preprocess=True, cr=True))

    sim.start()
    sim.wait()

    prolog.stop()
    mqi.stop()


# app = get_application(
#     application_id="arFarming",
#     node_assets=get_node_assets(),
#     edge_assets=get_edge_assets(),
#     seed=42,
# )

# print(app.graph["things"].keys(), app.nodes())

if __name__ == "__main__":
    config_example = {
        "application_id": "speakToMe",
        "max_ticks": 4,
        "kill_prob": 0.05,
        # "policy": ("ensure",),
        "topology": "BA",
        "nodes": 128,
        "seed": 42,
    }

    edgewise_grid(config_example)

    # ray.init(address="auto")

    # start_time = time()
    # run_config = train.RunConfig(storage_path=(DEFAULT_SIM_PATH).resolve())
    # tuner = tune.Tuner(
    #     # tune.with_resources(eclypse_grid, {"cpu": 0.5}),
    #     edgewise_grid,
    #     param_space=search_space,
    #     run_config=run_config,
    # )
    # tuner.fit()
    # print("Elapsed time: ", time() - start_time)

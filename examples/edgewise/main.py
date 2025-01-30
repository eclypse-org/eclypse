from pathlib import Path

# from ray import (
#     train,
#     tune,
# )

from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)
from examples.edgewise.applications import get_application
from examples.edgewise.assets import (
    get_edge_assets,
    get_node_assets,
)

# from examples.edgewise.infrastructures import get_infrastructure
# from examples.edgewise.strategy import EdgeWiseStrategy


# def edgewise_grid(config):
#     stg = train.get_context().get_storage()
#     path = (
#         Path(stg.storage_fs_path)
#         / stg.experiment_dir_name
#         / str(stg.trial_dir_name)
#         / "output"
#     )
#     sim_config = SimulationConfig(
#         seed=config["seed"],
#         max_ticks=config["max_ticks"],
#         path=path,
#         include_default_callbacks=False,
#         log_level="ERROR",
#     )

#     app = get_application(
#         application_id=config["application_id"],
#         node_update_policy=config["node_update_policy"],
#         edge_update_policy=config["edge_update_policy"],
#         node_assets=get_node_assets(),
#         edge_assets=get_edge_assets(),
#         seed=config["seed"],
#     )

#     infr = get_infrastructure(
#         n=config["nodes"],
#         seed=config["seed"],
#         topology=config["topology"],
#         node_update_policy=config["node_update_policy"],
#         edge_update_policy=config["edge_update_policy"],
#     )

#     sim = Simulation(infrastructure=infr, simulation_config=sim_config)
#     sim.register(app, EdgeWiseStrategy())

#     sim.start()
#     sim.wait()

#     raise ValueError(f"Invalid strategy '{config['strategy']}'")

app = get_application(
    application_id="arFarming",
    node_assets=get_node_assets(),
    edge_assets=get_edge_assets(),
    seed=42,
)

print(app.graph["things"].keys(), app.nodes())

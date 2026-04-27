from .application import image_app as app
from .metrics import get_metrics
from .services.utils import (
    BASE_PATH,
    STEP_EVERY_MS,
    STEPS,
)
from .update_policy import DegradePolicy

from eclypse.builders.infrastructure import get_star
from eclypse.placement.strategies import RandomStrategy
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)


def main() -> None:
    """Run the Image Prediction example."""
    seed = 2

    sim_config = SimulationConfig(
        seed=seed,
        max_steps=STEPS,
        step_every_ms=STEP_EVERY_MS,
        include_default_metrics=False,
        events=get_metrics(),
        log_to_file=True,
        path=BASE_PATH,
        # Pass a RemoteBootstrap instance here to request specific Ray resources.
        remote=True,
    )

    sim = Simulation(
        get_star(
            infrastructure_id="IPInfr",
            n_clients=5,
            seed=seed,
            update_policies=DegradePolicy(epochs=STEPS),
            include_default_assets=True,
            resource_init="max",
            symmetric=True,
        ),
        simulation_config=sim_config,
    )
    strategy = RandomStrategy(spread=True)

    sim.register(app, strategy)
    sim.run()


if __name__ == "__main__":
    main()

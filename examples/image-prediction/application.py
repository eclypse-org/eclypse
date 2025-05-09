from services import (
    EndService,
    PredictorService,
    TrainerService,
)

from eclypse.graph import Application
from eclypse.utils import MAX_LATENCY

image_app = Application("ImagePrediction", include_default_assets=True)

image_app.add_service(
    EndService("EndService"),
    cpu=1,
    gpu=0,
    ram=0.5,
    storage=0.5,
    availability=0.9,
    processing_time=5,
)

image_app.add_service(
    PredictorService("PredictorService"),
    cpu=1,
    gpu=1,
    ram=16.0,
    storage=64.0,
    availability=0.9,
)

image_app.add_service(
    TrainerService("TrainerService"),
    cpu=16,
    gpu=4,
    ram=16.0,
    storage=2.0,
    availability=0.9,
)


image_app.add_edge(
    "EndService",
    "PredictorService",
    latency=MAX_LATENCY,
    bandwidth=20.0,
    symmetric=True,
)

image_app.add_edge(
    "PredictorService",
    "TrainerService",
    latency=MAX_LATENCY,
    bandwidth=100.0,
    symmetric=True,
)

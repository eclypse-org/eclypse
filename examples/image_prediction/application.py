from services import (
    EndService,
    PredictorService,
    TrainerService,
)

from eclypse.graph import (
    Application,
    NodeGroup,
)
from eclypse.utils import MAX_LATENCY

image_app = Application("ImagePrediction")

image_app.add_service(
    EndService("EndService"),
    cpu=1,
    gpu=0,
    ram=0.5,
    storage=0.5,
    availability=0.9,
    group=NodeGroup.IOT,
    processing_time=5,
)

image_app.add_service(
    PredictorService("PredictorService"),
    cpu=1,
    gpu=1,
    ram=16.0,
    storage=64.0,
    availability=0.9,
    group=NodeGroup.FAR_EDGE,
)

image_app.add_service(
    TrainerService("TrainerService"),
    cpu=16,
    gpu=4,
    ram=16.0,
    storage=2.0,
    availability=0.9,
    group=NodeGroup.CLOUD,
)


image_app.add_symmetric_edge(
    "EndService",
    "PredictorService",
    latency=MAX_LATENCY,
    bandwidth=20.0,
)

image_app.add_symmetric_edge(
    "PredictorService",
    "TrainerService",
    latency=MAX_LATENCY,
    bandwidth=100.0,
)

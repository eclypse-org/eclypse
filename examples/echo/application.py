from echo import EchoService

from eclypse.graph import Application, NodeGroup

# Creating an instance of the EchoApp class
echo_app = Application("EchoApp")

echo_app.add_service(
    EchoService("Gateway"),
    cpu=1,
    gpu=0,
    ram=0.5,
    storage=0.5,
    availability=0.9,
    group=NodeGroup.IOT,
    processing_time=0.1,
)

echo_app.add_service(
    EchoService("SecurityService"),
    cpu=2,
    gpu=0,
    ram=4.0,
    storage=2.0,
    availability=0.8,
    group=NodeGroup.NEAR_EDGE,
    processing_time=2.0,
)

echo_app.add_service(
    EchoService("LightingService"),
    cpu=1,
    gpu=0,
    ram=2.0,
    storage=5.0,
    availability=0.8,
    group=NodeGroup.IOT,
    processing_time=1.0,
)

echo_app.add_service(
    EchoService("ClimateControlService"),
    cpu=2,
    gpu=0,
    ram=3.0,
    storage=8.0,
    availability=0.85,
    group=NodeGroup.NEAR_EDGE,
    processing_time=1.5,
)


echo_app.add_service(
    EchoService("EntertainmentService"),
    cpu=3,
    gpu=1,
    ram=4.0,
    storage=10.0,
    availability=0.9,
    group=NodeGroup.CLOUD,
    processing_time=5.0,
)

echo_app.add_symmetric_edge(
    "Gateway",
    "LightingService",
    latency=100.0,
    bandwidth=20.0,
)

echo_app.add_symmetric_edge(
    "Gateway",
    "ClimateControlService",
    latency=100.0,
    bandwidth=10.0,
)

echo_app.add_symmetric_edge(
    "Gateway",
    "SecurityService",
    latency=50.0,
    bandwidth=5.0,
)

echo_app.add_symmetric_edge(
    "SecurityService",
    "EntertainmentService",
    latency=50.0,
    bandwidth=10.0,
)

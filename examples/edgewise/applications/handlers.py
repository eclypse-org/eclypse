from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
)

if TYPE_CHECKING:
    from eclypse.graph import Application


def service_handler(app: Application, **sattr: Dict[str, Any]) -> None:
    service_id = sattr.pop("ServiceId")
    app.graph["components"]["service"].update({service_id: sattr})


def function_handler(app: Application, **fattr: Dict[str, Any]) -> None:
    function_id = fattr.pop("FunctionId")
    app.graph["components"]["function"].update({function_id: fattr})


def thing_handler(app: Application, **tattr: Dict[str, Any]) -> None:
    thing_id = tattr.pop("ThingId")
    app.graph["components"]["thing"].update({thing_id: tattr})


def application_handler(app: Application, **aattr: Dict[str, Any]) -> None:
    app.name = aattr.pop("AppId")
    app.graph.update(aattr)


def service_instance_handler(app: Application, **sattr: Dict[str, Any]) -> None:
    instance_id = sattr.pop("InstanceId")
    service_id = sattr.pop("ServiceId")
    app.add_node(instance_id, **app.graph["components"]["service"][service_id])


def function_instance_handler(app: Application, **fattr: Dict[str, Any]) -> None:
    instance_id = fattr.pop("InstanceId")
    function_id = fattr.pop("FunctionId")
    app.add_node(
        instance_id,
        **app.graph["components"]["function"][function_id],
        **fattr,
    )


def thing_instance_handler(app: Application, **tattr: Dict[str, Any]) -> None:
    instance_id = tattr.pop("InstanceId")
    thing_id = tattr.pop("ThingId")
    app.graph["things"].append(
        {instance_id: app.graph["components"]["thing"][thing_id]}
    )
    pass


def data_flow_handler(app: Application, **dattr: Dict[str, Any]) -> None:
    source_id, target_id = dattr.pop("SourceId"), dattr.pop("TargetId")
    size, rate = dattr.pop("Size"), dattr.pop("Rate")
    dattr.update({"bandwidth": size * rate})
    app.add_edge(source_id, target_id, **dattr)


def get_handlers() -> Dict[str, Callable]:
    return {
        "service": service_handler,
        "function": function_handler,
        "thing": thing_handler,
        "application": application_handler,
        "serviceInstance": service_instance_handler,
        "functionInstance": function_instance_handler,
        "thingInstance": thing_instance_handler,
        "dataFlow": data_flow_handler,
    }

from __future__ import annotations
from eclypse.report import metric
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph import Application, Infrastructure
    from eclypse.placement import Placement


@metric.application
def bins(_: Application, placement: Placement, __: Infrastructure):
    return len(set(placement.mapping.values()))


@metric.application
def is_placed(app: Application, placement: Placement, _: Infrastructure):
    return len(placement.mapping) == len(app.nodes)


@metric.application
def moved_services(_: Application, placement: Placement, __: Infrastructure):
    return placement.strategy.moved_services


@metric.application
def cost(_: Application, placement: Placement, __: Infrastructure):
    return placement.strategy.cost


@metric.application
def execution_time(_: Application, placement: Placement, __: Infrastructure):
    return placement.strategy.exec_time


def get_metrics():
    return [bins, is_placed, moved_services, cost, execution_time]

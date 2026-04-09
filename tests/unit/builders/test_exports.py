from __future__ import annotations

from eclypse.builders import application as application_builders
from eclypse.builders import infrastructure as infrastructure_builders


def test_builder_exports_are_available():
    assert callable(application_builders.get_sock_shop)
    assert callable(infrastructure_builders.get_orion_cev)

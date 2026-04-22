"""Workflow builders using `WfCommons <https://wfcommons.org/>`_ library.

The package groups *simulation-only* workflow builders that generate task DAGs
and map their metadata onto ECLYPSE applications. These builders do not expose
service implementations for emulation; instead, they target workflow-oriented
simulation studies where task structure, runtime, and data movement matter.
When WfCommons file sizes are mapped onto ECLYPSE assets, workflow ``storage``
and dependency ``bandwidth`` are normalised from bytes to MiB.
"""

from .workflow import get_workflow

__all__ = ["get_workflow"]

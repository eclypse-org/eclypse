from .vas import get_vas
from .assembly_platform import get_assembly_platform
from .health_guardian import get_health_guardian


def get_apps(seed: int = None):
    return [
        get_vas(seed=seed),
        get_health_guardian(seed=seed),
        get_assembly_platform(seed=seed),
    ]

import pytest

pytest_plugins = [
    "tests.fixtures.backends",
    "tests.fixtures.domain",
    "tests.fixtures.reporting",
    "tests.fixtures.remote",
]


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    # Group before xdist adds its scheduling suffix to each node ID.
    index = 0
    for item in items:
        if item.get_closest_marker("emulation"):
            item.add_marker(pytest.mark.xdist_group(f"ray_{index % 2}"))
            index += 1

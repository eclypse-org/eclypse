from __future__ import annotations

import ast
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_EXAMPLE_SCRIPTS = {
    "echo": "examples.echo.main:main",
    "grid-analysis": "examples.grid_analysis.main:main",
    "image-prediction": "examples.image_prediction.main:main",
    "off-the-shelf": "examples.off_the_shelf.main:main",
    "sock-shop-mpi": "examples.sock_shop.mpi:main",
    "sock-shop-rest": "examples.sock_shop.rest:main",
    "user-distribution": "examples.user_distribution.main:main",
}


def test_example_scripts_target_main_functions():
    with (REPO_ROOT / "pyproject.toml").open("rb") as pyproject:
        config = tomllib.load(pyproject)

    scripts = config["project"]["scripts"]
    for script, target in EXPECTED_EXAMPLE_SCRIPTS.items():
        assert scripts[script] == target


def test_example_script_targets_define_main_functions():
    for target in EXPECTED_EXAMPLE_SCRIPTS.values():
        module_name, function_name = target.split(":")
        module_path = REPO_ROOT.joinpath(*module_name.split(".")).with_suffix(".py")

        tree = ast.parse(module_path.read_text(), filename=str(module_path))
        assert any(
            isinstance(node, ast.FunctionDef) and node.name == function_name
            for node in tree.body
        )

import pytest


@pytest.fixture()
def lesson_plan_yaml_file() -> str:
    return "tests/fixtures/lesson_plan.yaml"


@pytest.fixture()
def lesson_plan_tex_file() -> str:
    return "tests/fixtures/lesson_plan.tex"

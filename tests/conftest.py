"""Fixtures compartidas: cada base se lee una sola vez por sesión de tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "src") not in sys.path:  # respaldo de la opción pythonpath de pyproject
    sys.path.insert(0, str(RAIZ / "src"))

from homologacion import cargar  # noqa: E402


@pytest.fixture(scope="session")
def historico():
    return cargar("historico")


@pytest.fixture(scope="session")
def becas():
    return cargar("becas")


@pytest.fixture(scope="session")
def colaboracion():
    return cargar("instituciones")


@pytest.fixture(scope="session")
def postulaciones():
    return cargar("postulaciones")

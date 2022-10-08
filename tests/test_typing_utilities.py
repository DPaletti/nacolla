from __future__ import annotations
from typing import Any
import pytest
from nacolla.type_utilities import io_interface


def test_io_interface_multi_input():
    def f(i: int, j: float) -> float:
        return i + j

    with pytest.raises(TypeError):
        io_interface(f)  # type: ignore


def test_io_interface_missing_input_annotation():
    def f(i) -> Any:  # type: ignore
        return i  # type: ignore

    with pytest.raises(TypeError):
        io_interface(f)  # type: ignore


def test_io_interface_missing_output_annotation():
    def f(i: int):
        return i

    with pytest.raises(TypeError):
        io_interface(f)

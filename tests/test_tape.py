"""Tests for the BFFTape data structure."""

import numpy as np
import pytest

from bff import BFFTape


def test_tape_creation_defaults() -> None:
    tape = BFFTape()
    assert len(tape) == 64
    assert all(tape[i] == 0 for i in range(len(tape)))


def test_tape_creation_with_custom_data() -> None:
    data = np.arange(16, dtype=np.uint8)
    tape = BFFTape(length=16, data=data)
    assert len(tape) == 16
    assert [tape[i] for i in range(16)] == data.tolist()
    # Original data should not be modified by assignments
    tape[0] = 255
    assert data[0] == 0


def test_tape_invalid_length() -> None:
    with pytest.raises(ValueError):
        BFFTape(length=0)


def test_tape_data_length_mismatch() -> None:
    with pytest.raises(ValueError):
        BFFTape(length=8, data=np.arange(4, dtype=np.uint8))


def test_tape_invalid_data_dimension() -> None:
    bad = np.zeros((2, 2), dtype=np.uint8)
    with pytest.raises(ValueError):
        BFFTape(length=4, data=bad)


def test_tape_index_wrapping() -> None:
    tape = BFFTape(length=10)
    tape[0] = 42
    assert tape[0] == 42
    assert tape[10] == 42
    assert tape[-10] == 42
    tape[19] = 7
    assert tape[9] == 7


def test_tape_set_invalid_value_range() -> None:
    tape = BFFTape(length=4)
    with pytest.raises(ValueError):
        tape[0] = 256
    with pytest.raises(ValueError):
        tape[1] = -1


def test_tape_set_invalid_type() -> None:
    tape = BFFTape(length=4)
    with pytest.raises(TypeError):
        tape[0] = "not-an-int"  # type: ignore[assignment]


def test_tape_copy_independence() -> None:
    tape1 = BFFTape.random(length=16, seed=123)
    tape2 = tape1.copy()
    tape2[0] = (tape2[0] + 1) % 256
    assert tape1[0] != tape2[0]


def test_tape_random_seed_reproducibility() -> None:
    tape1 = BFFTape.random(length=32, seed=999)
    tape2 = BFFTape.random(length=32, seed=999)
    assert [tape1[i] for i in range(32)] == [tape2[i] for i in range(32)]


def test_tape_random_invalid_length() -> None:
    with pytest.raises(ValueError):
        BFFTape.random(length=0)


def test_tape_to_string_and_snapshot() -> None:
    tape = BFFTape(length=4)
    for idx, value in enumerate([0x0A, 0x1B, 0x2C, 0x3D]):
        tape[idx] = value
    assert tape.to_string() == "0a 1b 2c 3d"

    snap = tape.snapshot()
    assert list(snap) == [0x0A, 0x1B, 0x2C, 0x3D]
    tape[0] = 0
    assert list(snap) == [0x0A, 0x1B, 0x2C, 0x3D]


def test_tape_data_property_returns_copy() -> None:
    tape = BFFTape(length=4)
    view = tape.data
    view[0] = 123
    assert tape[0] == 0


def test_tape_repr_and_snapshot_repr() -> None:
    tape = BFFTape(length=2)
    representation = repr(tape)
    assert "BFFTape" in representation
    snapshot_repr = repr(tape.snapshot())
    assert "TapeSlice" in snapshot_repr

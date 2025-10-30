"""BFF tape data structure.

This module provides the shared code/data memory model used by the
Brainfuck-Fusion (BFF) interpreter. The tape is implemented on top of a NumPy
array for performance and memory efficiency. Indexing operations wrap around
the tape boundaries to mimic the circular memory model described in the
paper.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np


@dataclass(frozen=True)
class TapeSlice:
    """Represents a snapshot slice of the tape for debugging and tests."""

    data: np.ndarray

    def __iter__(self):
        return iter(int(value) for value in self.data)

    def __repr__(self) -> str:
        return f"TapeSlice({self.data.tolist()})"


class BFFTape:
    """Represents a BFF program/data tape with circular indexing semantics."""

    def __init__(self, length: int = 64, data: Optional[Iterable[int]] = None):
        if length <= 0:
            raise ValueError("length must be positive")

        if data is None:
            self._data = np.zeros(length, dtype=np.uint8)
        else:
            array = np.array(list(data), dtype=np.uint8)
            if array.ndim != 1:
                raise ValueError("data must be one-dimensional")
            if len(array) != length:
                raise ValueError("length mismatch between length and data")
            self._data = array.copy()

        self._length = length

    def __len__(self) -> int:
        return self._length

    def __getitem__(self, index: int) -> int:
        idx = index % self._length
        return int(self._data[idx])

    def __setitem__(self, index: int, value: int) -> None:
        if not isinstance(value, (int, np.integer)):
            raise TypeError("value must be an integer")
        if value < 0 or value > 255:
            raise ValueError("value must be in range 0..255")
        idx = index % self._length
        self._data[idx] = np.uint8(value)

    def __repr__(self) -> str:
        return f"BFFTape(length={self._length}, data={self.to_string()})"

    def copy(self) -> "BFFTape":
        return BFFTape(length=self._length, data=self._data.copy())

    def to_string(self) -> str:
        return " ".join(f"{byte:02x}" for byte in self._data)

    def snapshot(self) -> TapeSlice:
        """Capture current tape contents for debugging purposes."""

        return TapeSlice(data=self._data.copy())

    @property
    def data(self) -> np.ndarray:
        return self._data.copy()

    @classmethod
    def random(cls, length: int = 64, seed: Optional[int] = None) -> "BFFTape":
        if length <= 0:
            raise ValueError("length must be positive")
        rng = np.random.default_rng(seed)
        data = rng.integers(0, 256, size=length, dtype=np.uint8)
        return cls(length=length, data=data)

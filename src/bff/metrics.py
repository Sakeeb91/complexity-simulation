"""Complexity and entropy metrics for the simulation."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Sequence, Union

import numpy as np

if TYPE_CHECKING:  # pragma: no cover - avoid runtime import cycle
    from .tape import BFFTape

ArrayLike = Union[np.ndarray, bytes, Sequence[int], "BFFTape"]


class ComplexityMetrics:
    """Collection of static helpers for entropy and complexity analysis."""

    @staticmethod
    def shannon_entropy(data: ArrayLike) -> float:
        """Compute Shannon entropy (base-2) for the supplied sequence."""

        array = ComplexityMetrics._ensure_numpy(data)
        if array.size == 0:
            return 0.0

        counts = Counter(int(value) for value in array)
        total = float(array.size)

        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * np.log2(p)

        return float(entropy)

    @staticmethod
    def _ensure_numpy(data: ArrayLike) -> np.ndarray:
        if isinstance(data, np.ndarray):
            return data.astype(np.uint8, copy=False).ravel()
        if isinstance(data, (bytes, bytearray, memoryview)):
            return np.frombuffer(bytes(data), dtype=np.uint8)
        attr = getattr(data, "data", None)
        if attr is not None:
            if callable(attr):
                attr = attr()
            return ComplexityMetrics._ensure_numpy(attr)
        if isinstance(data, Sequence):
            return np.array([int(value) & 0xFF for value in data], dtype=np.uint8)
        raise TypeError("Unsupported data type for entropy calculation")

    @staticmethod
    def _ensure_bytes(data: ArrayLike) -> bytes:
        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)
        if isinstance(data, np.ndarray):
            return data.astype(np.uint8, copy=False).tobytes()
        attr = getattr(data, "data", None)
        if attr is not None:
            if callable(attr):
                attr = attr()
            return ComplexityMetrics._ensure_bytes(attr)
        if isinstance(data, Sequence):
            return bytes(int(value) & 0xFF for value in data)
        raise TypeError("Unsupported data type for byte conversion")


def compute_entropy(sequence: bytes) -> float:
    """Placeholder for high-order entropy metric from Issue #4."""

    raise NotImplementedError("Metric implementation tracked in Issue #4")

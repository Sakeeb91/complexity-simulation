"""Complexity and entropy metrics for the simulation."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union

import brotli
import numpy as np

if TYPE_CHECKING:  # pragma: no cover - avoid runtime import cycle
    from .soup import PrimordialSoup
    from .tape import BFFTape

ArrayLike = Union[np.ndarray, bytes, Sequence[int], "BFFTape", Any]


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
    def kolmogorov_complexity_approx(
        data: ArrayLike, *, compression_quality: int = 2
    ) -> int:
        """Approximate Kolmogorov complexity using Brotli compression."""

        payload = ComplexityMetrics._ensure_bytes(data)
        if not payload:
            return 0

        compressed = brotli.compress(payload, quality=compression_quality)
        return len(compressed)

    @staticmethod
    def high_order_entropy(
        data: ArrayLike, *, compression_quality: int = 2
    ) -> float:
        """Compute high-order entropy for the given data sequence."""

        array = ComplexityMetrics._ensure_numpy(data)
        n = array.size
        if n == 0:
            return 0.0

        h_shannon = ComplexityMetrics.shannon_entropy(array)
        k_approx = ComplexityMetrics.kolmogorov_complexity_approx(
            array, compression_quality=compression_quality
        )

        normalized = (k_approx * 8.0) / n
        return max(0.0, h_shannon - normalized)

    @staticmethod
    def soup_complexity(
        soup: "PrimordialSoup",
        *,
        sample_size: Optional[int] = None,
        rng: Optional[np.random.Generator] = None,
    ) -> Dict[str, Any]:
        """Aggregate complexity metrics across a soup of programs."""

        programs = ComplexityMetrics._extract_programs(soup)
        total_programs = len(programs)

        if total_programs == 0:
            data = np.empty(0, dtype=np.uint8)
        else:
            if sample_size is not None and sample_size < total_programs:
                generator = rng or np.random.default_rng()
                indices = generator.choice(total_programs, size=sample_size, replace=False)
                selected = [programs[int(idx)] for idx in np.atleast_1d(indices)]
            else:
                selected = programs

            arrays = [ComplexityMetrics._ensure_numpy(prog) for prog in selected]
            data = np.concatenate(arrays) if arrays else np.empty(0, dtype=np.uint8)

        shannon = ComplexityMetrics.shannon_entropy(data)
        kolmogorov = ComplexityMetrics.kolmogorov_complexity_approx(data)
        high_order = ComplexityMetrics.high_order_entropy(data)

        unique_programs = {
            ComplexityMetrics._ensure_bytes(program)
            for program in programs
        }

        return {
            "shannon_entropy": shannon,
            "kolmogorov_approx": kolmogorov,
            "high_order_entropy": high_order,
            "unique_programs": len(unique_programs),
            "soup_size": getattr(soup, "soup_size", total_programs),
            "epoch": getattr(soup, "epoch", 0),
        }

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
            if isinstance(attr, np.ndarray):
                return attr.astype(np.uint8, copy=False).ravel()
            return ComplexityMetrics._ensure_numpy(attr)
        if isinstance(data, Sequence):
            return np.array([int(value) & 0xFF for value in data], dtype=np.uint8)
        raise TypeError("Unsupported data type for entropy calculation")

    @staticmethod
    def _ensure_bytes(data: ArrayLike) -> bytes:
        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)
        attr = getattr(data, "data", None)
        if attr is not None:
            if callable(attr):
                attr = attr()
            return ComplexityMetrics._ensure_bytes(attr)
        if isinstance(data, np.ndarray):
            return data.astype(np.uint8, copy=False).tobytes()
        if isinstance(data, Sequence):
            return bytes(int(value) & 0xFF for value in data)
        raise TypeError("Unsupported data type for byte conversion")

    @staticmethod
    def _extract_programs(soup: Any) -> List[ArrayLike]:
        programs: List[ArrayLike] = []

        direct = getattr(soup, "programs", None)
        if direct is not None:
            programs.extend(direct)

        if not programs:
            organisms = getattr(soup, "_organisms", [])
            for organism in organisms:
                genome = getattr(organism, "genome", None)
                if genome is not None:
                    programs.append(genome)

        return programs


def compute_entropy(sequence: ArrayLike) -> float:
    """Backwards-compatible wrapper for ``ComplexityMetrics.high_order_entropy``."""

    return ComplexityMetrics.high_order_entropy(sequence)

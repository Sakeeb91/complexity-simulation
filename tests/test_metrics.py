"""Tests for the complexity metrics module."""

from __future__ import annotations

import numpy as np

from src.bff.metrics import ComplexityMetrics
from src.bff.soup import PrimordialSoup
from src.bff.tape import BFFTape


def test_shannon_entropy_uniform() -> None:
    """Uniform random data should yield entropy close to 8 bits."""

    rng = np.random.default_rng(1234)
    data = rng.integers(0, 256, size=10_000, dtype=np.uint8)

    entropy = ComplexityMetrics.shannon_entropy(data)
    assert 7.9 < entropy < 8.1


def test_shannon_entropy_constant() -> None:
    """Constant data should have zero entropy."""

    data = np.zeros(1_000, dtype=np.uint8)
    entropy = ComplexityMetrics.shannon_entropy(data)
    assert entropy == 0.0


def test_high_order_entropy_random_noise() -> None:
    """High-order entropy should be ~0 for random noise."""

    rng = np.random.default_rng(4321)
    data = rng.integers(0, 256, size=10_000, dtype=np.uint8)

    hoe = ComplexityMetrics.high_order_entropy(data)
    assert 0.0 <= hoe < 1.0


def test_high_order_entropy_repeated_pattern() -> None:
    """Structured sequences should yield positive high-order entropy."""

    pattern = (b"ABCD" * 1024)
    hoe = ComplexityMetrics.high_order_entropy(pattern)

    assert hoe > 1.0


def test_kolmogorov_complexity_distinguishes_structure() -> None:
    """Structured data should compress better than random noise."""

    structured = b"ABCD" * 2048
    rng = np.random.default_rng(99)
    noise = rng.integers(0, 256, size=len(structured), dtype=np.uint8)

    k_structured = ComplexityMetrics.kolmogorov_complexity_approx(structured)
    k_noise = ComplexityMetrics.kolmogorov_complexity_approx(noise)

    assert k_structured < k_noise


def test_metrics_accept_bff_tape() -> None:
    """BFFTape instances should be accepted by the metrics helpers."""

    tape = BFFTape.random(length=128, seed=7)

    entropy = ComplexityMetrics.shannon_entropy(tape)
    assert entropy >= 0.0


def test_soup_complexity_aggregates_metrics() -> None:
    """Complexity metrics should aggregate data from the soup."""

    soup = PrimordialSoup(soup_size=10, tape_length=16, seed=42)

    metrics = ComplexityMetrics.soup_complexity(soup, sample_size=5)

    assert metrics["soup_size"] == 10
    assert metrics["epoch"] == 0
    assert metrics["unique_programs"] >= 1  # At least one unique program
    assert metrics["shannon_entropy"] >= 0.0
    assert metrics["high_order_entropy"] >= 0.0

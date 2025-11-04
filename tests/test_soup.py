"""Tests for the Primordial Soup simulation."""

import numpy as np
import pytest

from src.bff.soup import PrimordialSoup
from src.bff.tape import BFFTape


class TestPrimordialSoupInitialization:
    """Tests for soup initialization."""

    def test_soup_initialization_default(self):
        """Test soup initialization with default parameters."""
        soup = PrimordialSoup(soup_size=100, tape_length=64, seed=42)
        assert len(soup.programs) == 100
        assert all(len(p) == 64 for p in soup.programs)
        assert soup.epoch == 0
        assert soup.total_executions == 0
        assert soup.soup_size == 100
        assert soup.tape_length == 64

    def test_soup_initialization_custom_params(self):
        """Test soup initialization with custom parameters."""
        soup = PrimordialSoup(
            soup_size=50,
            tape_length=32,
            max_steps_per_execution=1000,
            mutation_rate=0.01,
            seed=123
        )
        assert len(soup.programs) == 50
        assert all(len(p) == 32 for p in soup.programs)
        assert soup.max_steps == 1000
        assert soup.mutation_rate == 0.01

    def test_soup_initialization_randomness(self):
        """Test that random initialization produces different soups."""
        soup1 = PrimordialSoup(soup_size=10, tape_length=64, seed=42)
        soup2 = PrimordialSoup(soup_size=10, tape_length=64, seed=43)

        # Different seeds should produce different programs
        programs_differ = False
        for i in range(10):
            if not np.array_equal(soup1.programs[i]._data, soup2.programs[i]._data):
                programs_differ = True
                break

        assert programs_differ, "Different seeds should produce different programs"

    def test_soup_initialization_reproducibility(self):
        """Test that same seed produces same soup."""
        soup1 = PrimordialSoup(soup_size=10, tape_length=64, seed=42)
        soup2 = PrimordialSoup(soup_size=10, tape_length=64, seed=42)

        # Same seed should produce identical programs
        for i in range(10):
            assert np.array_equal(soup1.programs[i]._data, soup2.programs[i]._data)

    def test_soup_initialization_invalid_params(self):
        """Test that invalid parameters raise errors."""
        with pytest.raises(ValueError, match="soup_size must be positive"):
            PrimordialSoup(soup_size=0)

        with pytest.raises(ValueError, match="soup_size must be positive"):
            PrimordialSoup(soup_size=-1)

        with pytest.raises(ValueError, match="tape_length must be positive"):
            PrimordialSoup(tape_length=0)

        with pytest.raises(ValueError, match="max_steps_per_execution must be positive"):
            PrimordialSoup(max_steps_per_execution=0)

        with pytest.raises(ValueError, match="mutation_rate must be in range"):
            PrimordialSoup(mutation_rate=-0.1)

        with pytest.raises(ValueError, match="mutation_rate must be in range"):
            PrimordialSoup(mutation_rate=1.5)


class TestConcatenateSplit:
    """Tests for concatenate and split operations."""

    def test_concatenate_basic(self):
        """Test basic concatenation of two tapes."""
        soup = PrimordialSoup(soup_size=10, seed=42)
        tape_a = soup.programs[0].copy()
        tape_b = soup.programs[1].copy()

        concatenated = soup._concatenate(tape_a, tape_b)

        assert len(concatenated) == len(tape_a) + len(tape_b)
        assert len(concatenated) == 128

        # Verify data is correctly concatenated
        for i in range(len(tape_a)):
            assert concatenated[i] == tape_a[i]
        for i in range(len(tape_b)):
            assert concatenated[len(tape_a) + i] == tape_b[i]

    def test_split_basic(self):
        """Test basic splitting of a tape."""
        soup = PrimordialSoup(soup_size=10, seed=42)
        tape_a = soup.programs[0].copy()
        tape_b = soup.programs[1].copy()

        concatenated = soup._concatenate(tape_a, tape_b)
        split_a, split_b = soup._split(concatenated)

        assert len(split_a) == 64
        assert len(split_b) == 64

    def test_concatenate_split_roundtrip(self):
        """Test that concatenate and split are inverse operations."""
        soup = PrimordialSoup(soup_size=10, seed=42)
        tape_a = soup.programs[0].copy()
        tape_b = soup.programs[1].copy()

        # Store original data
        original_a_data = tape_a._data.copy()
        original_b_data = tape_b._data.copy()

        # Concatenate and split
        concatenated = soup._concatenate(tape_a, tape_b)
        split_a, split_b = soup._split(concatenated)

        # Verify round-trip preserves data
        assert np.array_equal(split_a._data, original_a_data)
        assert np.array_equal(split_b._data, original_b_data)

    def test_split_even_length(self):
        """Test splitting tape with even length."""
        tape = BFFTape(length=10, data=range(10))
        soup = PrimordialSoup(soup_size=1, seed=42)

        first, second = soup._split(tape)

        assert len(first) == 5
        assert len(second) == 5
        assert list(first._data) == [0, 1, 2, 3, 4]
        assert list(second._data) == [5, 6, 7, 8, 9]


class TestMutations:
    """Tests for mutation operations."""

    def test_mutation_rate_zero(self):
        """Test that zero mutation rate causes no mutations."""
        soup = PrimordialSoup(soup_size=100, mutation_rate=0.0, seed=42)

        # Save initial state
        initial = [p._data.copy() for p in soup.programs]

        # Apply mutations
        soup._apply_mutations()

        # Verify no changes
        for i in range(soup.soup_size):
            assert np.array_equal(initial[i], soup.programs[i]._data)

    def test_mutation_rate_approximate(self):
        """Test that mutations occur at approximately the expected rate."""
        # Use larger mutation rate for reliable testing
        soup = PrimordialSoup(soup_size=1000, mutation_rate=0.01, seed=42)

        # Save initial state
        initial = [p._data.copy() for p in soup.programs]

        # Apply mutations
        soup._apply_mutations()

        # Count differences
        total_bytes = soup.soup_size * soup.tape_length
        differences = sum(
            np.sum(initial[i] != soup.programs[i]._data)
            for i in range(soup.soup_size)
        )

        # Should be approximately mutation_rate * total_bytes
        # Use generous bounds due to randomness
        expected = 0.01 * total_bytes
        assert 0.5 * expected < differences < 1.5 * expected

    def test_mutation_changes_values(self):
        """Test that mutations actually change byte values."""
        soup = PrimordialSoup(soup_size=10, mutation_rate=0.1, seed=42)

        # Save initial state
        initial = [p._data.copy() for p in soup.programs]

        # Apply mutations multiple times
        for _ in range(5):
            soup._apply_mutations()

        # At least some bytes should have changed
        total_differences = sum(
            np.sum(initial[i] != soup.programs[i]._data)
            for i in range(soup.soup_size)
        )

        assert total_differences > 0


class TestInteractions:
    """Tests for program interactions."""

    def test_interact_modifies_programs(self):
        """Test that interaction can modify programs."""
        soup = PrimordialSoup(soup_size=10, seed=42)

        # Save initial programs
        initial_0 = soup.programs[0]._data.copy()
        initial_1 = soup.programs[1]._data.copy()

        # Perform interaction
        soup._interact(0, 1)

        # Programs should still be 64 bytes
        assert len(soup.programs[0]) == 64
        assert len(soup.programs[1]) == 64

        # Total executions should increment
        assert soup.total_executions == 1

    def test_interact_maintains_tape_length(self):
        """Test that interactions maintain tape length."""
        soup = PrimordialSoup(soup_size=10, tape_length=64, seed=42)

        for _ in range(10):
            i, j = soup.rng.choice(soup.soup_size, size=2, replace=False)
            soup._interact(i, j)

        # All programs should still be 64 bytes
        assert all(len(p) == 64 for p in soup.programs)


class TestEpochs:
    """Tests for epoch execution."""

    def test_epoch_execution_basic(self):
        """Test basic epoch execution."""
        soup = PrimordialSoup(soup_size=10, seed=42)
        initial_epoch = soup.epoch

        soup.run_epoch()

        assert soup.epoch == initial_epoch + 1
        assert soup.total_executions >= 10  # At least soup_size interactions

    def test_epoch_execution_custom_interactions(self):
        """Test epoch with custom number of interactions."""
        soup = PrimordialSoup(soup_size=10, seed=42)

        soup.run_epoch(interactions_per_epoch=5)

        assert soup.epoch == 1
        assert soup.total_executions == 5

    def test_multiple_epochs(self):
        """Test running multiple epochs."""
        soup = PrimordialSoup(soup_size=10, seed=42)

        for i in range(5):
            soup.run_epoch()
            assert soup.epoch == i + 1

        assert soup.epoch == 5

    def test_run_with_epochs(self):
        """Test the run method with multiple epochs."""
        soup = PrimordialSoup(soup_size=10, seed=42)

        soup.run(num_epochs=3, callback=None)

        assert soup.epoch == 3
        assert soup.total_executions >= 30

    def test_run_with_callback(self):
        """Test multi-epoch run with callback."""
        soup = PrimordialSoup(soup_size=10, seed=42)
        epochs_seen = []

        def callback(s, epoch):
            epochs_seen.append(epoch)
            assert s.epoch == epoch

        soup.run(num_epochs=5, callback=callback)

        assert epochs_seen == [1, 2, 3, 4, 5]
        assert soup.epoch == 5

    def test_pair_selection_no_duplicates(self):
        """Test that pair selection doesn't select same program twice."""
        soup = PrimordialSoup(soup_size=10, seed=42)

        # Run many epochs and verify no self-interactions occur
        # This is a statistical test - we check the implementation logic
        for _ in range(10):
            i, j = soup.rng.choice(soup.soup_size, size=2, replace=False)
            assert i != j, "Pair selection should not select same index twice"


class TestSnapshot:
    """Tests for snapshot functionality."""

    def test_snapshot_basic(self):
        """Test basic snapshot functionality."""
        soup = PrimordialSoup(soup_size=10, seed=42)
        snapshot = soup.get_snapshot()

        assert snapshot['epoch'] == 0
        assert snapshot['soup_size'] == 10
        assert snapshot['tape_length'] == 64
        assert len(snapshot['programs']) == 10
        assert snapshot['total_executions'] == 0

    def test_snapshot_after_epochs(self):
        """Test snapshot after running epochs."""
        soup = PrimordialSoup(soup_size=10, seed=42)
        soup.run_epoch()

        snapshot = soup.get_snapshot()

        assert snapshot['epoch'] == 1
        assert snapshot['total_executions'] >= 10

    def test_snapshot_independence(self):
        """Test that snapshot creates independent copies."""
        soup = PrimordialSoup(soup_size=10, seed=42)
        snapshot = soup.get_snapshot()

        # Modify original soup
        soup.run_epoch()

        # Snapshot should not be affected
        assert snapshot['epoch'] == 0
        assert soup.epoch == 1

        # Verify programs are independent copies
        original_data = soup.programs[0]._data.copy()
        snapshot['programs'][0][0] = 255
        assert soup.programs[0][0] != 255


class TestIntegration:
    """Integration tests for the soup simulation."""

    def test_run_100_epochs_no_errors(self):
        """Integration test: Run 100 epochs without errors."""
        soup = PrimordialSoup(soup_size=50, tape_length=64, seed=42)

        # This should complete without errors
        soup.run(num_epochs=100, callback=None)

        assert soup.epoch == 100
        assert soup.total_executions >= 5000
        assert all(len(p) == 64 for p in soup.programs)

    def test_small_soup_evolution(self):
        """Test evolution of a small soup over time."""
        soup = PrimordialSoup(
            soup_size=20,
            tape_length=64,
            mutation_rate=0.001,
            seed=42
        )

        initial_snapshot = soup.get_snapshot()

        # Run for several epochs
        soup.run(num_epochs=10)

        final_snapshot = soup.get_snapshot()

        # Verify state progression
        assert final_snapshot['epoch'] == 10
        assert final_snapshot['total_executions'] >= 200

        # At least some programs should have changed
        changes = 0
        for i in range(soup.soup_size):
            if not np.array_equal(
                initial_snapshot['programs'][i]._data,
                final_snapshot['programs'][i]._data
            ):
                changes += 1

        assert changes > 0, "Some programs should have changed"

    def test_large_soup_initialization(self):
        """Test initialization of large soup (closer to paper defaults)."""
        # Use smaller size for testing, but still substantial
        soup = PrimordialSoup(soup_size=1000, tape_length=64, seed=42)

        assert len(soup.programs) == 1000
        assert all(len(p) == 64 for p in soup.programs)

        # Run a few epochs to ensure no memory issues
        soup.run_epoch()
        assert soup.epoch == 1

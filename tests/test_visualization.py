"""
Unit tests for visualization module.

Tests data validation and smoke tests for plot generation.
"""

import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from src.bff.visualization import SoupVisualizer


class TestSoupVisualizer:
    """Test cases for SoupVisualizer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.visualizer = SoupVisualizer()

    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')

    def test_init(self):
        """Test visualizer initialization."""
        vis = SoupVisualizer()
        assert vis.style == 'seaborn-v0_8-darkgrid'

        vis_custom = SoupVisualizer(style='default')
        assert vis_custom.style == 'default'

    def test_plot_complexity_over_time_basic(self):
        """Test basic complexity over time plotting."""
        history = [
            {'epoch': 0, 'high_order_entropy': 0.1},
            {'epoch': 1, 'high_order_entropy': 0.3},
            {'epoch': 2, 'high_order_entropy': 0.5}
        ]

        # Smoke test - should not raise exception
        self.visualizer.plot_complexity_over_time(history)

    def test_plot_complexity_over_time_save(self, tmp_path):
        """Test saving complexity over time plot."""
        history = [
            {'epoch': 0, 'high_order_entropy': 0.1},
            {'epoch': 1, 'high_order_entropy': 0.3}
        ]

        save_path = tmp_path / "complexity.png"
        self.visualizer.plot_complexity_over_time(history, str(save_path))

        assert save_path.exists()

    def test_plot_complexity_over_time_empty(self):
        """Test plotting with empty history creates empty plot without error."""
        # Empty data should not raise exception, just create empty plot
        self.visualizer.plot_complexity_over_time([])

    def test_plot_complexity_distribution_basic(self):
        """Test basic complexity distribution plotting."""
        run1 = [
            {'high_order_entropy': 0.1},
            {'high_order_entropy': 0.3}
        ]
        run2 = [
            {'high_order_entropy': 0.2},
            {'high_order_entropy': 0.4}
        ]

        # Smoke test
        self.visualizer.plot_complexity_distribution([run1, run2])

    def test_plot_complexity_distribution_custom_quantiles(self):
        """Test complexity distribution with custom quantiles."""
        runs = [
            [{'high_order_entropy': 0.1}, {'high_order_entropy': 0.2}],
            [{'high_order_entropy': 0.15}, {'high_order_entropy': 0.25}],
            [{'high_order_entropy': 0.12}, {'high_order_entropy': 0.22}]
        ]

        quantiles = [0.25, 0.5, 0.75]
        self.visualizer.plot_complexity_distribution(runs, quantiles=quantiles)

    def test_plot_complexity_distribution_save(self, tmp_path):
        """Test saving complexity distribution plot."""
        runs = [
            [{'high_order_entropy': 0.1}, {'high_order_entropy': 0.2}],
            [{'high_order_entropy': 0.15}, {'high_order_entropy': 0.25}]
        ]

        save_path = tmp_path / "distribution.png"
        self.visualizer.plot_complexity_distribution(runs, save_path=str(save_path))

        assert save_path.exists()

    def test_plot_token_statistics_basic(self):
        """Test basic token statistics plotting."""
        history = [
            {'epoch': 0, 'unique_tokens': 100, 'high_order_entropy': 0.1},
            {'epoch': 1, 'unique_tokens': 200, 'high_order_entropy': 0.3},
            {'epoch': 2, 'unique_tokens': 300, 'high_order_entropy': 0.5}
        ]

        # Smoke test
        self.visualizer.plot_token_statistics(history)

    def test_plot_token_statistics_save(self, tmp_path):
        """Test saving token statistics plot."""
        history = [
            {'epoch': 0, 'unique_tokens': 100, 'high_order_entropy': 0.1},
            {'epoch': 1, 'unique_tokens': 200, 'high_order_entropy': 0.3}
        ]

        save_path = tmp_path / "tokens.png"
        self.visualizer.plot_token_statistics(history, str(save_path))

        assert save_path.exists()

    def test_plot_mutation_rate_heatmap_basic(self):
        """Test basic mutation rate heatmap plotting."""
        results = {
            (0.001, 100): 5,
            (0.001, 200): 3,
            (0.01, 100): 7,
            (0.01, 200): 4
        }
        mutation_rates = [0.001, 0.01]
        epoch_bins = [100, 200]

        # Smoke test
        self.visualizer.plot_mutation_rate_heatmap(
            results, mutation_rates, epoch_bins
        )

    def test_plot_mutation_rate_heatmap_save(self, tmp_path):
        """Test saving mutation rate heatmap."""
        results = {(0.001, 100): 5, (0.01, 100): 7}
        mutation_rates = [0.001, 0.01]
        epoch_bins = [100]

        save_path = tmp_path / "heatmap.png"
        self.visualizer.plot_mutation_rate_heatmap(
            results, mutation_rates, epoch_bins, str(save_path)
        )

        assert save_path.exists()

    def test_plot_mutation_rate_heatmap_normalization(self):
        """Test that mutation rate heatmap normalizes rows correctly."""
        results = {
            (0.001, 100): 10,
            (0.001, 200): 20,
            (0.01, 100): 30,
            (0.01, 200): 60
        }
        mutation_rates = [0.001, 0.01]
        epoch_bins = [100, 200]

        # Should not raise exception with normalization
        self.visualizer.plot_mutation_rate_heatmap(
            results, mutation_rates, epoch_bins
        )

    def test_plot_complexity_histogram_basic(self):
        """Test basic complexity histogram plotting."""
        datasets = {
            'Control': [0.1, 0.2, 0.3, 0.4],
            'Treatment': [0.3, 0.4, 0.5, 0.6]
        }

        # Smoke test
        self.visualizer.plot_complexity_histogram(datasets)

    def test_plot_complexity_histogram_custom_bins(self):
        """Test complexity histogram with custom bins."""
        datasets = {
            'Dataset1': [0.1, 0.2, 0.3],
            'Dataset2': [0.4, 0.5, 0.6]
        }

        self.visualizer.plot_complexity_histogram(datasets, bins=10)

    def test_plot_complexity_histogram_save(self, tmp_path):
        """Test saving complexity histogram."""
        datasets = {
            'Control': [0.1, 0.2, 0.3],
            'Treatment': [0.4, 0.5, 0.6]
        }

        save_path = tmp_path / "histogram.png"
        self.visualizer.plot_complexity_histogram(datasets, save_path=str(save_path))

        assert save_path.exists()

    def test_plot_2d_grid_basic(self):
        """Test basic 2D grid plotting."""
        # Create mock grid_soup object
        class MockGridSoup:
            def __init__(self):
                self.height = 4
                self.width = 4
                self.epoch = 10
                self.programs = []
                for i in range(16):
                    prog = type('obj', (object,), {
                        'data': np.random.randint(0, 256, size=10, dtype=np.uint8)
                    })
                    self.programs.append(prog)

        grid_soup = MockGridSoup()

        # Smoke test
        self.visualizer.plot_2d_grid(grid_soup)

    def test_plot_2d_grid_save(self, tmp_path):
        """Test saving 2D grid plot."""
        class MockGridSoup:
            def __init__(self):
                self.height = 2
                self.width = 2
                self.epoch = 5
                self.programs = []
                for i in range(4):
                    prog = type('obj', (object,), {
                        'data': np.random.randint(0, 256, size=10, dtype=np.uint8)
                    })
                    self.programs.append(prog)

        grid_soup = MockGridSoup()
        save_path = tmp_path / "grid.png"

        self.visualizer.plot_2d_grid(grid_soup, str(save_path))

        assert save_path.exists()


class TestDataValidation:
    """Test data validation for visualization inputs."""

    def setup_method(self):
        """Set up test fixtures."""
        self.visualizer = SoupVisualizer()

    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')

    def test_complexity_over_time_missing_keys(self):
        """Test error handling for missing required keys."""
        invalid_history = [{'epoch': 0}]  # Missing 'high_order_entropy'

        with pytest.raises(KeyError):
            self.visualizer.plot_complexity_over_time(invalid_history)

    def test_token_statistics_missing_keys(self):
        """Test error handling for missing token statistics keys."""
        invalid_history = [{'epoch': 0, 'unique_tokens': 100}]  # Missing entropy

        with pytest.raises(KeyError):
            self.visualizer.plot_token_statistics(invalid_history)

    def test_complexity_distribution_empty_runs(self):
        """Test error handling for empty runs list."""
        with pytest.raises(ValueError):
            self.visualizer.plot_complexity_distribution([])

    def test_complexity_histogram_empty_datasets(self):
        """Test histogram with empty datasets dict."""
        self.visualizer.plot_complexity_histogram({})
        # Should not raise exception, just create empty plot

"""
Visualization tools for BFF soup evolution.

This module provides visualization capabilities for analyzing soup evolution,
complexity metrics, token statistics, and spatial distributions.
"""

import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Optional, Tuple, Any
import numpy as np


class SoupVisualizer:
    """
    Visualization tools for BFF soup evolution.

    Provides methods to create plots matching the figures from the paper:
    - Figure 1: Token statistics over time
    - Figure 5: Complexity evolution
    - Figure 6: Mutation rate heat maps
    - Figure 7: Complexity histograms
    - Figure 8: 2D spatial soup visualization
    """

    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """
        Initialize visualizer with consistent styling.

        Args:
            style: Matplotlib style to use for plots
        """
        plt.style.use(style)
        sns.set_palette("husl")
        self.style = style

    def plot_complexity_over_time(
        self,
        history: List[Dict[str, float]],
        save_path: Optional[str] = None
    ):
        """
        Plot high-order entropy over time.

        Replicates Figure 5 from the paper for a single run.

        Args:
            history: List of metric dictionaries from each epoch.
                     Each dict should have 'epoch' and 'high_order_entropy' keys.
            save_path: Optional path to save figure

        Example:
            >>> visualizer = SoupVisualizer()
            >>> history = [
            ...     {'epoch': 0, 'high_order_entropy': 0.1},
            ...     {'epoch': 1, 'high_order_entropy': 0.3},
            ...     {'epoch': 2, 'high_order_entropy': 0.5}
            ... ]
            >>> visualizer.plot_complexity_over_time(history, 'complexity.png')
        """
        epochs = [h['epoch'] for h in history]
        complexity = [h['high_order_entropy'] for h in history]

        plt.figure(figsize=(12, 6))
        plt.plot(epochs, complexity, linewidth=2)
        plt.xlabel('Epoch', fontsize=12)
        plt.ylabel('High-order Entropy', fontsize=12)
        plt.title('Evolution of Complexity Over Time', fontsize=14)
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_complexity_distribution(
        self,
        runs: List[List[Dict[str, float]]],
        quantiles: List[float] = [0.1, 0.25, 0.5, 0.75, 0.9],
        save_path: Optional[str] = None
    ):
        """
        Plot complexity distribution over time across multiple runs.

        Replicates Figure 5 from the paper with quantile bands.

        Args:
            runs: List of run histories (each run is a list of metric dicts).
                  Each metric dict should have 'high_order_entropy' key.
            quantiles: Quantiles to display as shaded regions
            save_path: Optional path to save figure

        Example:
            >>> visualizer = SoupVisualizer()
            >>> run1 = [{'high_order_entropy': 0.1}, {'high_order_entropy': 0.3}]
            >>> run2 = [{'high_order_entropy': 0.2}, {'high_order_entropy': 0.4}]
            >>> visualizer.plot_complexity_distribution([run1, run2])
        """
        # Find common epoch range
        max_epochs = min(len(run) for run in runs)
        epochs = list(range(max_epochs))

        # Collect complexity values at each epoch
        complexity_matrix = np.array([
            [run[e]['high_order_entropy'] for e in epochs]
            for run in runs
        ])

        # Calculate quantiles
        quantile_values = {}
        for q in quantiles:
            quantile_values[q] = np.quantile(complexity_matrix, q, axis=0)

        # Plot
        plt.figure(figsize=(14, 7))

        # Median line
        plt.plot(epochs, quantile_values[0.5],
                linewidth=2, label='Median', color='darkblue')

        # Quantile bands
        colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(quantiles)//2))
        for i in range(len(quantiles)//2):
            lower_q = quantiles[i]
            upper_q = quantiles[-(i+1)]
            plt.fill_between(
                epochs,
                quantile_values[lower_q],
                quantile_values[upper_q],
                alpha=0.3,
                color=colors[i],
                label=f'{int(lower_q*100)}-{int(upper_q*100)}%'
            )

        plt.xlabel('Epoch', fontsize=12)
        plt.ylabel('High-order Entropy', fontsize=12)
        plt.title(f'Complexity Distribution Over Time ({len(runs)} runs)',
                 fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_token_statistics(
        self,
        history: List[Dict[str, Any]],
        save_path: Optional[str] = None
    ):
        """
        Plot token tracking statistics over time.

        Replicates Figure 1 from the paper.

        Args:
            history: List of dicts with token statistics per epoch.
                     Each dict should have 'epoch', 'unique_tokens', and
                     'high_order_entropy' keys.
            save_path: Optional path to save figure

        Example:
            >>> visualizer = SoupVisualizer()
            >>> history = [
            ...     {'epoch': 0, 'unique_tokens': 100, 'high_order_entropy': 0.1},
            ...     {'epoch': 1, 'unique_tokens': 200, 'high_order_entropy': 0.3}
            ... ]
            >>> visualizer.plot_token_statistics(history)
        """
        epochs = [h['epoch'] for h in history]
        unique_tokens = [h['unique_tokens'] for h in history]
        complexity = [h['high_order_entropy'] for h in history]

        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot unique tokens
        color = 'tab:blue'
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Unique Tokens', color=color, fontsize=12)
        ax1.plot(epochs, unique_tokens, color=color, linewidth=2)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_yscale('log')

        # Plot complexity on second y-axis
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('High-order Entropy', color=color, fontsize=12)
        ax2.plot(epochs, complexity, color=color, linewidth=2, linestyle='--')
        ax2.tick_params(axis='y', labelcolor=color)

        plt.title('Token Statistics and Complexity Over Time', fontsize=14)
        fig.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_mutation_rate_heatmap(
        self,
        results: Dict[Tuple[float, int], int],
        mutation_rates: List[float],
        epoch_bins: List[int],
        save_path: Optional[str] = None
    ):
        """
        Plot heat map of mutation rate vs time to complexity.

        Replicates Figure 6 from the paper.

        Args:
            results: Dict mapping (mutation_rate, epoch_bin) to count
            mutation_rates: List of mutation rates tested
            epoch_bins: List of epoch bins
            save_path: Optional path to save figure

        Example:
            >>> visualizer = SoupVisualizer()
            >>> results = {(0.001, 100): 5, (0.001, 200): 3, (0.01, 100): 7}
            >>> mutation_rates = [0.001, 0.01]
            >>> epoch_bins = [100, 200]
            >>> visualizer.plot_mutation_rate_heatmap(results, mutation_rates, epoch_bins)
        """
        # Create matrix
        matrix = np.zeros((len(mutation_rates), len(epoch_bins)))
        for i, mr in enumerate(mutation_rates):
            for j, eb in enumerate(epoch_bins):
                matrix[i, j] = results.get((mr, eb), 0)

        # Normalize rows
        row_sums = matrix.sum(axis=1, keepdims=True)
        matrix = np.divide(matrix, row_sums, where=row_sums != 0)

        # Plot
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            matrix,
            annot=True,
            fmt='.2f',
            cmap='YlOrRd',
            xticklabels=epoch_bins,
            yticklabels=[f'{mr:.3%}' for mr in mutation_rates],
            cbar_kws={'label': 'Fraction of runs'}
        )
        plt.xlabel('Epochs', fontsize=12)
        plt.ylabel('Mutation Rate', fontsize=12)
        plt.title('Distribution of Time to ≥ 1 Complexity', fontsize=14)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_complexity_histogram(
        self,
        datasets: Dict[str, List[float]],
        bins: int = 20,
        save_path: Optional[str] = None
    ):
        """
        Plot histogram comparison of final complexity.

        Replicates Figure 7 from the paper.

        Args:
            datasets: Dict mapping label to list of complexity values
            bins: Number of histogram bins
            save_path: Optional path to save figure

        Example:
            >>> visualizer = SoupVisualizer()
            >>> datasets = {
            ...     'Control': [0.1, 0.2, 0.3, 0.4],
            ...     'Treatment': [0.3, 0.4, 0.5, 0.6]
            ... }
            >>> visualizer.plot_complexity_histogram(datasets)
        """
        plt.figure(figsize=(12, 6))

        for label, values in datasets.items():
            plt.hist(values, bins=bins, alpha=0.6, label=label, edgecolor='black')

        plt.xlabel('High-order Entropy', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.title('Final Complexity Distribution Comparison', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_2d_grid(
        self,
        grid_soup: Any,
        save_path: Optional[str] = None
    ):
        """
        Visualize 2D spatial soup.

        Replicates Figure 8 from the paper.

        Args:
            grid_soup: Grid2DSoup instance with height, width, programs, and epoch attributes
            save_path: Optional path to save figure

        Example:
            >>> visualizer = SoupVisualizer()
            >>> # Assuming grid_soup is a Grid2DSoup instance
            >>> visualizer.plot_2d_grid(grid_soup, 'spatial_soup.png')
        """
        # Create color map based on program content
        # Use hash of first few bytes for color
        grid = np.zeros((grid_soup.height, grid_soup.width, 3))

        for i in range(grid_soup.height):
            for j in range(grid_soup.width):
                idx = i * grid_soup.width + j
                prog = grid_soup.programs[idx]

                # Simple hash to RGB
                hash_val = hash(tuple(prog.data[:4])) % (256**3)
                r = (hash_val >> 16) & 0xFF
                g = (hash_val >> 8) & 0xFF
                b = hash_val & 0xFF

                grid[i, j] = [r/255, g/255, b/255]

        plt.figure(figsize=(12, 8))
        plt.imshow(grid, interpolation='nearest')
        plt.title(f'2D Spatial Soup (Epoch {grid_soup.epoch})', fontsize=14)
        plt.axis('off')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

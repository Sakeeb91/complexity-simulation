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

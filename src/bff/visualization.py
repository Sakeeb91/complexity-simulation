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

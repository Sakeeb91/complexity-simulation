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

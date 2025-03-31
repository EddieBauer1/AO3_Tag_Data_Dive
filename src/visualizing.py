import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

def make_heatmap(data: pd.DataFrame, scoring: str, n_decks: int, seed: int) -> None:
    """
    Turns dataframe into a heatmap. I decided to keep the full heatmap instead of cutting it in half, for easier interpretation.
    
    Parameters:
        data (DataFrame): Dataframe of player 2 win percentages to be converted into a heatmap.
    
    Returns:
        None.
    """
    # mask = np.triu(np.ones_like(data, dtype=bool)) <-- If I want to remove upper diagonal
    # Remove diagonal values (where both players have the same combination)
    np.fill_diagonal(data.values, np.nan)
    # Create heatmap
    sns.heatmap(data, annot = True, vmax = 1, vmin = 0, center = 0.5, fmt = ".2f", cmap = 'coolwarm', annot_kws = {"size":11}, mask=np.isnan(data), cbar = False)
    # Title of heatmap, specifying scoring type, number of decks, and seed
    plt.title(f'Heatmap of Your Win Percentages with {scoring} Scoring ({n_decks} Decks)(Seed = {seed})')
    # Save heatmap as pdf and png
    plt.savefig(f'figures/{n_decks}_Decks_Seed-{seed}_{scoring}.pdf', bbox_inches='tight')
    plt.savefig(f'figures/{n_decks}_Decks_Seed-{seed}_{scoring}.png', bbox_inches='tight')
    # Show heatmap
    plt.show()
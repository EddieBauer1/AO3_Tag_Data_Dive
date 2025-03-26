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
    # mask = np.triu(np.ones_like(data, dtype=bool))
    np.fill_diagonal(data.values, np.nan)
    sns.heatmap(data, annot = True, vmax = 1, vmin = 0, center = 0.5, fmt = ".2f", cmap = 'coolwarm', annot_kws = {"size":11}, mask=np.isnan(data), cbar = False)
    plt.title(f'Heatmap of Your Win Percentages with {scoring} Scoring ({n_decks} Decks)(Seed = {seed})')
    plt.savefig(f'figures/{n_decks}_Decks_Seed-{seed}_{scoring}.pdf', bbox_inches='tight')
    plt.savefig(f'figures/{n_decks}_Decks_Seed-{seed}_{scoring}.png', bbox_inches='tight')
    plt.show()
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from src.processing import create_dataframe, get_values, merge_lists

def make_heatmap(data: list, scoring: str, n_decks: int, seed: int) -> None:
    """
    Turns dataframe into a heatmap. I decided to keep the full heatmap instead of cutting it in half, for easier interpretation.
    
    Parameters:
        data (list): List of player 2 wins and ties to be converted into a heatmap.
        scoring (str): Type of scoring for the heatmap to display, either "Tricks" or "Cards"
        n_decks (int): Number of decks that were simulated to create results, to be displayed in title.
        seed (int): Seed that was used during simulation, to be displayed in title.
    
    Returns:
        None.
    """
    # mask = np.triu(np.ones_like(data, dtype=bool)) <-- If I want to remove upper diagonal
    # Create a dataframe of just wins
    wins_df = create_dataframe(data)
    # Create lists of wins and ties from the data
    wins_list = get_values(data, "wins")
    ties_list = get_values(data, "ties")
    # Merge lists into Wins(Ties) format, to be used for heatmap labels, then turns that list into an array
    data_list = merge_lists(wins_list, ties_list)
    text = [data_list[0:8], data_list[8:16], data_list[16:24], data_list[24:32], data_list[32:40], data_list[40:48], data_list[48:56], data_list[56:64]]
    # Sets diagonals in dataframe to -1, so that they can be removed later
    np.fill_diagonal(wins_df.values, -1)
    # Create heatmap, label with wins and ties, remove diagonal
    sns.heatmap(wins_df, annot = text, vmax = n_decks, vmin = 0, center = n_decks/2, fmt = "", cmap = 'coolwarm', mask = wins_df == -1, cbar = False)
    # Title of heatmap, specifying scoring type, number of decks, and seed
    plt.title(f'Heatmap of Your Wins and Ties with {scoring} Scoring\n({n_decks} Decks)(Seed = {seed})')
    # Save heatmap as pdf and png
    plt.savefig(f'figures/{n_decks}_Decks_Seed-{seed}_{scoring}.pdf', bbox_inches='tight')
    plt.savefig(f'figures/{n_decks}_Decks_Seed-{seed}_{scoring}.png', bbox_inches='tight')
    # Show heatmap
    plt.show()
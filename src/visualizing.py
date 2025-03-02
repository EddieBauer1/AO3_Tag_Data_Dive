import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def make_heatmap(data: pd.DataFrame) -> None:
    """
    Turns dataframe into a heatmap. I decided to keep the full heatmap instead of cutting it in half, for easier interpretation.
    
    Parameters:
        data (DataFrame): Dataframe of player 2 win percentages to be convertaed into a heatmap.
    
    Returns:
        None.
    """
    # mask = np.triu(np.ones_like(data, dtype=bool))
    # In case I want to cut the heatmap in half
    sns.heatmap(data, annot = True, vmax = 1, vmin = 0, center = 0.5, fmt = ".2f", cmap = 'coolwarm', annot_kws = {"size":11})
    plt.title('Heatmap of Player 2 Win Percentages')
    plt.savefig('figures/Win_Percentage_Heatmap.pdf', bbox_inches='tight')
    plt.savefig('figures/Win_Percentage_Heatmap.png', bbox_inches='tight')
    plt.show()
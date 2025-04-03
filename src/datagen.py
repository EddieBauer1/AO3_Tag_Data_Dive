import numpy as np
from src.helpers import debugger_factory

# Define the half deck size
HALF_DECK_SIZE = 26  # Adjust this depending on the deck structure

@debugger_factory(show_args=True)
def get_decks(n_decks: int, 
              half_deck_size: int = HALF_DECK_SIZE, 
              seed: int = 42) -> np.ndarray:
    """
    Efficiently generate `n_decks` shuffled decks using NumPy.
    
    Parameters:
        n_decks (int): Number of decks to generate.
        half_deck_size (int): Size of half a deck. Default is 26.
        seed (int): Seed for random number generation for reproducibility. Default is 42.
    
    Returns:
        decks (np.ndarray): 2D array of shape (n_decks, num_cards), each row is a shuffled deck.
    """
    # Initialize the deck (half Bs and half Rs for simplicity, adjust as needed)
    init_deck = ["B"] * half_deck_size + ["R"] * half_deck_size
    decks = np.tile(init_deck, (n_decks, 1))  # Create `n_decks` identical decks
    
    # Random number generator (RNG)
    rng = np.random.default_rng(seed)
    
    # Shuffle each deck independently
    rng.permuted(decks, axis=1, out=decks)
    
    return decks

def store_decks(decks: list, filename: str) -> None:
    """
    Store shuffled decks onto a .npy file.
    
    Parameters:
        decks (list): List of shuffled decks.
        filename (str): Name of created .npy file.
    
    Returns:
        None.
    """
    np.save(f"data/{filename}.npy", decks)

def load_decks(filename: str) -> np.ndarray:
    """
    Load shuffled decks from a .npy file.
    
    Parameters:
        filename (str): Name of .npy file to load deck from.
    
    Returns:
        np.ndarray: 2D array (n_decks, num_cards), each row is a shuffled deck.
    """
    return np.load(f"data/{filename}.npy")
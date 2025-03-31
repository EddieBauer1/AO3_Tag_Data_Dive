from src.datagen import get_decks, store_decks
from src.processing import calculate_all_results, store_results, create_dataframe, load_results
from src.visualizing import make_heatmap

def run_project_penney(half_deck_size: int = 26, n_decks: int = 10000, seed: int = 42) -> None:
    """
    Runs Project Penney, automatically running each function.
    
    Parameters:
        n_decks (int): Number of decks to generate.
        half_deck_size (int): Size of half a deck. Default is 26.
        seed (int): Seed for random number generation for reproducibility. Default is 42.
    
    Returns:
        None.
    """
    # Create and store decks
    decks = get_decks(n_decks = n_decks, half_deck_size = half_deck_size, seed = seed)
    store_decks(decks, f'{n_decks}_Decks')

    # Play Penney's Game with the decks, record player 2 win percentages for every choice in every deck
    results = calculate_all_results(decks)

    # Save results, specify number of decks and scoring type
    tricks = results[0]
    cards = results[1]
    store_results(tricks, f'{n_decks}_Tricks_Result')
    store_results(cards, f'{n_decks}_Cards_Result')

    # Create and save heatmaps
    trick_data = create_dataframe(tricks)
    make_heatmap(trick_data, "Tricks", n_decks, seed)
    card_data = create_dataframe(cards)
    make_heatmap(card_data, "Cards", n_decks, seed)


def append(original_decks: int = 10000, seed: int = 42, half_deck_size: int = 26, new_decks: int = 100) -> None:
    """
    Appends additional decks to pre-existing decks, creates heatmaps.
    
    Parameters:
        original_decks (int): Number of pre-existing decks to append new decks to.
        half_deck_size (int): Size of half a deck. Default is 26.
        seed (int): Seed for random number generation for reproducibility. Default is 42.
        new_decks(int): Number of new decks to append to original_decks.
    
    Returns:
        None.
    """
    # Generates new decks to append
    decks = get_decks(n_decks = new_decks, half_deck_size = half_deck_size, seed = seed)
    results = calculate_all_results(decks)
    tricks = results[0]
    cards = results[1]

    # Load pre-existing decks
    original_cards = load_results(f'{original_decks}_Cards_Result')
    original_tricks = load_results(f'{original_decks}_Tricks_Result')

    # Adds results of new decks to the pre-existing decks results
    appended_tricks = []
    appended_cards = []
    i = 0
    while i < len(original_cards):
        appended_cards.append([original_cards[i][0], original_cards[i][1], (float(original_cards[i][2])*original_decks + float(cards[i][2])*new_decks)/(original_decks + new_decks)])
        appended_tricks.append([original_tricks[i][0], original_tricks[i][1], (float(original_tricks[i][2])*original_decks + float(tricks[i][2])*new_decks)/(original_decks + new_decks)])
        i+=1

    # Store new results of the appended decks
    store_results(tricks, f'{original_decks+new_decks}_Tricks_Result')
    store_results(cards, f'{original_decks+new_decks}_Cards_Result')

    # Create and save heatmaps of appended decks
    trick_data = create_dataframe(appended_tricks)
    make_heatmap(trick_data, "Tricks", original_decks+new_decks, seed)
    card_data = create_dataframe(appended_cards)
    make_heatmap(card_data, "Cards", original_decks+new_decks, seed)
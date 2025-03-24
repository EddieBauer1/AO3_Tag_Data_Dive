import numpy as np
import pandas as pd

def calculate_scores(deck: np.ndarray, player1: list, player2: list) -> tuple:
    """
    Calculate score of singular game using tricks method.
    
    Parameters:
        deck (np.ndarray): Singular deck of shuffled cards.
        player1 (list): player1's selection of card colors (list of 3 ints, 0 or 1).
        player2 (list): player1's selection of card colors (list of 3 ints, 0 or 1).
    
    Returns:
        Tuple: contains player1_score (int), player2_score (int), the number of tricks scored by each player after going through the deck of cards.
    """
    player1_tricks_score = 0
    player2_tricks_score = 0
    player1_cards_score = 0
    player2_cards_score = 0
    cards = 0
    deck_length = len(deck)
    
    i = 0
    while i < deck_length - 2:  # Make sure we don't go out of bounds
        # Check for match for Player 1
        if deck[i:i+3].tolist() == player1:
            player1_tricks_score += 1
            player1_cards_score += cards+3
            i = i+3
            cards = 0
        # Check for match for Player 2
        elif deck[i:i+3].tolist() == player2:
            player2_tricks_score += 1
            player2_cards_score += cards+3
            i = i+3
            cards = 0
        # Move on if no match
        else:
            i+=1
            cards+=1
    return player1_tricks_score, player2_tricks_score, player1_cards_score, player2_cards_score



def collect_scores(decks: np.ndarray, player1: list, player2: list) -> tuple:
    """
    Score games using tricks method, using every deck contained in "decks".
    
    Parameters:
        decks (np.ndarray): 2D array, contains an array of shuffled decks.
        player1 (list): player1's selection of card colors (list of 3 ints, 0 or 1).
        player2 (list): player1's selection of card colors (list of 3 ints, 0 or 1).
    
    Returns:
        scores: list of tuples, each one containing player1 and player2 score from a singular game. One tuple for each deck in decks.
    """
    tricks = []
    cards = []
    for deck in decks:
        player1_tricks, player2_tricks, player1_cards, player2_cards = calculate_scores(deck, player1, player2)
        tricks.append((player1_tricks, player2_tricks))
        cards.append((player1_cards, player2_cards))
    return (tricks, cards)



def calculate_win_percentage(decks: np.ndarray, player1: list, player2: list) -> list:
    """
    Goes through array of tuples, then finds percentage of games that player 2 won for that specific combination of player choices.
    
    Parameters:
        decks (np.ndarray): 2D array, contains an array of shuffled decks.
        player1 (list): player1's selection of card colors (list of 3 ints, 0 or 1).
        player2 (list): player1's selection of card colors (list of 3 ints, 0 or 1).
    
    Returns:
        float: decimal representing player 2's win percentage.
    """
    # Collect scores for all games
    scores = collect_scores(decks, player1, player2)
    tricks = scores[0]
    cards = scores[1]
    tricks_scores = np.array(tricks)
    cards_scores = np.array(cards)
    # Compare scores for player1 and player2 and count the wins for player2
    player2_tricks = np.sum(tricks_scores[:, 1] > tricks_scores[:, 0])
    player2_cards = np.sum(cards_scores[:, 1] > cards_scores[:, 0])
    # Return win percentage for player2 in both scoring options
    return [player2_tricks/len(tricks), player2_cards/len(cards)]



def calculate_all_results(decks: np.ndarray) -> list:
    """
    Goes through each combination of possible player choices, and calculates player 2's win percentage for that combo.
    
    Parameters:
        decks (np.ndarray): 2D array, contains an array of shuffled decks.
  
    Returns:
        results: List of tuples, each tuple containing player1 and player2's choices, plus win percentage.
    """
    tricks = []
    cards = []
    # Every possible choice for each player
    choices = [["B", "B", "B"], ["B", "B", "R"], ["B", "R", "B"], ["B", "R", "R"], ["R", "B", "B"], ["R", "B", "R"], ["R", "R", "B"], ["R", "R", "R"]]
    # Goes through each possible player choice, then finds player 2's  win percentage for that combo. HIGHLY INEFFICIENT, try to optimize later.
    for player1 in choices:
        for player2 in choices:
            if player1 == player2:
                tricks.append(["".join(map(str, player1)), "".join(map(str, player2)), 0])
                cards.append(["".join(map(str, player1)), "".join(map(str, player2)), 0])
            else:
                win_pct = calculate_win_percentage(decks, player1, player2)
                tricks.append(["".join(map(str, player1)), "".join(map(str, player2)), win_pct[:1][0]])
                cards.append(["".join(map(str, player1)), "".join(map(str, player2)), win_pct[1:2][0]])
    return tricks, cards



def store_results(results: list, filename: str) -> None:
    """
    Store list of player 2 win percentages of each combo onto a .npy file. (Literally the store_decks function, is it reallllyyyy necessary?)
    
    Parameters:
        results (list): List of win percentages.
        filename (str): Name of created .npy file.
    
    Returns:
        None.
    """
    np.save(f"data/{filename}.npy", results)



def load_results(filename: str) -> np.ndarray:
    """
    Load list of player 2 win percentages for each combo from a .npy file.
    
    Parameters:
        filename (str): Name of .npy file to load results from.
    
    Returns:
        np.ndarray: 2D array, each row is a list of player1 choice, player2 choice, and player2 win percentage.
    """
    return np.load(f"data/{filename}.npy")



def create_dataframe(data: list) -> pd.DataFrame:
    """
    Takes list of win percentages per choice combination, and turns it into a proper dataframe.
    
    Parameters:
        data (list): List of player 2 win percentages to be converted to a dataframe.
    
    Returns:
        dataframe (DataFrame): Each row is player 1's choices, and each column is player 2's choices. Each cell is the player 2 win percentage with those choices.
    """
    # create DataFrame 
    df = pd.DataFrame(data, columns =["Opponent's Pick", 'Your Pick', 'Win Pct'])
    dataframe = df.pivot(index="Opponent's Pick", columns='Your Pick', values='Win Pct')
    return dataframe
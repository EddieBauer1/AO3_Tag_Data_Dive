import numpy as np
import pandas as pd

def calculate_scores(deck: np.ndarray, player1: list, player2: list) -> tuple:
    """
    Calculate score of singular game using both tricks and cards methods.
    
    Parameters:
        deck (np.ndarray): Singular deck of shuffled cards.
        player1 (list): player1's selection of card colors (list of 3 strs, "B" or "R").
        player2 (list): player1's selection of card colors (list of 3 strs, "B" or "R").
    
    Returns:
        Tuple:  Contains player1_tricks_score, player2_tricks_score - the number of tricks scored by each player after going through the deck of cards,
                and player1_cards_score, player2_cards_score - the number of cards scored by each player
    """
    # Create counting variables and find deck length
    player1_tricks_score = 0
    player2_tricks_score = 0
    player1_cards_score = 0
    player2_cards_score = 0
    cards = 0
    deck_length = len(deck)
    i = 0

    while i < deck_length - 2:  # -2 to make sure we don't go out of bounds
        # Check for match for Player 1 - if so, add one to tricks score and cards in sequence to card score
        if deck[i:i+3].tolist() == player1:
            player1_tricks_score += 1
            player1_cards_score += cards+3
            i = i+3
            cards = 0
        # Check for match for Player 2 - if so, add one to tricks score and cards in sequence to card score
        elif deck[i:i+3].tolist() == player2:
            player2_tricks_score += 1
            player2_cards_score += cards+3
            i = i+3
            cards = 0
        # Move on if no match
        else:
            i+=1
            cards+=1
    # Return game results for each player for both scoring methods
    return player1_tricks_score, player2_tricks_score, player1_cards_score, player2_cards_score

def collect_scores(decks: np.ndarray, player1: list, player2: list) -> tuple:
    """
    Score games using both methods, using every deck contained in "decks".
    
    Parameters:
        decks (np.ndarray): 2D array, contains an array of shuffled decks.
        player1 (list): player1's selection of card colors (list of 3 strs, "B" or "R").
        player2 (list): player1's selection of card colors (list of 3 strs, "B" or "R").
    
    Returns:
        Tuple: Contains two lists of tuples - "tricks" and "cards". Each list of tuples contains player1 and player2 scores from every deck in "decks", formatted as one tuple for each deck.
    """
    # Create empty lists that will contain score tuples
    tricks = []
    cards = []
    # Go through each deck and calculate score of that game, then add results to "tricks" and "cards"
    for deck in decks:
        player1_tricks, player2_tricks, player1_cards, player2_cards = calculate_scores(deck, player1, player2)
        tricks.append((player1_tricks, player2_tricks))
        cards.append((player1_cards, player2_cards))
    return (tricks, cards)

def calculate_win_percentage(decks: np.ndarray, player1: list, player2: list) -> tuple:
    """
    Goes through array of tuples, then finds number of games that player 2 won for that specific combination of player choices, and number of resulting ties.
    
    Parameters:
        decks (np.ndarray): 2D array, contains an array of shuffled decks.
        player1 (list): player1's selection of card colors (list of 3 strs, "B" or "R").
        player2 (list): player1's selection of card colors (list of 3 strs, "B" or "R").
    
    Returns:
        List: Contains four floats, the first representing player 2's tricks wins, the second representing player 2's cards wins. The third and fourth contain the number of ties for each type of scoring.
    """
    # Collect scores for all games
    scores = collect_scores(decks, player1, player2)
    tricks = scores[0]
    cards = scores[1]
    tricks_scores = np.array(tricks)
    cards_scores = np.array(cards)
    # Compare scores for player1 and player2 and count the wins for player2 and ties
    player2_tricks = int(np.sum(tricks_scores[:, 1] > tricks_scores[:, 0]))
    player2_cards = int(np.sum(cards_scores[:, 1] > cards_scores[:, 0]))
    ties_tricks = int(np.sum(tricks_scores[:, 1] == tricks_scores[:, 0]))
    ties_cards = int(np.sum(cards_scores[:, 1] == cards_scores[:, 0]))
    # Return number of wins for player2 in both scoring options, as well as number of ties
    return [player2_tricks, player2_cards, ties_tricks, ties_cards]

def calculate_all_results(decks: np.ndarray) -> tuple:
    """
    Goes through each combination of possible player choices, and calculates player 2's wins and ties (tricks and cards) for that combo.
    
    Parameters:
        decks (np.ndarray): 2D array, contains an array of shuffled decks.
  
    Returns:
        Tuple: Tuple containing two lists of tuples (one for tricks and one for cards), each tuple containing player1 and player2's choices, plus player 2's number of wins and ties.
    """
    # Create empty list for each scoring option
    tricks = []
    cards = []
    # Every possible choice for each player
    choices = [["B", "B", "B"], ["B", "B", "R"], ["B", "R", "B"], ["B", "R", "R"], ["R", "B", "B"], ["R", "B", "R"], ["R", "R", "B"], ["R", "R", "R"]]
    # Goes through each possible player choice, then finds player 2's number of wins and ties for that combo. I thought this would be inefficient but people have said my code is fast??
    for player1 in choices:
        for player2 in choices:
            # If player 1 and player 2 have the same choice, skip the calculation
            if player1 == player2:
                tricks.append(["".join(map(str, player1)), "".join(map(str, player2)), 0, 0])
                cards.append(["".join(map(str, player1)), "".join(map(str, player2)), 0, 0])
            else:
                # Calculate wins and ties for that combination of choices
                win_pct = calculate_win_percentage(decks, player1, player2)
                tricks.append(["".join(map(str, player1)), "".join(map(str, player2)), win_pct[:1][0], win_pct[2:3][0]])
                cards.append(["".join(map(str, player1)), "".join(map(str, player2)), win_pct[1:2][0], win_pct[3:4][0]])
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
    # Save result as a npy file with customized name
    np.save(f"data/{filename}.npy", results)

def load_results(filename: str) -> list:
    """
    Load list of player 2 win percentages for each combo from a .npy file.
    
    Parameters:
        filename (str): Name of .npy file to load results from.
    
    Returns:
        np.ndarray: 2D array, each row is a list of player1 choice, player2 choice, and player2 win percentage.
    """
    # Loads npy file from data folder
    return np.load(f"data/{filename}.npy").tolist()

def get_values(data: list, win_or_tie: str) -> list:
    """
    Extracts win values or tie values from tricks or cards result of calculate_all_results function.

    Parameters:
        data (list): List of lists, each one containing player1 and player2 choices, number of player 2 wins, and ties. For example: ["BBB", "RBB", 100, 0]
        win_or_tie (str): String that should either be "wins" or "ties", telling the function which values to extract from the list.

    Returns:
        new_list (list): List of just the win or tie values for each combination of player choices, without the additional info.
    """
    # Create new list
    new_list = []

    # If asked for wins, return list of win values
    if win_or_tie == "wins":
        for value in data:
            new_list.append(value[2])

    # If asked for ties, return list of ties
    elif win_or_tie == "ties":
        for value in data:
            new_list.append(value[3])
    return new_list

def create_dataframe(data: list) -> pd.DataFrame:
    """
    Takes list of wins and ties per choice combination, and turns it into a proper dataframe containing only wins.
    
    Parameters:
        data (list): List of player 2 wins and ties to be converted to a dataframe.
    
    Returns:
        dataframe (DataFrame): Each row is player 1's choices, and each column is player 2's choices. Each cell is the player 2 win percentage with those choices.
    """
    # Create DataFrame 
    df = pd.DataFrame(data, columns =["Opponent's Pick", 'Your Pick', 'Wins', 'Ties'])
    dataframe = df.pivot(index="Opponent's Pick", columns='Your Pick', values='Wins')
    return dataframe

def merge_lists(wins: list, ties: list) -> list:
    """
    Combines the wins and ties lists such that each value in the new list will be in the format "Wins(Ties)" for each combination of player choices.
    
    Parameters:
        wins (list): List of player 2's win numbers for each combination of player choices.
        ties (list): List of tie numbers for each combination of player choices.
    Returns:
        new_list (list): New list of strings with both win and tie values, in Wins(Ties) format.
    """
    new_list = []
    i = 0
    # Create new list item for each value in wins and ties.
    while i < len(wins):
        new_list.append(f'{wins[i]}\n({ties[i]})')
        i+=1
    return new_list
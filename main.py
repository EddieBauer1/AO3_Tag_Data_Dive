from src.run import run_project_penney

if __name__ == "__main__":
    n_decks = int(input("How many decks? "))
    half_deck_size = int(input("Half Deck Size? (26 is standard) "))
    seed = int(input("Seed? "))
    run_project_penney(half_deck_size = half_deck_size, n_decks = n_decks, seed = seed)
from src.run import run_project_penney, append

if __name__ == "__main__":
    # Ask customization options
    n_decks = int(input("How many decks? "))
    seed = int(input("Seed? "))

    # Run the project with the user inputs
    run_project_penney(half_deck_size = 26, n_decks = n_decks, seed = seed)
    # After project runs, ask if user wants to append
    check = (input("Would you like to append to this result? (Y/N) "))
    # If so, run append function after asking how many decks to append
    if check == "Y":
        new_decks = int(input("How many decks? "))
        append(original_decks = n_decks, half_deck_size = 26, new_decks = new_decks, seed = seed)
        print("Thanks for playing!")
    # End simulation
    else:
        print("Thanks for playing!")
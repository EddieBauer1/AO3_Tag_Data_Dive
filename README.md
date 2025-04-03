Project Penney

This code runs simulations of the Humble-Nishiyama Randomness Game, a version of Penney's Game that consists of two players selecting from a deck of playing cards a sequence of three cards - colored black or red - instead of flipping a coin. The results of these simulated games are scored using the tricks and cards methods while saving both the generated shuffled decks and the game results. Lastly, a heatmap will be created using this data in order to find the optimal choices for Player 2 in response to Player 1's selection.

The game should run by asking the user for the number of decks and the randomness seed, then using these customization options to run the game simulations. After the initial simulation, the user will be asked if they want to append more decks.

Everything you need will be in the src folder:

    helpers.py contains the debugger_factory function.

    datagen.py contains functions involved in generating, storing, and retrieving deck data.

    processing.py contains the functions that simulates games, calculates the scoring, and saves and loads the results.

    visualizing.py has the make_heatmap function, which produces and saves the heatmap with customized names according to deck size, scoring method, and seed.

    run.py contains the run_project_penney function, which runs the whole process with input of deck size, number of decks, and seed. It also contains the append function, which adds new decks after the initial game is finished.

Figures are saved in the figures folder in both pdf and png format, while deck data and results are saved in the data folder.
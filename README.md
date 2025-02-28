Project Penney

This code is intended to run simulations of Penney's Game using generated card decks, then scoring those games using the tricks method while saving both the generated shuffled decks and the game results. Lastly, a heatmap will be created using this date in order to find the optimal choices for Player 2 in response to Player 1's selection.

Everything you need will be in the "important_stuff" folder:

    datagen.py contains functions involved in generating data

    processing.py contains the functions that calculate scoring, process the data, etc.

    visualizing.py has the function to produce the heatmap

    main.py has the function to run the whole process!

I've had some annoying issues importing pandas and seaborn on VSCode and Github so I honestly have no idea what's going on there, but the code works perfectly fine on Jupyterhub so hopefully it should be fine.

Also, some of the code is admittedly rather inefficient; I'd recommend against simulating a massive number of decks unless you want the code running for a while. The stuff in the data folder holds the results from running 100,000 decks and the files already seem rather large.
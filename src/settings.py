# Stockfish eval towards the user needed for the line to be considered (In Centipawn Loss)
WINNING_THRESH = 200
# Percentage of the games so you account for low total games || BUT ALSO HAVE TO FIGURE OUT HOW TO DO THIS FOR THE LINE BC MAYBE THEY DONT PLAY THE LINE OFTEN?
FREQUENCY_PLAYED = 10
# How highly rated the opponent has to be compared to the player (% of highest rating?)
OPPONENT_THRESH = 90
# How much depth stockfish needs to analyze (lines deep)
COMPUTER_DEPTH = 10
# How long the computer can think (sec)
COMPUTER_TIME = 0.05
# How many moves deep to analyze
MOVE_DEPTH = 8
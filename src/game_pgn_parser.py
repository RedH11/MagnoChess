import chess.pgn
import chess.engine
from sys import platform
import os
from src import settings
import json
from difflib import SequenceMatcher

# Compares how similar two strings are and returns a ratio score
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Parses through the pgn of the user and retrieves the important information
class GamesParser:

    # Need to implement a system for efficient tracking of they they play it vs against it (prob just split the analysis)
    # into when they play as black vs. as white

    # A map of the name of the opening the user has played (and played against) and how many times they've played with it
    __openings_played = {}

    # With the pgn and the player name, parses the pgn and passes it to functions to get relevant info
    def __init__(self, games_file, player_name):

        # Gets the stockfish engine for analysis (different file for mac vs windows)
        engine = self.get_engine()  # Get's the engine based on the OS (windows/mac)

        # Arrays of the chess games as pgn text form and as ChessGame classes
        all_games_pgn = [""]
        all_chess_games = []

        # Opens the pgn
        with open(games_file) as png_info:

            cur_game = ""
            # Goes line by line in the pgn, splitting each game into the all_games_pgn array
            for line in png_info:
                if (line == "\n" and last_line == "\n"):
                    # Sections off an individual game (separated by two lines in the pgn)
                    all_games_pgn.append(cur_game)
                    cur_game = ""

                cur_game += line
                last_line = line

        # Removes the blank first part of the pgn
        all_games_pgn.pop(0)  # Removes the empty first game

        # Get the information for all the ECO codes
        eco_info = json.loads(open(os.getcwd() + "/src/resources/eco_names.json").read())

        # Put all chess games into the array by putting them in a temporary pgn file then making them the ChessGame class
        for game_pgn in all_games_pgn:
            with open("cur_game.pgn", "w") as cur_file:
                cur_file.write(game_pgn)
                cur_file.close()
            all_chess_games.append(ChessGame(open("cur_game.pgn"), player_name, engine, eco_info))

        # Finds the openings the user loses the most as and against
        self.find_worst_openings(all_chess_games)
        # Finds the worst moves the user makes commonly
        self.find_worst_moves(all_chess_games)

        # How many of each opening was played
        print(self.__openings_played)

    def find_worst_openings(self, all_chess_games):
        for game in all_chess_games:
            opening, result = game.get_opening_and_result()

            if self.__openings_played.keys().__contains__(opening):
                self.__openings_played[opening] += 1  # Add one to an existing opening
            else:
                self.__openings_played[opening] = 1  # Make a new opening and set the amount played to one

        # Sort the dictionary by the most played openings
        self.__openings_played = dict(sorted(self.__openings_played.items(), key= lambda item: item[1], reverse= True))

    def find_worst_moves(self, all_games):
        return ""


    def get_engine(self):
        if platform == "darwin":
            # OSX
            return chess.engine.SimpleEngine.popen_uci(os.getcwd() + "/src/resources/stockfish-10-64")

        elif platform == "win32":
            # Windows
            return chess.engine.SimpleEngine.popen_uci(os.getcwd() + "/src/resources/stockfish_10_x64.exe")


class ChessGame:
    __result = 0  # 1 - Win | 0 - Loss
    __game_type = ""  # Classical, Rapid, Blitz, Bullet
    __moves = ""
    __player_color = 0  # 1 - White | 0 - Black
    __opening_code = ""
    __opening_variation = ""
    __opening_name = ""

    def __init__(self, game_pgn_path, player_name, engine, eco_info):
       # Reads the text png of the game
       game_info = chess.pgn.read_game(game_pgn_path)
       self.__player_color = int(game_info.headers["White"] == player_name)
       self.__result = (int(game_info.headers["Result"][0]) - self.__player_color) # Gets the first number in the string
       self.__opening_code = game_info.headers["ECO"]
       self.__moves = str(game_info.mainline_moves())
       self.__opening_name = self.get_general_opening_name(self.__opening_code, eco_info)
       print(self.__opening_name)
       self.__opening_variation = self.get_opening_variation_and_moves(eco_info)
       self.__opening_variation = self.get_opening_variation_and_moves(eco_info)
       #self.analyze_game(game_info, engine)

    def analyze_game(self, game_info, engine):
        board = game_info.board()

        move_counter = 0
        move_limit = settings.MOVE_DEPTH

        for move in game_info.mainline_moves():
            board.push(move)
            move_counter += 1
            info = engine.analyse(board, chess.engine.Limit(time=0.1, depth=10))
            score = int(str(info["score"].relative))

            # Display when the game imbalance is greater than +2
            if (abs(score) >= 300):
                print("Score:", info["score"], f"After: {board.piece_at(move.to_square)}{move}", "On move:", move_counter)

            # Only check as many moves deep as the MOVE_DEPTH
            if (move_counter >= move_limit):
                break

    # Get the specific opening variation and moves
    def get_opening_variation_and_moves(self, eco_info):

        # Get all opening variations for the game opening from the ECO code
        opening_options= []
        opening_options = [opening for opening in eco_info if opening['eco'] == self.__opening_code]

        opening_name = ""
        opening_moves = ""
        highest_similarity = 0.0

        # Finds the opening that has moves most similar to the game moves
        for opening in opening_options:
            if self.__moves.__contains__(opening['moves']):
                similarity_val = similar(opening['moves'], self.__moves)
                if similarity_val > highest_similarity:
                    opening_name = opening['name']
                    opening_moves = opening['moves']
                    highest_similarity = similarity_val

        return opening_name, opening_moves

    # The the unspecific name of the opening (no variation)
    def get_general_opening_name(self, eco_code, eco_info):
        for opening in eco_info:
            if opening['eco'] == self.__opening_code:
                # Remove everything after the colon so it's not shown as a variation
                return opening['name'].split(":", 1)[0]



    def get_opening_and_result(self):
        return self.__opening_name, self.__result
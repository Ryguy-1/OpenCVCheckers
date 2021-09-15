import numpy as np


class GenerateMoves:

    # L ~ L ~ L ~ L ~
    # ~ L ~ L ~ L ~ L
    # L ~ L ~ L ~ L ~
    # ~ ~ ~ ~ ~ ~ ~ ~
    # ~ ~ ~ ~ ~ ~ ~ ~
    # ~ C ~ C ~ C ~ C
    # C ~ C ~ C ~ C ~
    # ~ C ~ C ~ C ~ C

    algebraic_notation = [  # This is reversed because this is how the camera reads the board ¯\_(ツ)_/¯
            ["h8", "g8", "f8", "e8", "d8", "c8", "b8", "a8"],
            ["h7", "g7", "f7", "e7", "d7", "c7", "b7", "a7"],
            ["h6", "g6", "f6", "e6", "d6", "c6", "b6", "a6"],
            ["h5", "g5", "f5", "e5", "d5", "c5", "b5", "a5"],
            ["h4", "g4", "f4", "e4", "d4", "c4", "b4", "a4"],
            ["h3", "g3", "f3", "e3", "d3", "c3", "b3", "a3"],
            ["h2", "g2", "f2", "e2", "d2", "c2", "b2", "a2"],
            ["h1", "g1", "f1", "e1", "d1", "c1", "b1", "a1"]]

    reference_bitboard_array = [] # Array of 64 bitboards, each one with a single 1 populated (left to right)

    # These are switched from the algebraic notation array, just because the array is mirrored (same idea though)
    # Represents the Left Column In Binary
    a_file = int("1000000010000000100000001000000010000000100000001000000010000000", 2)
    b_file = int("0100000001000000010000000100000001000000010000000100000001000000", 2)
    # Represents the Right Column In Binary
    g_file = int("0000001000000010000000100000001000000010000000100000001000000010", 2)
    h_file = int("0000000100000001000000010000000100000001000000010000000100000001", 2)
    # Length Compare (64 bits)
    print(len("0000000000000000000000000000000000000000000000000000000000000000"))

    def __init__(self):
        if len(self.reference_bitboard_array) == 0:
            self.populate_reference_array()
        pass

    # You can only attack/move on a diagonal
    # INT HAS NO MAX SIZE IN PYTHON 3

    # Takes a String Board (As received from the board viewer) and returns a list of good moves, in order from best
    # To Worst
    def analyze_read_bord(self, string_board, casing):

        # Holds a string of 1 if piece and 0 if not piece
        cap_string = ""
        # The bitboard that the string gets converted into
        cap_bitboard = 0
        lc_string = ""
        lc_bitboard = 0

        # Convert Board to Bitboard Strings
        for row in string_board:
            for char in row:
                if char == "C":
                    cap_string += "1"
                    lc_string += "0"
                elif char == "L":
                    cap_string += "0"
                    lc_string += "1"
                else:
                    cap_string += "0"
                    lc_string += "0"

        # Convert Strings to Ints (bitboards)
        cap_bitboard = int(cap_string, 2)
        lc_bitboard = int(lc_string, 2)

        # Initialize Board StartPos
        start_pos = Position([cap_bitboard, lc_bitboard], casing)
        print(f'Eval: {start_pos.get_evaluation()}')
        print(self.get_move_list_algebraic(start_pos))

    # Give it a position, and it returns all of the potential moves in algebraic notation for the side up
    # (side up encoded in the position object)
    def get_move_list_algebraic(self, position):
        if position.to_move == "C":
            capital_bitboards = self.split_bitboard(position.current_board[0])
            for bitboard_index in range(len(capital_bitboards)):
                # Turns the 1d array into a 2d array, the second index being the place it can move to in bitboard
                capital_bitboards[bitboard_index] = [capital_bitboards[bitboard_index]]
                capital_bitboards[bitboard_index].append(self.find_moves(capital_bitboards[bitboard_index][0], position))

            from_to_moves = []
            # Gets the squares from and to in algebraic notation
            for combo in capital_bitboards:
                # Record the From Square Algebraically
                from_square = self.get_algebraic_notation_from_single_bitboard(combo[0])
                # Get Array of all All the Bitboard To Squares for Each From Square
                to_square_bitboards = self.split_bitboard(combo[1])
                # Record 2 squares algebraically as they are found
                to_squares = []
                # Iterate over the to bitboards
                for i in range(len(to_square_bitboards)):
                    # Append the algebraic notation as found
                    to_squares.append(self.get_algebraic_notation_from_single_bitboard(to_square_bitboards[i]))
                # Add to from_to_moves the sequence in full algebraic notation
                for to_square in to_squares:
                    from_to_moves.append(from_square + to_square)
            return from_to_moves
        else:  # position.to_move == "L":
            lower_case_bitboards = self.split_bitboard(position.current_board[1])
            for bitboard_index in range(len(lower_case_bitboards)):
                # Turns the 1d array into a 2d array, the second index being the place it can move to in bitboard
                lower_case_bitboards[bitboard_index] = [lower_case_bitboards[bitboard_index]]
                lower_case_bitboards[bitboard_index].append(
                    self.find_moves(lower_case_bitboards[bitboard_index][0], position))

            from_to_moves = []
            # Gets the squares from and to in algebraic notation
            for combo in lower_case_bitboards:
                # Record the From Square Algebraically
                from_square = self.get_algebraic_notation_from_single_bitboard(combo[0])
                # Get Array of all All the Bitboard To Squares for Each From Square
                to_square_bitboards = self.split_bitboard(combo[1])
                # Record 2 squares algebraically as they are found
                to_squares = []
                # Iterate over the to bitboards
                for i in range(len(to_square_bitboards)):
                    # Append the algebraic notation as found
                    to_squares.append(self.get_algebraic_notation_from_single_bitboard(to_square_bitboards[i]))
                # Add to from_to_moves the sequence in full algebraic notation
                for to_square in to_squares:
                    from_to_moves.append(from_square + to_square)
            return from_to_moves

    # Put in a Position object, encoded in which is a string for who's to move, and it returns a bitboard of all
    # the squares that can be moved to
    def find_moves(self, this_piece, position):
        # Array to be returned of moves in a single bitboard
        possible_moves_return = []

        cap_bitboard = position.current_board[0]
        lc_bitboard = position.current_board[1]

        if position.to_move == 'C':
            # Get Diagonal Bitboard (Left)
            left_bitboard = ((this_piece << 9) & ~self.h_file & ~cap_bitboard)  # including lc pieces
            # Get Diagonal Bitboard (Right)
            right_bitboard = ((this_piece << 7) & ~self.a_file & ~cap_bitboard)  # including lc pieces
            # Combined Right and Left (Excluding LC Pieces from Calculation)
            move_without_skip_including_lc_pieces = left_bitboard | right_bitboard
            # Find the Potential Moves without skipping (1 move ahead) Now including LC Calculation
            move_without_skip = move_without_skip_including_lc_pieces & ~lc_bitboard
            # Find LC Pieces Which are in attacking range on the next square diagonally (1 square attacking range)
            lc_pieces_directly_ahead = move_without_skip_including_lc_pieces & lc_bitboard
            # Shift the LC pieces which are 1 ahead and find their attacking places. If these attacking places are
            # another piece, this move isn't legal. If it's empty, then this is a valid move as well for a skip.
            # Last two conditions make sure it's a legal move (double diagonal from a piece)
            # and ~self.g_file/~self.b_file for specific edge case
            lc_pieces_shifted_legal = (((lc_pieces_directly_ahead << 9) & ~self.h_file & ~cap_bitboard & ~lc_bitboard & ~self.g_file) |\
                                      ((lc_pieces_directly_ahead << 7) & ~self.a_file & ~cap_bitboard & ~lc_bitboard) & ~self.b_file) &\
                            (((this_piece << 18) & ~self.g_file & ~self.h_file & ~cap_bitboard & ~lc_bitboard) |
                            ((this_piece << 14) & ~self.a_file & ~self.b_file & ~cap_bitboard & ~lc_bitboard))
            # Add together all moves without skips and skip moves into one
            all_moves = move_without_skip | lc_pieces_shifted_legal
            return all_moves

        else:  # casing == 'L':
            # Get Diagonal Bitboard (Left)
            left_bitboard = ((this_piece >> 9) & ~self.a_file & ~lc_bitboard)  # including cap pieces
            # Get Diagonal Bitboard (Right)
            right_bitboard = ((this_piece >> 7) & ~self.h_file & ~lc_bitboard)  # including cap pieces
            # Combined Right and Left (Excluding Cap Pieces from Calculation)
            move_without_skip_including_cap_pieces = left_bitboard | right_bitboard
            # Find the Potential Moves without skipping (1 move ahead) Now including Cap Calculation
            move_without_skip = move_without_skip_including_cap_pieces & ~cap_bitboard
            # Find Cap Pieces Which are in attacking range on the next square diagonally (1 square attacking range)
            cap_pieces_directly_ahead = move_without_skip_including_cap_pieces & cap_bitboard
            # Shift the Cap pieces which are 1 ahead and find their attacking places. If these attacking places are
            # another piece, this move isn't legal. If it's empty, then this is a valid move as well for a skip.
            # Last two conditions make sure it's a legal move (double diagonal from a piece)
            # and ~self.g_file/~self.b_file for specific edge case
            cap_pieces_shifted_legal = (((cap_pieces_directly_ahead >> 9) & ~self.a_file & ~lc_bitboard & ~cap_bitboard & ~self.b_file) |\
                                      ((cap_pieces_directly_ahead >> 7) & ~self.h_file & ~lc_bitboard & ~cap_bitboard) & ~self.g_file) &\
                            (((this_piece >> 18) & ~self.a_file & ~self.b_file & ~lc_bitboard & ~cap_bitboard) |
                            ((this_piece >> 14) & ~self.g_file & ~self.h_file & ~lc_bitboard & ~cap_bitboard))
            # Add together all moves without skips and skip moves into one
            all_moves = move_without_skip | cap_pieces_shifted_legal
            return all_moves

    # Gets a reference array to assist in separating bits from the bitboard array of a position
    # Each index is bit shifted 1 to the right to create an array of 64 bitboards
    # We can then use these and and operators to split the bitboard into each individual piece
    def populate_reference_array(self):
        starting = int("1000000000000000000000000000000000000000000000000000000000000000", 2)
        returning_array = []
        for i in range(64):
            returning_array.append(starting)
            starting = starting >> 1
        self.reference_bitboard_array = returning_array

    # Takes a bitboard and returns an array of bitboards, each one with a single 1 populated for a single checker
    def split_bitboard(self, bitboard):
        returned_array = []
        for ref_board in self.reference_bitboard_array:
            if ref_board & bitboard > 0:
                returned_array.append(ref_board)
        return returned_array

    # Input: bitboard with a single 1 (single piece represented) and returns the string with algebraic notation
    def get_algebraic_notation_from_single_bitboard(self, bitboard):
        # Gets index of the bit from bitboard
        try:
            index_of_bit = format(bitboard, '064b').index("1")
        except:  # if no 1 is found
            return ""
        # Going backwards in bitboard (top left to bottom right) (same orientation as algebraic notation array)
        counter = 0
        # Loop through algebraic notation
        for row in self.algebraic_notation:
            for square in row:
                if counter == index_of_bit:
                    return square
                counter += 1

    def print_bitboard(self, bitboard):
        string_bitboard = format(bitboard, '064b')
        for bit_idx in range(len(string_bitboard)):
            if bit_idx % 8 == 0 and bit_idx != 0:
                print()
            print(string_bitboard[bit_idx], end=' ')


# Keeps track of board position
class Position:

    move_generator = GenerateMoves()

    def __init__(self, bitboard, to_move):
        self.current_board = bitboard
        self.to_move = to_move

    # For now just returns the sum of pieces
    def get_evaluation(self):
        # Gets the total amount of capital pieces in its bitboard
        total_cap = len(self.move_generator.split_bitboard(self.current_board[0]))
        # Gets the total amount of lower case pieces in its bitboard
        total_lc = len(self.move_generator.split_bitboard((self.current_board[1])))

        # Checks for game won and returns a value accordingly
        if total_cap == 0:
            return -10000000
        elif total_lc == 0:
            return 10000000

        # Otherwise, return the point differential (cap = +, lc = -)
        return total_cap - total_lc


class Minimax:

    # Values that won't be reached under current evaluation method
    max = 10000000
    min = -10000000

    # Uses Alpha Beta Pruned Minimax Algorithm to find best move in a certain situation
    # (isMaximizingPlayer from position!!)
    def minimax(self, pos, depth, alpha, beta):

        # Reached Leaf Node (Game is Over)
        if depth == 0:
            return pos

        # If isMaximizingPlayer
        if pos.to_move == "C":
            best_value = self.min
            least_moves = self.max
            best_position = None
            # possible_moves =

import numpy as np

# Assumptions / Rules:
# - If a skip is longer than another skip, only consider the longer skip.
# - If a skip is available, you have to take it (rule of the game)

# Bitboards: https://en.wikipedia.org/wiki/Bitboard


# Purpose: Takes a String Board (As received from the board viewer) and returns next best move
# Input: Board Representation (From Board Viewer), "C" or "L" for next move
def analyze_read_bord(string_board, casing):

    # Strings for locations of "C" and "L" in binary
    cap_string = ""
    lc_string = ""

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
    # print(GenerateMoves().get_moves_skipping(start_pos, int("0000000000000000000000000000000000000000010000000000000000000000", 2), []))


    # print(GenerateMoves().get_move_list_algebraic(start_pos))


    # New Minimax Object
    minimax = Minimax()
    result = minimax.minimax(start_pos, 10, Minimax.min, Minimax.max).moves_to_current
    print(f'Predicted 10 Moves Ahead: {result}')
    print(f'Searched {minimax.nodes_searched} plausible nodes')
    # Return Next Best Move
    return result[0]


# Purpose: Encapsulates Member Variables and Methods Needed to Generate a Move Sequence
class GenerateMoves:

    # Example of a Board Representation from BoardViewer
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

    # Used for Splitting Bitboards into Multiple
    reference_bitboard_array = []  # Array of 64 bitboards, each one with a single 1 populated (left to right)

    # These are switched from the algebraic notation array, just because the array is mirrored (same idea though)
    # Left Column In Binary
    a_file = int("1000000010000000100000001000000010000000100000001000000010000000", 2)
    # Second to Left Column in Binary
    b_file = int("0100000001000000010000000100000001000000010000000100000001000000", 2)
    # Right Column In Binary
    g_file = int("0000001000000010000000100000001000000010000000100000001000000010", 2)
    # Second to Right Column in Binary
    h_file = int("0000000100000001000000010000000100000001000000010000000100000001", 2)

    # Rank 8 in Binary
    rank_8 = int("1111111100000000000000000000000000000000000000000000000000000000", 2)
    # Rank 1 in Binary
    rank_1 = int("0000000000000000000000000000000000000000000000000000000011111111", 2)

    # Length Compare (64 bits)
    print(len("0000000000000000000000000000000000000000000000000000000000000000"))

    # Purpose: Initialize Reference Array
    def __init__(self):
        # If Static Reference Bitboard Array Hasn't been populated, populate it
        if len(self.reference_bitboard_array) == 0:
            self.populate_reference_array()

    # Purpose: Given Position object, return all of the potential moves in algebraic notation for the side to move
    # Input: Position Object with all necessary data encapsulated
    # Output: Array of all Possible Moves from that position
    def get_move_list_algebraic(self, position):

        if position.to_move == "C":
            capital_bitboards = self.split_bitboard(position.current_board[0])
            # Array that contains [(start position)[0] and 1 to 2 arrays at [1] and [2] that have bitboard lists]
            bitboard_move_list = []
            # List to keep track of only skips
            skip_list = []
            # For each individual piece
            for bitboard_index in range(len(capital_bitboards)):
                (left_bitboard, left_was_skip, right_bitboard, right_was_skip) = self.find_moves_regular(capital_bitboards[bitboard_index], position)
                if left_was_skip or right_was_skip:
                    # Looks like this [[move1, move2], [move1], [move1, move2, move3]]
                    trail_array = self.get_moves_skipping(position, capital_bitboards[bitboard_index], [])
                    trail_array = self.extract_array_format(trail_array)
                    # Use the largest -> rule of thumb assumption that's almost always true.
                    longest_skip = []
                    skip_arr_temp = []
                    for move in trail_array:
                        if len(move) > len(longest_skip):
                            longest_skip = move
                    for move in trail_array:
                        if len(move) == len(longest_skip):
                            skip_arr_temp.append(move)
                    # Append skip moves to the skip list
                    skip_list.append(skip_arr_temp)
                # Fill in the non skips
                if not left_was_skip and left_bitboard != 0:
                    from_string = self.get_algebraic_notation_from_single_bitboard(capital_bitboards[bitboard_index])
                    to_string = self.get_algebraic_notation_from_single_bitboard(left_bitboard)
                    if from_string != "" and to_string != "":
                        bitboard_move_list.append(from_string+to_string)
                if not right_was_skip and right_bitboard != 0:
                    from_string = self.get_algebraic_notation_from_single_bitboard(capital_bitboards[bitboard_index])
                    to_string = self.get_algebraic_notation_from_single_bitboard(right_bitboard)
                    if from_string != "" and to_string != "":
                        bitboard_move_list.append(from_string+to_string)
            # Mandate skips if available
            if len(skip_list) > 0:
                bitboard_move_list = self.extract_array_format(skip_list)
            else:
                bitboard_move_list = self.extract_array_format(bitboard_move_list)
            return bitboard_move_list

        else:  # position.to_move == "L"
            lower_case_bitboards = self.split_bitboard(position.current_board[1])

            # Array that contains [(start position)[0] and 1 to 2 arrays at [1] and [2] that have bitboard lists]
            bitboard_move_list = []
            # List to keep track of only skips
            skip_list = []
            # For each individual piece
            for bitboard_index in range(len(lower_case_bitboards)):
                (left_bitboard, left_was_skip, right_bitboard, right_was_skip) = self.find_moves_regular(
                    lower_case_bitboards[bitboard_index], position)

                if left_was_skip or right_was_skip:
                    # Looks like this [[move1, move2], [move1], [move1, move2, move3]]
                    trail_array = self.get_moves_skipping(position, lower_case_bitboards[bitboard_index], [])
                    trail_array = self.extract_array_format(trail_array)
                    # Use the largest -> rule of thumb assumption that's almost always true.
                    longest_skip = []
                    skip_arr_temp = []
                    for move in trail_array:
                        if len(move) > len(longest_skip):
                            longest_skip = move
                    for move in trail_array:
                        if len(move) == len(longest_skip):
                            skip_arr_temp.append(move)
                    # Append skip moves to the skip list
                    skip_list.append(skip_arr_temp)
                # Fill in the non skips
                if not left_was_skip and left_bitboard != 0:
                    from_string = self.get_algebraic_notation_from_single_bitboard(lower_case_bitboards[bitboard_index])
                    to_string = self.get_algebraic_notation_from_single_bitboard(left_bitboard)
                    if from_string != "" and to_string != "":
                        bitboard_move_list.append(from_string+to_string)
                if not right_was_skip and right_bitboard != 0:
                    from_string = self.get_algebraic_notation_from_single_bitboard(lower_case_bitboards[bitboard_index])
                    to_string = self.get_algebraic_notation_from_single_bitboard(right_bitboard)
                    if from_string != "" and to_string != "":
                        bitboard_move_list.append(from_string+to_string)
            # Mandate skips if available
            if len(skip_list) > 0:
                bitboard_move_list = self.extract_array_format(skip_list)
            else:
                bitboard_move_list = self.extract_array_format(bitboard_move_list)
            return bitboard_move_list

    # Purpose: Formats Array Nicely from get_moves_skipping
    # Input: get_moves_skipping array
    # Output: Cleanly formatted get_moves_skipping_array
    def extract_array_format(self, array):

        # Check if an object contains a list
        def list_contains_array(array2):
            if not isinstance(array2, list):
                return False
            for variable in array2:
                if isinstance(variable, list):
                    return True
            return False
        # Initialize returned array
        returned_array = []

        # Recursively cycle through values
        def value_cycle(arr):
            for value in arr:
                # if the object doesn't contain another list
                if not list_contains_array(value):
                    # If it is a string append it as a list
                    if isinstance(value, str):
                        returned_array.append([value])
                    # Otherwise, append it as the list it is
                    else:
                        returned_array.append(value)

                elif not list_contains_array(value[:2]):
                    returned_array.append(value[:2])
                    if len(value) > 2:
                        value_cycle(value[2:3])
                else:
                    value_cycle(value)
        value_cycle(array)
        return returned_array

    # Purpose: Recursively find All Skip Combinations
    # Input: Start Position, Start Piece (in bitboard representation), paths to this point list
    # Output: Possible Paths after that Point
    def get_moves_skipping(self, start_position, node_piece_bitboard, paths):
        # print(f'Node piece board{node_piece_bitboard}')
        # Base Case if there are no more skipping moves left or right
        (left_bitboard, left_was_skip, right_bitboard, right_was_skip) = self.find_moves_regular(node_piece_bitboard, start_position)
        # Array returned each call
        returned_arr_left = []
        returned_arr_right = []
        # If left has a skip opportunity
        if left_was_skip:
            # Make a copy of the position
            position_copy = start_position.get_position_copy()
            # Get the move strings for that position
            from_string = self.get_algebraic_notation_from_single_bitboard(node_piece_bitboard)
            to_string = self.get_algebraic_notation_from_single_bitboard(left_bitboard)
            # Make the move in the copied position
            if from_string != "" and to_string != "":
                position_copy.make_move(from_string+to_string)
            # Undo Move Changes -> Same person is moving twice
            if position_copy.to_move == "C":
                position_copy.to_move = "L"
            else:  # position_copy.to_move == "L":
                position_copy.to_move = "C"

            # Copy over moves from paths into the returned array (create deep copy)
            for move in paths:
                returned_arr_left.append(move)
            # Append newly found move first
            if from_string != "" and to_string != "":
                returned_arr_left.append(from_string+to_string)
            # Recursive call to get possibilities from this new place
                new_arr = self.get_moves_skipping(position_copy, left_bitboard, returned_arr_left)
            # If there are any new possibilities, add them
                if len(new_arr) != 0:
                    returned_arr_left.append(new_arr)

        # Comments are the same
        if right_was_skip:
            position_copy = start_position.get_position_copy()
            from_string = self.get_algebraic_notation_from_single_bitboard(node_piece_bitboard)
            to_string = self.get_algebraic_notation_from_single_bitboard(right_bitboard)
            if from_string != "" and to_string != "":
                position_copy.make_move(from_string+to_string)
            if position_copy.to_move == "C":
                position_copy.to_move = "L"
            else:  # position_copy.to_move == "L":
                position_copy.to_move = "C"
            for move in paths:
                returned_arr_right.append(move)
            if from_string != "" and to_string != "":
                returned_arr_right.append(from_string+to_string)
                new_arr = self.get_moves_skipping(position_copy, right_bitboard, returned_arr_right)
                if len(new_arr) != 0:
                    returned_arr_right.append(new_arr)

        # Combine left and right arrays (if you have skip right AND left, this rids of ambiguity)
        total_arr = []
        # for value in returned_arr_right:
        #     total_arr.append(value)
        # for value in returned_arr_left:
        #     total_arr.append(value)
        if len(returned_arr_left) > 0:
            total_arr.append(returned_arr_left)
        if len(returned_arr_right) > 0:
            total_arr.append(returned_arr_right)
        # Base case / general return function= neither path has another skip
        return total_arr

    # Purpose: From Position Object, find possible moves of a certain piece.
    # Input: Piece Bitboard, Position object
    # Output: left_move bitboard, left_move_was_skip, right_move bitboard, right_move_was_skip
    def find_moves_regular(self, this_piece, position):
        cap_bitboard = position.current_board[0]
        lc_bitboard = position.current_board[1]

        if position.to_move == 'C':

            # Only for capital -> Make sure no overflow -> 0's don't automatically get cut off when go about 64 bits
            if this_piece & int("1111111100000000000000000000000000000000000000000000000000000000", 2) > 0:
                return 0, False, 0, False

            # Get Diagonal Bitboard (Left)
            left_bitboard = ((this_piece << 9) & ~self.h_file & ~cap_bitboard)  # including lc pieces
            # Get Diagonal Bitboard (Right)
            right_bitboard = ((this_piece << 7) & ~self.a_file & ~cap_bitboard)  # including lc pieces

            # Moves without skips bitboards
            move_without_skip_left = left_bitboard & ~lc_bitboard
            move_without_skip_right = right_bitboard & ~lc_bitboard

            # Pieces next move on each diagonal
            lc_pieces_directly_ahead_left = left_bitboard & lc_bitboard
            lc_pieces_directly_ahead_right = right_bitboard & lc_bitboard

            # Get squares you land on if skip
            lc_pieces_shifted_legal_left = ((lc_pieces_directly_ahead_left << 9) & ~self.h_file & ~cap_bitboard & ~lc_bitboard & ~self.g_file) &\
                            ((this_piece << 18) & ~self.g_file & ~self.h_file & ~cap_bitboard & ~lc_bitboard)
            lc_pieces_shifted_legal_right = ((lc_pieces_directly_ahead_right << 7) & ~self.a_file & ~cap_bitboard & ~lc_bitboard & ~self.b_file) &\
                            ((this_piece << 14) & ~self.a_file & ~self.b_file & ~cap_bitboard & ~lc_bitboard)

            # Combine 1 move and skip moves together on each side and get boolean for if it was a skip
            left_move = move_without_skip_left | lc_pieces_shifted_legal_left
            left_move_was_skip = lc_pieces_shifted_legal_left > 0
            right_move = move_without_skip_right | lc_pieces_shifted_legal_right
            right_move_was_skip = lc_pieces_shifted_legal_right > 0

            # Check if went over (max can go over 2 rows past top)
            if left_move & ((self.rank_8 << 8) | (self.rank_8 << 16)) > 0:
                left_move = 0
                left_move_was_skip = False
            if right_move & ((self.rank_8 << 8) | (self.rank_8 << 16)) > 0:
                right_move = 0
                right_move_was_skip = False

            return left_move, left_move_was_skip, right_move, right_move_was_skip

        else:  # casing == 'L':
            # Get Diagonal Bitboard (Left)
            left_bitboard = ((this_piece >> 9) & ~self.a_file & ~lc_bitboard)  # including cap pieces
            # Get Diagonal Bitboard (Right)
            right_bitboard = ((this_piece >> 7) & ~self.h_file & ~lc_bitboard)  # including cap pieces

            # Moves without skips bitboards
            move_without_skip_left = left_bitboard & ~cap_bitboard
            move_without_skip_right = right_bitboard & ~cap_bitboard

            # Pieces next move on each diagonal
            cap_pieces_directly_ahead_left = left_bitboard & cap_bitboard
            cap_pieces_directly_ahead_right = right_bitboard & cap_bitboard

            # Get squares you land on if skip
            lc_pieces_shifted_legal_left = ((cap_pieces_directly_ahead_left >> 9) & ~self.a_file & ~lc_bitboard & ~cap_bitboard & ~self.b_file) &\
                            ((this_piece >> 18) & ~self.a_file & ~self.b_file & ~lc_bitboard & ~cap_bitboard)
            lc_pieces_shifted_legal_right = ((cap_pieces_directly_ahead_right >> 7) & ~self.h_file & ~lc_bitboard & ~cap_bitboard & ~self.g_file) &\
                            ((this_piece >> 14) & ~self.g_file & ~self.h_file & ~lc_bitboard & ~cap_bitboard)

            # Combine 1 move and skip moves together on each side and get boolean for if it was a skip
            left_move = move_without_skip_left | lc_pieces_shifted_legal_left
            left_move_was_skip = lc_pieces_shifted_legal_left > 0
            right_move = move_without_skip_right | lc_pieces_shifted_legal_right
            right_move_was_skip = lc_pieces_shifted_legal_right > 0

            return left_move, left_move_was_skip, right_move, right_move_was_skip

    # Purpose: Gets Array of len 64, each index is bit shifted over 1 to right (used in splitting bitboards)
    def populate_reference_array(self):
        starting = int("1000000000000000000000000000000000000000000000000000000000000000", 2)
        returning_array = []
        for i in range(64):
            returning_array.append(starting)
            starting = starting >> 1
        self.reference_bitboard_array = returning_array

    # Purpose: Takes a bitboard and returns an array of bitboards with 1 bit populated each
    def split_bitboard(self, bitboard):
        returned_array = []
        for ref_board in self.reference_bitboard_array:
            if ref_board & bitboard > 0:
                returned_array.append(ref_board)
        return returned_array

    # Input: bitboard with a single 1 (single piece represented)
    # Output: the string with algebraic notation
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

    # Purpose: Debugging print bitboard
    def print_bitboard(self, bitboard):
        string_bitboard = format(bitboard, '064b')
        for bit_idx in range(len(string_bitboard)):
            if bit_idx % 8 == 0 and bit_idx != 0:
                print()
            print(string_bitboard[bit_idx], end=' ')


# Keeps track of board position with all necessary data/action functions encapsulated
class Position:

    # Static Move Generator Object
    move_generator = GenerateMoves()

    # Input: Bitboard Array [capital, lower case], "C" or "L" for next to move
    def __init__(self, bitboard, to_move):
        self.current_board = bitboard
        self.to_move = to_move
        # Keeps Track of String of Moves to Current
        self.moves_to_current = []

    # Purpose: Assign a Number to How "Good" a Board is for each player -> (+ = good for C, - = good for L)
    def get_evaluation(self):
        # Gets the total amount of capital pieces in its bitboard
        total_cap = len(self.move_generator.split_bitboard(self.current_board[0]))
        # Gets the total amount of lower case pieces in its bitboard
        total_lc = len(self.move_generator.split_bitboard((self.current_board[1])))

        # Checks for game won and returns a value accordingly
        if total_cap == 0 or (self.move_generator.rank_1 & self.current_board[1] > 0):
            return -10000000
        if total_lc == 0 or (self.move_generator.rank_8 & self.current_board[0] > 0):
            return 10000000

        # Otherwise, return the point differential (cap = +, lc = -)
        return total_cap - total_lc

    # Add move to member variable moves_to_current
    def add_move_to_current(self, algebraic_move):
        self.moves_to_current.append(algebraic_move)

    # Purpose: Makes Move on Position Object
    # Input: Move in Algebraic Notation
    def make_move(self, algebraic_move):

        if algebraic_move == "" or len(algebraic_move) != 4:
            # print("TRIED TO MAKE ILLEGAL MOVE")
            return

        # Strings of moves separated
        from_algebraic = algebraic_move[:2]
        to_algebraic = algebraic_move[2:]

        # Create Strings in bits
        bitboard_string_from = ""
        bitboard_string_to = ""
        for row in self.move_generator.algebraic_notation:
            for move in row:
                if move == from_algebraic:
                    bitboard_string_from += "1"
                    bitboard_string_to += "0"
                elif move == to_algebraic:
                    bitboard_string_to += "1"
                    bitboard_string_from += "0"
                else:
                    bitboard_string_from += "0"
                    bitboard_string_to += "0"

        # Bitboards for to and from
        from_bitboard = int(bitboard_string_from, 2)
        to_bitboard = int(bitboard_string_to, 2)

        # Remove starting place and add in ending place
        if self.to_move == "C":
            self.current_board[0] = self.current_board[0] ^ from_bitboard
            self.current_board[0] = self.current_board[0] | to_bitboard
            # Skip Add Ins
            # If you are attacking on the left diagonal, remove the piece for lower case
            # that is << 9 from the from bitboard. Also check if there is a piece to remove (and clause)
            if to_bitboard == (from_bitboard << 18) and ((from_bitboard << 9) & self.current_board[1]) > 0:
                self.current_board[1] = self.current_board[1] ^ (from_bitboard << 9)
            elif to_bitboard == (from_bitboard << 14) and ((from_bitboard << 7) & self.current_board[1]) > 0:
                self.current_board[1] = self.current_board[1] ^ (from_bitboard << 7)

        else:  # self.to_move == "L"
            self.current_board[1] = self.current_board[1] ^ from_bitboard
            self.current_board[1] = self.current_board[1] | to_bitboard
            # Skip Add Ins
            # If you are attacking on the left diagonal, remove the piece for capital
            # that is >> 9/7 from the from bitboard. Also check if there is a piece to remove (and clause)
            if to_bitboard == (from_bitboard >> 18) and ((from_bitboard >> 9) & self.current_board[0]) > 0:
                self.current_board[0] = self.current_board[0] ^ (from_bitboard >> 9)
            elif to_bitboard == (from_bitboard >> 14) and ((from_bitboard >> 7) & self.current_board[0]) > 0:
                self.current_board[0] = self.current_board[0] ^ (from_bitboard >> 7)

        # Return opposite of capital / lower case
        if self.to_move == "C":
            self.to_move = "L"
        else:  # self.to_move == "L"
            self.to_move = "C"

    # Purpose: Return a copy object of the same position
    # Output: An Identical Position Object, but in no way Linked
    def get_position_copy(self):
        new_board = [self.current_board[0], self.current_board[1]]
        copy_pos = Position(new_board, self.to_move)
        copy_pos.moves_to_current = self.moves_to_current.copy()
        return copy_pos

    # Draw Position Object to Console
    def draw(self):
        # Format Bitboards as Strings
        string_bitboard_cap = format(self.current_board[0], '064b')
        string_bitboard_lc = format(self.current_board[1], '064b')
        # Print out Board
        for bit_idx in range(len(string_bitboard_cap)):
            if bit_idx % 8 == 0 and bit_idx != 0:
                print()
            if string_bitboard_cap[bit_idx] == '1':
                print("C", end=' ')
            elif string_bitboard_lc[bit_idx] == '1':
                print("L", end=' ')
            else:
                print("-", end=' ')


# Purpose: Main Move Logic Function. Uses Famous, yet simple, Minimax Algorithm
class Minimax:

    # Static move_generator object
    move_generator = GenerateMoves()

    # Values that won't be reached under current evaluation method
    max = 100000000000
    min = -100000000000

    # Purpose: Initialize nodes_searched to 0
    def __init__(self):
        self.nodes_searched = 0

    # Purpose: Implementation of Alpha Beta Pruned Minimax Algorithm to find best move sequence from a certain situation
    def minimax(self, pos, depth, alpha, beta):

        self.nodes_searched += 1

        # Reached Leaf Node (Game is Over)
        if depth == 0 or pos.get_evaluation() > 10000 or pos.get_evaluation() < -10000:
            return pos

        # If isMaximizingPlayer
        if pos.to_move == "C":
            best_value = self.min
            least_moves = self.max
            best_position = None
            possible_moves = self.move_generator.get_move_list_algebraic(pos)

            if len(possible_moves) == 0:
                return pos
            # print(possible_moves)
            # Get all possible moves
            for move_arr in possible_moves:
                # Get Position Copy Object (Child) (Including history)
                child_pos = pos.get_position_copy()
                # Make the Move in this child object
                for single_move in move_arr:
                    child_pos.make_move(single_move)
                    if child_pos.to_move == "L":
                        child_pos.to_move = "C"
                    else:  # child_pos.to_move == "C":
                        child_pos.to_move = "L"
                if child_pos.to_move == "L":
                    child_pos.to_move = "C"
                else:  # child_pos.to_move == "C":
                    child_pos.to_move = "L"

                # Add the move to moves to current
                child_pos.add_move_to_current(move_arr)
                # print(child_pos.moves_to_current)
                # Recursive Call To Minimax
                temp_position = self.minimax(child_pos, depth-1, alpha, beta)
                # Check if this position is better
                if temp_position.get_evaluation() > best_value:
                    # Set least moves equal to this better position found
                    least_moves = len(temp_position.moves_to_current)
                    # Set the best value equal to this new evaluation
                    best_value = temp_position.get_evaluation()
                    # Set best position equal to this temp position
                    best_position = temp_position
                # Check if position has same evaluation, but less moves
                elif temp_position.get_evaluation() == best_value and len(temp_position.moves_to_current) < least_moves:
                    # Set less moves equal to this new position
                    least_moves = len(temp_position.moves_to_current)
                    # Set best value equal to this new position's evaluation
                    best_value = temp_position.get_evaluation()
                    # Set the best position equal to the new position
                    best_position = temp_position

                # # Need to come back to understand alpha beta pruning
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            # Return the best position
            return best_position
        else:  # Lower Case
            # Best value
            best_value = self.max
            # least amount of moves
            least_moves = self.max
            # Best position initialized to none
            best_position = None
            # Find possible moves
            possible_moves = self.move_generator.get_move_list_algebraic(pos)

            # print(possible_moves)

            # print(f'Lower Case Possible Moves: {possible_moves}')
            # If possible moves are none, return position, leaf node
            if len(possible_moves) == 0:
                return pos

            # Get all possible moves
            for move_arr in possible_moves:
                # Get Position Copy Object (Child) (Including history)
                child_pos = pos.get_position_copy()
                # Make the Move in this child object
                for single_move in move_arr:
                    child_pos.make_move(single_move)
                    if child_pos.to_move == "C":
                        child_pos.to_move = "L"
                    else:  # child_pos.to_move == "L":
                        child_pos.to_move = "C"
                if child_pos.to_move == "C":
                    child_pos.to_move = "L"
                else:  # child_pos.to_move == "L":
                    child_pos.to_move = "C"
                # Add the move to moves to current

                # print(f'Move arr{move_arr}')
                child_pos.add_move_to_current(move_arr)
                # Recursive Call To Minimax
                temp_position = self.minimax(child_pos, depth - 1, alpha, beta)

                # Check if this position is better
                if temp_position.get_evaluation() < best_value:
                    # Update least moves
                    least_moves = len(temp_position.moves_to_current)
                    # Update best value
                    best_value = temp_position.get_evaluation()
                    # Update best position
                    best_position = temp_position
                # If same eval, but less moves to get there
                elif temp_position.get_evaluation() == best_value and len(temp_position.moves_to_current) < least_moves:
                    # Least moves update
                    least_moves = len(temp_position.moves_to_current)
                    # Update best value
                    best_value = temp_position.get_evaluation()
                    # Update best position
                    best_position = temp_position

                # Need to come back to understand alpha beta pruning
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            # Return the best position
            return best_position

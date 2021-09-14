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

    # Represents the Left Column In Binary
    a_file = int("1000000010000000100000001000000010000000100000001000000010000000", 2)
    # Represents the Right Column In Binary
    h_file = int("0000000100000001000000010000000100000001000000010000000100000001", 2)

    def __init__(self):
        # Length Compare (64 bits)
        print(len("0000000000000000000000000000000000000000000000000000000000000000"))
        pass

    # You can only attack/move on a diagonal
    # INT HAS NO MAX SIZE IN PYTHON 3
    def get_moves(self, string_board, casing):

        # Holds a string of 1 if piece and 0 if not piece
        cap_string = ""
        # The bitboard that the string gets converted into
        cap_bitboard = 0
        lc_string = ""
        lc_bitboard = 0

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

        cap_bitboard = int(cap_string, 2)
        lc_bitboard = int(lc_string, 2)

        possible_moves = []
        if casing == 'C':
            # Get Diagonal Bitboard (Left)
            left_bitboard = ((cap_bitboard << 9) & ~self.h_file & ~cap_bitboard & ~lc_bitboard)
            # Get Diagonal Bitboard (Right)
            right_bitboard = ((cap_bitboard << 7) & ~self.a_file & ~cap_bitboard & ~lc_bitboard)
        else:  # casing == 'L':
            # Get Diagonal Bitboard (Left)
            left_bitboard = ((cap_bitboard >> 7) & ~self.h_file & ~cap_bitboard & ~lc_bitboard)
            # Get Diagonal Bitboard (Right)
            right_bitboard = ((cap_bitboard >> 9) & ~self.a_file & ~cap_bitboard & ~lc_bitboard)



    def print_bitboard(self, bitboard):
        print(bin(bitboard))

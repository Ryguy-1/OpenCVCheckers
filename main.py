from BoardViewer import BoardViewer
from BoardAnalyzer import BoardAnalyzer
from GenerateMoves import analyze_read_bord
import numpy as np

# Ryland Checkers: A New Quicker Version of Checkers
# Goal: Get 1 Piece to the Other Side Before Your Opponent, OR Wipe Them From the Board
# First to do Either, wins. Good Luck (you'll need it).


def main():
    board_viewer = BoardViewer(1000, 1000)
    board_analyzer = BoardAnalyzer(board_viewer=board_viewer)
    # test_array = np.array([['L', '~', 'L', '~', 'L', '~', 'L', '~'],
    #                        ['~', 'L', '~', 'L', '~', 'L', '~', 'L'],
    #                        ['L', '~', 'L', '~', 'L', '~', 'L', '~'],
    #                        ['~', '~', '~', '~', '~', '~', '~', '~'],
    #                        ['~', '~', '~', '~', '~', '~', '~', '~'],
    #                        ['~', 'C', '~', 'C', '~', 'C', '~', 'C'],
    #                        ['C', '~', 'C', '~', 'C', '~', 'C', '~'],
    #                        ['~', 'C', '~', 'C', '~', 'C', '~', 'C'],
    #                        ])
    # test_array = np.array([['L', '~', 'L', '~', 'L', '~', 'L', '~'],
    #                        ['~', '~', '~', 'L', '~', 'L', '~', 'L'],
    #                        ['L', '~', 'L', '~', 'L', '~', 'L', '~'],
    #                        ['~', 'L', '~', 'C', '~', '~', '~', '~'],
    #                        ['C', '~', '~', '~', '~', '~', '~', '~'],
    #                        ['~', '~', '~', '~', '~', 'C', '~', 'C'],
    #                        ['C', '~', 'C', '~', 'C', '~', 'C', '~'],
    #                        ['~', 'C', '~', 'C', '~', 'C', '~', 'C'],
    #                        ])
    # test_array = np.array([['L', '~', 'L', '~', 'L', '~', 'L', '~'],
    #                        ['~', '~', '~', '~', '~', '~', '~', 'L'],
    #                        ['L', '~', 'L', '~', '~', '~', '~', '~'],
    #                        ['~', '~', '~', '~', '~', '~', '~', '~'],
    #                        ['C', '~', 'L', '~', 'C', '~', '~', '~'],
    #                        ['~', 'C', '~', 'C', '~', '~', '~', 'L'],
    #                        ['C', '~', '~', '~', 'C', '~', 'C', '~'],
    #                        ['~', '~', '~', '~', '~', 'C', '~', 'C'],
    #                        ])

    # print(analyze_read_bord(test_array, 'C'))


if __name__ == '__main__':
    main()

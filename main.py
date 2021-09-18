from BoardViewer import BoardViewer
from BoardAnalyzer import BoardAnalyzer
from GenerateMoves import analyze_read_bord
from GenerateMoves import Position
import cv2
import threading
import numpy as np


def main():
    board_viewer = BoardViewer()
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
    # test_array = np.array([['~', '~', '~', '~', '~', '~', '~', '~'],
    #                        ['~', '~', '~', '~', '~', '~', '~', '~'],
    #                        ['~', '~', 'L', '~', '~', '~', 'L', '~'],
    #                        ['~', '~', '~', '~', '~', '~', '~', '~'],
    #                        ['~', '~', 'L', '~', 'L', '~', '~', '~'],
    #                        ['~', '~', '~', 'C', '~', '~', '~', '~'],
    #                        ['~', '~', '~', '~', '~', '~', '~', '~'],
    #                        ['~', '~', '~', '~', '~', '~', '~', '~'],
    #                        ])
    # print(analyze_read_bord(test_array, 'C'))


if __name__ == '__main__':
    main()

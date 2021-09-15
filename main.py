from BoardViewer import BoardViewer
from GenerateMoves import GenerateMoves
from GenerateMoves import Position
import cv2
import threading
import numpy as np





def main():
    # board_viewer = BoardViewer()
    move_generator = GenerateMoves()
    test_array = np.array([['L', '~', 'L', '~', 'L', '~', 'L', '~'],
                           ['~', 'L', '~', 'L', '~', 'L', '~', 'L'],
                           ['L', '~', 'L', '~', 'L', '~', 'L', '~'],
                           ['~', 'C', '~', '~', '~', '~', '~', '~'],
                           ['~', '~', '~', '~', '~', '~', '~', '~'],
                           ['~', 'C', '~', 'C', '~', 'C', '~', 'C'],
                           ['C', '~', 'C', '~', 'C', '~', 'C', '~'],
                           ['~', 'C', '~', 'C', '~', 'C', '~', 'C'],
                           ])
    move_generator.analyze_read_bord(test_array, 'L')


if __name__ == '__main__':
    main()

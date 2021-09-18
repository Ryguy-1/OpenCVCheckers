import threading
import keyboard
import cv2
from GenerateMoves import analyze_read_bord
import numpy as np


class BoardAnalyzer:

    def __init__(self, board_viewer):
        self.board_viewer = board_viewer
        self.analyze_thread = threading.Thread(target=self.analyze_thread).start()

    # Whenever you press the space bar,
    def analyze_thread(self):
        while True:
            checking_keys = True
            key_pressed = ''
            while checking_keys:

                if keyboard.is_pressed('space'):
                    key_pressed = 'space'
                    checking_keys = False
                    break
                cv2.waitKey(1)

            if key_pressed == 'space':
                print()
                print()
                print("Current Board: ")
                board_to_use = self.board_viewer.board_representation.copy()
                self.board_viewer.print_board(board_to_use)
                print()
                print()
                correct_move = input("Correct Board (y/n): ")
                if correct_move != "y":
                    print("Adjust Settings / Try Again.")
                    continue
                moving = input("Suggest Move: 'a' for Side 1 and 'b' for Side 2:  ")
                if moving == 'a':
                    print("Searching For Best Move: ")
                    print(analyze_read_bord(board_to_use, 'C'))
                elif moving == 'b':
                    print("Searching For Best Move: ")
                    print(analyze_read_bord(board_to_use, 'L'))
                else:
                    print("Need to Select 'a' or 'b' for which side to suggest move for")


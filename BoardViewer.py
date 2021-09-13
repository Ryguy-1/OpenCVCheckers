import time
import numpy as np
from WebCamFeed import WebCamFeed
import cv2
import threading
import math


# Gets Checker Pieces from Feed and Map Them to a board array. ANGLE FROM SIDE OF BOARD HARDCODED FOR NOW.
class BoardViewer:

    def __init__(self, frame_width=1000, frame_height=1000):
        # WebCamFeed for each BoardViewer
        self.webcam_feed = WebCamFeed(frame_width, frame_height)
        self.contour_list = [[], []]  # 2d list with capital pieces in one list and lower case in the other
        # -> updated every frame (consistent though)
        self.board_representation = [] # [32] array with a 'c' for capital present and a 'l' for lower case present
        # Number for adaptive thresholding
        self.adaptive_threshold_num = 41  # was 111  ------>> VARIABLE 1 -> Has Slider :)
        # Reset Switch
        self.adaptive_threshold_num_start = self.adaptive_threshold_num
        # Minimum Area Considered as Piece
        self.contour_area_cutoff_min = 663  # --------->> VARIABLE 2 -> Has Slider :)
        # Maimum Area Considered as Piece
        self.contour_area_cutoff_max = 1011  # ---------->> Maybe_VARIABLE 3 -> Has Slider :)
        # Difference in Mean of HSV Values Considered 1 Color
        self.color_distinguish_threshold = 25
        # HSV Separator -> Change Accordingly
        self.hsv_1 = 74  # --------->> Maybe_VARIABLE 4 -> Has Slider :)
        # Gaussian Blur Number
        self.gaussian_blur = (13, 13)
        # Canny Edge Detection Lower, Upper
        self.canny_lower = 70; self.canny_upper = 90
        # Frame Delay (Must be >= 16)
        self.frame_delay = 16; self.frame_counter = 0
        # Row/Column Threshold
        self.row_col_threshold = 40
        # Hold Rank and File Location Information
        self.ranks_x = []
        self.files_y = []
        # Thread which takes info from the webcam feed and constantly updates contour and board information
        self.analyze_thread = threading.Thread(target=self.analyze_board).start()
        # Allows Changing Adaptive Threshold number from Command Prompt -> Not used in final version (testing)
        # self.threshold_resizer = threading.Thread(target=self.threshold_resizer).start()

    def adaptive_threshold_change(self, val):
        if val % 2 == 0:
            val += 1
            self.adaptive_threshold_num = val
            return
        self.adaptive_threshold_num = val

    def contour_area_cutoff_min_change(self, val):
        self.contour_area_cutoff_min = val

    def contour_area_cutoff_max_change(self, val):
        self.contour_area_cutoff_max = val

    def hsv_color_separator(self, val):
        self.hsv_1 = val

    def frame_delay_adjust(self, val):
        self.frame_delay = val

    def row_col_threshold_adjust(self, val):
        self.row_col_threshold = val

    def analyze_board(self):
        is_first_show = True  # Use For Initialization of Sliders
        # While webcam still running, analyze frames and update the internal mappings
        while self.webcam_feed.is_running:
            # If the current frame isn't empty (on initialization)
            if self.webcam_feed.current_frame.all() is not None:
                # Grab current frame from WebCamFeed
                image = self.webcam_feed.current_frame
                # Black and white
                grayscaled_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # Threshold -> Adaptive Threshold useful to help mitigate shadow of camera overhead
                try:
                    grayscaled_image = cv2.adaptiveThreshold(grayscaled_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                             cv2.THRESH_BINARY, self.adaptive_threshold_num, 0)
                except:
                    print("Must be an Odd Number")
                    self.adaptive_threshold_num = self.adaptive_threshold_num_start

                # Gaussian Blur
                grayscaled_image = cv2.GaussianBlur(grayscaled_image, self.gaussian_blur, 0)  # 11, 11 works well

                # Canny Edged Image (70, 90 works pretty well)
                canny_edged_image = cv2.Canny(grayscaled_image, self.canny_lower, self.canny_upper)
                # Find Contours and filter contours by area
                (contours, hierarchy) = cv2.findContours(canny_edged_image.copy(), cv2.RETR_TREE,
                                                         cv2.CHAIN_APPROX_SIMPLE)
                filtered_contours, filtered_hierarchy = self.filter_contours(contours, hierarchy)

                # Updates contour list -> once every 30 frames
                if len(filtered_contours) > 0 and self.frame_counter % 10 == 0:
                    self.update_contour_list(filtered_contours, image)
                    image = self.draw_labels(self.contour_list, image)
                    self.update_board_representation()
                    self.frame_counter = 0

                # Make copy of image (destructive)
                outline_image = image.copy()
                # Draw contours into image
                cv2.drawContours(outline_image, filtered_contours, -1, (0, 255, 0),
                                 1)  # -1 = draw all contours -> otherwise, it's the index

                outline_image = self.draw_x_y_lines(self.ranks_x, self.files_y, outline_image)
                # Show the image
                cv2.imshow(self.webcam_feed.frame_title, outline_image)
                if is_first_show:
                    cv2.createTrackbar('Adaptive Threshold', self.webcam_feed.frame_title, self.adaptive_threshold_num, 400,
                                       self.adaptive_threshold_change)
                    cv2.createTrackbar('Contour Area Cutoff Min', self.webcam_feed.frame_title, self.contour_area_cutoff_min, 1500,
                                       self.contour_area_cutoff_min_change)
                    cv2.createTrackbar('Contour Area Cutoff Max', self.webcam_feed.frame_title, self.contour_area_cutoff_max, 2000,
                                       self.contour_area_cutoff_max_change)
                    cv2.createTrackbar('HSV Color Separator', self.webcam_feed.frame_title, self.hsv_1, 300,
                                       self.hsv_color_separator)
                    cv2.createTrackbar('Frame Delay', self.webcam_feed.frame_title, self.frame_delay, 300,
                                       self.frame_delay_adjust)
                    # cv2.createTrackbar('Row/Col Threshold', self.webcam_feed.frame_title, self.row_col_threshold, 300,
                    #                    self.row_col_threshold_adjust)
                    (self.ranks_x, self.files_y) = self.get_x_y_lines()
                    is_first_show = False

                # Wait 10 ms in between frames
                cv2.waitKey(self.frame_delay)
                print(f'Adaptive Threshold is {self.adaptive_threshold_num}')

    # Filter Contours by Area (Closed Mandatory)
    def filter_contours(self, contours, hierarchy):
        # New Empty Lists for Contours and Hierarchy
        new_contours = []
        new_hierarchy = [[]]
        # Iterate through Contours
        for i in range(len(contours)):
            # If Contour Area (closed) is greater than value 1 and less than value 2, it is a piece
            if (cv2.contourArea(contours[i]) > self.contour_area_cutoff_min) and \
                    (cv2.contourArea(contours[i]) < self.contour_area_cutoff_max):
                # Append the Piece Contours to the new_contours and new_hierarchy lists
                new_contours.append(contours[i])
                new_hierarchy[0].append(hierarchy[0][i])
        # Copy over to contours and hierarchy variables
        contours = new_contours.copy()  # Amend Contours List
        hierarchy = new_hierarchy.copy()
        # Print Contours Found (2x numbers of pieces because gradient both ways counts with canny for some reason)
        # print(f'Num Contours: {len(contours)}')
        # Return Contour and Hierarchy Lists
        return contours, hierarchy

    # (testing) Resize threshold from CP
    def threshold_resizer(self):
        while True:
            try:
                self.adaptive_threshold_num = int(input(f"Resize Threshold (Currently {self.adaptive_threshold_num}) To: "))
            except:
                print("Please Enter a Number.")

    # Finds Centroid using Pixel Values (cv2.moments is cool)
    def get_center_of_contour(self, contour):
        # cv2.moments gives access to a bunch of data about a contour
        M = cv2.moments(contour)
        # contour centroid x and y are calculated like this
        contour_center_X = int(M["m10"] / M["m00"])
        contour_center_Y = int(M["m01"] / M["m00"])
        # return the centroid x and y coords
        return contour_center_X, contour_center_Y

    # Updates the Member variable contour_list (a 2d array of contours sorted by color)
    def update_contour_list(self, piece_contour_list, image):

        # Convert to HSV colorspace for easier color distinction
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Initialize HSV_value array (parallel with piece_contour_list)
        hsv_values = []
        # Get HSV mean Values for Each Piece and append to array (easy way to distinguish between colors) HSV = very
        # good for this
        # Iterate over each contour in piece_contour_list
        for contour in piece_contour_list:
            # Get the Centroid
            center_x, center_y = self.get_center_of_contour(contour)
            # Calculate a value based on hsv (like a mean) -> very good distinction between colors
            # (5 on each side of centroid is enough to get good mean)
            hsv_mean_value = np.mean(np.array(image_hsv[center_y-5:center_y+5, center_x-5:center_x+5]))
            # Append teh hsv value to the hsv_values list
            hsv_values.append(hsv_mean_value)

        # Sort in piece contour list by color distinguish threshold
        # Initialize New List to Populate
        new_list = [[], []]
        # Set the color_1 equal to 1 color's average on average (set elsewhere)
        color_1 = self.hsv_1
        # Iterate over HSV mean values
        for i in range(len(hsv_values)):
            # If the color value of this particular hsv_value is far enough away, it is a different color
            if abs(color_1-hsv_values[i]) < self.color_distinguish_threshold:
                # Same color
                new_list[0].append(piece_contour_list[i])
            else:  # Other color
                new_list[1].append(piece_contour_list[i])
        # Say How Many Pieces Each Side Has on the Board
        print(f'Color 1 Has {len(np.array(new_list)[0])//2} pieces')
        print(f'Color 2 Has {len(np.array(new_list)[1])//2} pieces')
        # Set Member Variable equal to New Distribution
        self.contour_list = new_list.copy()

    # Draws Labels On Top of Pieces
    def draw_labels(self, filtered_contours, image):
        # Iterate Through color 1
        for i in range(0, len(filtered_contours[0]), 2):
            # Get Center
            (center_x, center_y) = self.get_center_of_contour(filtered_contours[0][i])
            # Draw Text Above
            cv2.putText(image, "Player 1", (center_x-15, center_y-25), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.25, color=(255, 0, 0))
        # Iterate Through color 2
        for i in range(0, len(filtered_contours[1]), 2):
            # Get Center
            (center_x, center_y) = self.get_center_of_contour(filtered_contours[1][i])
            # Draw Text Above
            cv2.putText(image, "Player 2", (center_x-15, center_y-25), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.25, color=(0, 0, 255))
        return image

    def update_board_representation(self):
        # since self.contour list can change, we make a copy at the beginning
        local_contour_list = self.contour_list.copy()
        # Get lists of x centers and y centers (parallel)
        x_centers_0 = []; x_centers_1 = []
        y_centers_0 = []; y_centers_1 = []
        # Iterate through contours[0] and append centers to lists -> Also get rid of repeat contours (every other)
        for i in range(0, len(local_contour_list[0]), 2):
            # Get center
            (center_x, center_y) = self.get_center_of_contour(local_contour_list[0][i])
            # Append center
            x_centers_0.append(center_x)
            y_centers_0.append(center_y)
        # Iterate through contours[1] and append centers to lists -> Also get rid of repeat contours (every other)
        for i in range(0, len(local_contour_list[1]), 2):
            # Get center
            (center_x, center_y) = self.get_center_of_contour(local_contour_list[1][i])
            # Append center
            x_centers_1.append(center_x)
            y_centers_1.append(center_y)

        # DO BOARD REPRESENTATION HERE


    def get_x_y_lines(self):
        # since self.contour list can change, we make a copy at the beginning
        local_contour_list = self.contour_list.copy()
        # Get lists of x centers and y centers (parallel)
        x_centers_0 = []; x_centers_1 = []
        y_centers_0 = []; y_centers_1 = []
        # Iterate through contours[0] and append centers to lists -> Also get rid of repeat contours (every other)
        for i in range(0, len(local_contour_list[0]), 2):
            # Get center
            (center_x, center_y) = self.get_center_of_contour(local_contour_list[0][i])
            # Append center
            x_centers_0.append(center_x)
            y_centers_0.append(center_y)
        # Iterate through contours[1] and append centers to lists -> Also get rid of repeat contours (every other)
        for i in range(0, len(local_contour_list[1]), 2):
            # Get center
            (center_x, center_y) = self.get_center_of_contour(local_contour_list[1][i])
            # Append center
            x_centers_1.append(center_x)
            y_centers_1.append(center_y)

        # To Calculate File, Use Both the Starting Y coords for both colors
        combined_y_coords = []
        for coord in y_centers_0:
            combined_y_coords.append(coord)
        for coord in y_centers_1:
            combined_y_coords.append(coord)

        # Calculate Files Using combined y coords -> file = y, rank = x
        files_y = []  # array of y coords for each rank
        # Iterate over all y coordinates of the pieces
        for y_coord in combined_y_coords:
            # Iterate over rank y coords already found
            found_matching_rank = False
            for found_rank_idx in range(len(files_y)):
                # If the difference between this specific y coord and any rank is found, it's not new
                if abs(y_coord-files_y[found_rank_idx]) < self.row_col_threshold:
                    # Found matching rank already
                    found_matching_rank = True
                    # Break loop ranks
                    break
            # If rank wasn't found after search, it's unique
            if not found_matching_rank:
                # Append this new rank
                files_y.append(y_coord)

        # Calculate Ranks Using x_centers_0 and interpolation -> rank = x, file = y -> NEED TO DO
        ranks_x = []

        return ranks_x, files_y

    def draw_x_y_lines(self, ranks_x, files_y, image):
        for file_coord in files_y:
            cv2.line(image, (0, file_coord), (image.shape[1], file_coord), color=(255, 0, 255), thickness=1)
        return image













        # # Approxamate the Shape of the Contour!! -> We want circles for now -> (contour, epsilon=distance it can be off from original shape, closed=True)
        # new_contours = []
        # for i in range(len(contours)):
        #     approx = cv2.approxPolyDP(contours[i], 0.001 * cv2.arcLength(contours[i], True), True)
        #     if len(approx) == 1:  # if it is a square
        #         print("1")
        #     elif len(approx) == 2:
        #         print("2")
        #     elif len(approx) == 3:
        #         print("3")
        #     elif len(approx) == 4:
        #         print("4")
        #     elif len(approx) == 5:
        #         print("5")
        #     else:
        #         new_contours.append(contours[i])
        # contours = new_contours.copy()

        #####################################################

        # # Filter out Innermost items (circles)
        # new_contours = []
        # new_hierarchy = [[]]
        # number_in_hierarchy = 0
        # for i in range(len(hierarchy[0])):
        #     (next, previous, first_child, parent) = hierarchy[0][i]
        #     if (first_child == -1) and (len(cv2.approxPolyDP(contours[i], 0.001 * cv2.arcLength(contours[i], True), True)) != 4):
        #         number_in_hierarchy += 1
        #         new_contours.append(contours[i])
        #         new_hierarchy[0].append(hierarchy[0][i])
        # contours = new_contours.copy()  # Amend Contours List
        # hierarchy = new_hierarchy.copy()
        # # print(number_in_hierarchy)

        ################################################

        # Filter Contours by Size (Filter out Small Ones) (CAMERA ABOUT 26 INCHES ABOVE BOARD) (assume parallel lists -> pretty sure for now)
        # new_contours = []
        # new_hierarchy = [[]]
        # for i in range(len(contours)):
        #     if cv2.arcLength(contours[i], False) > self.contour_perimeter_cutoff:
        #         new_contours.append(contours[i])
        #         new_hierarchy[0].append(hierarchy[0][i])
        #     elif cv2.arcLength(contours[i], True) > self.contour_perimeter_cutoff:
        #         new_contours.append(contours[i])
        #         new_hierarchy[0].append(hierarchy[0][i])
        # contours = new_contours.copy()  # Amend Contours List
        # hierarchy = new_hierarchy.copy()
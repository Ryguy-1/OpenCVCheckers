import numpy as np
from WebCamFeed import WebCamFeed
import cv2
import threading


# Analyzes Webcam Feed. Draws Contours. Updates Member Variable: self.board_representation based on Web Cam Feed
class BoardViewer:

    # Purpose: Initializes Individual Webcam Feed. Hold/Update Board Representation. Start Analyze Board Thread.
    def __init__(self, frame_width=1000, frame_height=1000):
        # WebCamFeed for each BoardViewer
        self.webcam_feed = WebCamFeed(frame_width, frame_height)
        # 2d list with capital pieces in one list and lower case in the other
        self.contour_list = [[], []]
        # [] 8x8 with a 'C' for capital present and a 'L' for lower case present
        self.starting_board_representation = np.array([['~', '~', '~', '~', '~', '~', '~', '~'],
                                                       ['~', '~', '~', '~', '~', '~', '~', '~'],
                                                       ['~', '~', '~', '~', '~', '~', '~', '~'],
                                                       ['~', '~', '~', '~', '~', '~', '~', '~'],
                                                       ['~', '~', '~', '~', '~', '~', '~', '~'],
                                                       ['~', '~', '~', '~', '~', '~', '~', '~'],
                                                       ['~', '~', '~', '~', '~', '~', '~', '~'],
                                                       ['~', '~', '~', '~', '~', '~', '~', '~'],
                                                       ])
        # Reset Switch (Board)
        self.board_representation = self.starting_board_representation.copy()
        # Adaptive Thresholding
        self.adaptive_threshold_num = 117
        # Reset Switch (Threshold)
        self.adaptive_threshold_num_start = self.adaptive_threshold_num
        # Minimum Area Considered as Piece
        self.contour_area_cutoff_min = 510
        # Maximum Area Considered as Piece
        self.contour_area_cutoff_max = 1342
        # Difference in Mean of HSV Values Considered 1 Color
        self.color_distinguish_threshold = 50
        # HSV Separator
        self.hsv_1 = 18
        # Gaussian Blur Number
        self.gaussian_blur = (13, 13)
        # Canny Edge Detection Lower, Upper
        self.canny_lower = 70
        self.canny_upper = 90
        # Frame Delay
        self.frame_delay = 16
        # Row/Column Threshold
        self.row_col_threshold = 40
        # Hold Rank and File Location Information
        self.ranks_x = []
        self.files_y = []
        # Thread which takes info from the webcam feed and constantly updates contour and board information
        self.analyze_thread = threading.Thread(target=self.analyze_board).start()

    # Purpose: cv2 bind for slider (Thresholding)
    def adaptive_threshold_change(self, val):
        if val % 2 == 0:
            val += 1
            self.adaptive_threshold_num = val
            return
        self.adaptive_threshold_num = val

    # Purpose: cv2 bind for slider (Min Area)
    def contour_area_cutoff_min_change(self, val):
        self.contour_area_cutoff_min = val

    # Purpose: cv2 bind for slider (Max Area)
    def contour_area_cutoff_max_change(self, val):
        self.contour_area_cutoff_max = val

    # Purpose: cv2 bind for slider (HSV Separator)
    def hsv_color_separator(self, val):
        self.hsv_1 = val

    # Purpose: cv2 bind for slider (Frame Delay)
    def frame_delay_adjust(self, val):
        self.frame_delay = val

    # Purpose: cv2 bind for slider (Row/Col)
    def row_col_threshold_adjust(self, val):
        self.row_col_threshold = val

    # Purpose: cv2 bind for slider (Grid Reset Switch)
    def reset_grid(self, val):
        if val == 1:
            (self.ranks_x, self.files_y) = self.get_x_y_lines()

    # Purpose: Main Update Loop. Takes Recent frame from self.webcam_feed and acts on it.
    def analyze_board(self):
        # Used for Initialization of Sliders
        is_first_show = True
        while self.webcam_feed.is_running:
            # If the current frame isn't empty (on initialization)
            if self.webcam_feed.current_frame.all() is not None:
                # Grab current frame from WebCamFeed
                image = self.webcam_feed.current_frame
                # Convert to HSV (Hue, Saturation, Value) -> Value
                _, _, grayscale_image = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))
                # Threshold -> Adaptive Threshold useful to help mitigate shadow of camera overhead
                try:
                    # Adaptively Threshold the Grayscale
                    grayscale_image = cv2.adaptiveThreshold(grayscale_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                            cv2.THRESH_BINARY, self.adaptive_threshold_num, 0)
                except:
                    # If User Sets to Even Number, Reset It
                    self.adaptive_threshold_num = self.adaptive_threshold_num_start

                # Blur Threshold Image
                grayscale_image = cv2.GaussianBlur(grayscale_image, self.gaussian_blur, 0)
                # Canny Edged Image
                canny_edged_image = cv2.Canny(grayscale_image, self.canny_lower, self.canny_upper)
                # Find Contours
                (contours, hierarchy) = cv2.findContours(canny_edged_image.copy(), cv2.RETR_TREE,
                                                         cv2.CHAIN_APPROX_SIMPLE)
                # Filter Contours By Area Range
                filtered_contours, filtered_hierarchy = self.filter_contours(contours, hierarchy)
                # Updates contour list
                self.update_contour_list(filtered_contours, image)
                # Draw Labels onto Image
                image = self.draw_labels(self.contour_list, image)
                # Update Board Representation for Read in BoardAnalyzer
                self.update_board_representation()
                # Make copy of image
                outline_image = image.copy()
                # Draw contours into image
                cv2.drawContours(outline_image, filtered_contours, -1, (0, 255, 0),
                                 1)  # -1 = draw all contours -> otherwise, it's the index
                # Draw Ranks and Files on Board
                outline_image = self.draw_x_y_lines(self.ranks_x, self.files_y, outline_image)
                # Show the image
                cv2.imshow(self.webcam_feed.frame_title, outline_image)
                # If First Run, Add Sliders
                if is_first_show:
                    # Threshold Slider
                    cv2.createTrackbar('Thresh', self.webcam_feed.frame_title, self.adaptive_threshold_num, 400,
                                       self.adaptive_threshold_change)
                    # Min Area Slider
                    cv2.createTrackbar('Min Area', self.webcam_feed.frame_title, self.contour_area_cutoff_min, 1500,
                                       self.contour_area_cutoff_min_change)
                    # Max Area Slider
                    cv2.createTrackbar('Max Area', self.webcam_feed.frame_title, self.contour_area_cutoff_max, 2000,
                                       self.contour_area_cutoff_max_change)
                    # Color Separator Slider
                    cv2.createTrackbar('Color', self.webcam_feed.frame_title, self.hsv_1, 300,
                                       self.hsv_color_separator)
                    # Grid Reset Slider (only do at beginning of game)
                    cv2.createTrackbar('Reset Grid', self.webcam_feed.frame_title, 0, 1,
                                       self.reset_grid)
                    # Unused Sliders ##
                    # cv2.createTrackbar('Frame Delay', self.webcam_feed.frame_title, self.frame_delay, 300,
                    #                    self.frame_delay_adjust)
                    # cv2.createTrackbar('Grid Thrsh', self.webcam_feed.frame_title, self.row_col_threshold, 300,
                    #                    self.row_col_threshold_adjust)
                    ###################

                    # Calculate Rank And File Location
                    (self.ranks_x, self.files_y) = self.get_x_y_lines()
                    is_first_show = False
                # Wait in between frames
                cv2.waitKey(self.frame_delay)

    # Purpose: Filter Contours by Area (Closed Mandatory)
    # Input: Contour List, Hierarchy List
    # Output: Contours Filtered by Area, Corresponding Hierarchy
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
        # Return Contour and Hierarchy Lists
        return new_contours, new_hierarchy

    # Purpose: Finds Centroid using Pixel Values
    # Input: Contour
    # Output: Centroid Coordinates of Contour
    def get_center_of_contour(self, contour):
        # cv2.moments read data
        m = cv2.moments(contour)
        # Get X Coordinate, Get Y Coordinate
        contour_center_x = int(m["m10"] / m["m00"])
        contour_center_y = int(m["m01"] / m["m00"])
        # return the centroid x and y coordinates
        return contour_center_x, contour_center_y

    # Purpose: Updates the Member variable contour_list (a 2d array of contours sorted by color)
    # Input: Contour List, Image to Get Colors From
    # Output: Updates Member Variable self.contour_list
    def update_contour_list(self, piece_contour_list, image):

        # Convert to HSV (Saturation Value Works Best)
        _, image_hsv, _ = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))
        # Initialize HSV_value array
        hsv_values = []
        # Iterate over each contour in piece_contour_list
        for contour in piece_contour_list:
            # Get the Centroid
            center_x, center_y = self.get_center_of_contour(contour)
            # Calculate a value based on hsv (like a mean) -> very good distinction between colors
            # (10px on each side of centroid is enough to get good mean)
            hsv_mean_value = np.mean(np.array(image_hsv[center_y-10:center_y+10, center_x-10:center_x+10]))
            # Append HSV value to the hsv_values list
            hsv_values.append(hsv_mean_value)

        # Sort in piece contour list by color distinguish threshold
        # Initialize New List to Populate
        new_list = [[], []]
        # Set the color_1 equal to 1 color's average on average
        color_1 = self.hsv_1
        # Iterate over HSV mean values
        for i in range(len(hsv_values)):
            # If the color value of this particular hsv_value is far enough away, it is a different color
            if abs(color_1-hsv_values[i]) < self.color_distinguish_threshold:
                # Same color
                new_list[1].append(piece_contour_list[i])  # Player 1 has to be on right***
            else:  # Other color
                new_list[0].append(piece_contour_list[i])  # Player 2 has to be on left***
        # Set Member Variable equal to New Distribution
        self.contour_list = new_list.copy()

    # Purpose: Draws Labels On Top of Pieces
    # Input: Contours to Draw on Top of, Image to Draw Contours on
    # Output: Image with Labels Drawn
    def draw_labels(self, filtered_contours, image):
        # Iterate Through color 1
        for i in range(0, len(filtered_contours[0]), 2):
            # Get Center
            (center_x, center_y) = self.get_center_of_contour(filtered_contours[0][i])
            # Draw Text Above
            cv2.putText(image, "Player 1", (center_x-15, center_y-25), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.25,
                        color=(255, 0, 0))
        # Iterate Through color 2
        for i in range(0, len(filtered_contours[1]), 2):
            # Get Center
            (center_x, center_y) = self.get_center_of_contour(filtered_contours[1][i])
            # Draw Text Above
            cv2.putText(image, "Player 2", (center_x-15, center_y-25), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.25,
                        color=(0, 0, 255))
        return image

    # Purpose: Update Member Variable self.board_representation with proper 8x8 numpy array
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

        # Uses the previously calculated x, y lines to figure out where each piece is
        # based on whether it's within the threshold.
        # (X Ranks and Y Files are already both sorted)

        # Player 0 indices for coordinates
        player_0_rank_files = []  # Array of tuples with rank and file (x, then y)
        # Loop through their coordinates
        for (x_coord, y_coord) in zip(x_centers_0, y_centers_0):
            # Keep track of their rank and file numbers found
            rank_num = 0; file_num = 0
            # Loop through the rank coordinates
            for rank_idx in range(len(self.ranks_x)):  # Same size, but for completeness
                # If this x coord is on that rank
                if abs(x_coord-self.ranks_x[rank_idx]) < self.row_col_threshold:
                    # set the rank number to rank_idx
                    rank_num = rank_idx
            # Loop through file coordinates
            for file_idx in range(len(self.files_y)):  # Same size, but for completeness
                # If this y coord is on that rank
                if abs(y_coord-self.files_y[file_idx]) < self.row_col_threshold:
                    # set the file number to file_idx
                    file_num = file_idx
            player_0_rank_files.append((rank_num, file_num))

        # Player 1 indices for coordinates
        player_1_rank_files = []  # Array of tuples with rank and file (x, then y)
        # Loop through their coordinates
        for (x_coord, y_coord) in zip(x_centers_1, y_centers_1):
            # Keep track of their rank and file numbers found
            rank_num = 0; file_num = 0
            # Loop through the rank coordinates
            for rank_idx in range(len(self.ranks_x)):  # Same size, but for completeness
                # If this x coord is on that rank
                if abs(x_coord-self.ranks_x[rank_idx]) < self.row_col_threshold:
                    # set the rank number to rank_idx
                    rank_num = rank_idx
            # Loop through file coordinates
            for file_idx in range(len(self.files_y)):  # Same size, but for completeness
                # If this y coord is on that rank
                if abs(y_coord-self.files_y[file_idx]) < self.row_col_threshold:
                    # set the file number to file_idx
                    file_num = file_idx
            player_1_rank_files.append((rank_num, file_num))

        # Reset Board Representation -> Make copy of original board representation so don't change it
        temp_representation = self.starting_board_representation.copy()
        # Appending to this member variable:
        # self.board_representation = []  # [] 8x8 with a 'C' for capital present and a 'L' for lower case present
        for (x, y) in player_0_rank_files:
            for row_idx in range(len(temp_representation)):
                for col_idx in range(len(temp_representation[row_idx])):
                    if x == row_idx and y == col_idx:
                        temp_representation[row_idx][col_idx] = 'C'
        for (x, y) in player_1_rank_files:
            for row_idx in range(len(temp_representation)):
                for col_idx in range(len(temp_representation[row_idx])):
                    if x == row_idx and y == col_idx:
                        temp_representation[row_idx][col_idx] = 'L'

        self.board_representation = temp_representation  # set board representation equal to this new board

    # Purpose: At Beginning of Game, Use Initial Position of Pieces to Draw x, y lines for checkerboard
    # Output: (From Side View of Board) List of X Ranks (Columns), List of Y Files (Rows)
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

        # To Calculate File, Use the Starting Y coords for both colors
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
                if abs(y_coord-files_y[found_rank_idx][0]) < self.row_col_threshold:
                    # Found matching rank already
                    found_matching_rank = True
                    # Add coord at same rank
                    files_y[found_rank_idx].append(y_coord)
                    # Break loop ranks
                    break
            # If rank wasn't found after search, it's unique
            if not found_matching_rank:
                # Append this new rank
                files_y.append([y_coord])

        # Average the different values found for that rank
        averaged_files_y = []
        for file in files_y:
            averaged_files_y.append(int(np.mean(file)))

        # Calculate Ranks Using x_centers_0 and interpolation -> rank = x, file = y
        ranks_x = []

        # To Calculate Rank, Use the Starting X coords for both colors
        combined_x_coords = []
        for coord in x_centers_0:
            combined_x_coords.append(coord)
        for coord in x_centers_1:
            combined_x_coords.append(coord)

        # Iterate over all x coordinates of the pieces
        for x_coord in combined_x_coords:
            # Iterate over rank y coords already found
            found_matching_rank = False
            for found_rank_idx in range(len(ranks_x)):
                # If the difference between this specific y coord and any rank is found, it's not new
                if abs(x_coord-ranks_x[found_rank_idx][0]) < self.row_col_threshold:
                    # Found matching rank already
                    found_matching_rank = True
                    # Add coord at same rank
                    ranks_x[found_rank_idx].append(x_coord)
                    # Break loop ranks
                    break
            # If rank wasn't found after search, it's unique
            if not found_matching_rank:
                # Append this new rank
                ranks_x.append([x_coord])

        # Average the different values found for that rank
        averaged_ranks_x = []
        for rank in ranks_x:
            averaged_ranks_x.append(int(np.mean(rank)))

        # Sort Each Rank
        averaged_ranks_x = np.sort(averaged_ranks_x)
        averaged_files_y = np.sort(averaged_files_y)

        # Fill in Middle 2 X Ranks (Interpolate)
        try:
            # Get Distances between index 1 and 2 (left side middle difference)
            difference_left = np.mean([abs(averaged_ranks_x[1]-averaged_ranks_x[2])])
            # Get Distances between index 3 and 4 (right side middle difference)
            difference_right = np.mean([abs(averaged_ranks_x[3]-averaged_ranks_x[4])])
            # Insert a new index after the left three -> using the left difference
            averaged_ranks_x = np.insert(averaged_ranks_x, 3, averaged_ranks_x[2]+difference_left)
            # Insert a new index before the right three -> using the right difference
            averaged_ranks_x = np.insert(averaged_ranks_x, 4, averaged_ranks_x[4]-difference_right)
        except:
            print("Please Use Reset Slider to Reset X, Y")

        return averaged_ranks_x, averaged_files_y

    # Purpose: Draw X and Y Lines on Image
    # Input: X lines, Y Lines, Image to Draw On
    # Output: Image with Rows/Cols Drawn on It
    def draw_x_y_lines(self, ranks_x, files_y, image):
        # Draw Files
        for file_coord in files_y:
            cv2.line(image, (0, file_coord), (image.shape[1], file_coord), color=(255, 255, 255), thickness=1)

        # Draw Ranks
        for rank_coord in ranks_x:
            cv2.line(image, (rank_coord, 0), (rank_coord, image.shape[0]), color=(255, 255, 255), thickness=1)

        return image

    # Purpose: Print Board Representation to Console
    # Input: Board Representation
    def print_board(self, board):
        for row_idx in range(len(board)):
            for col_idx in range(len(board)):
                print(board[row_idx][col_idx], end =" ")  # Print without new line at end
            print()  # Print spacer line

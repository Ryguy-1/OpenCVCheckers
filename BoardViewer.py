import time
import numpy as np
from WebCamFeed import WebCamFeed
import cv2
import threading
import math

# Gets Checker Pieces from Feed and Map Them to a board array (bitboards)
class BoardViewer:

    def __init__(self, frame_width=1000, frame_height=1000):
        # WebCamFeed for each BoardViewer
        self.webcam_feed = WebCamFeed(frame_width, frame_height)
        self.contour_list = [[], []]  # 2d list with white pieces in one list and blue in the other -> updated every frame (consistent though)
        # Number for adaptive thresholding
        self.adaptive_threshold_num = 111
        # Reset Switch
        self.adaptive_threshold_num_start = self.adaptive_threshold_num
        # Minimum Area Considered as Piece
        self.contour_area_cutoff_min = 80 * math.pi
        # Maimum Area Considered as Piece
        self.contour_area_cutoff_max = 1400
        # Difference in Mean of HSV Values Considered 1 Color
        self.color_distinguish_threshold = 15
        # Gaussian Blur Number
        self.gaussian_blur = (13, 13)
        # Canny Edge Detection Lower, Upper
        self.canny_lower = 70; self.canny_upper = 90
        # Thread which takes info from the webcam feed and constantly updates contour information in contour_list
        self.analyze_thread = threading.Thread(target=self.analyze_board).start()
        # Allows Changing Adaptive Threshold number from Command Prompt -> Not used in final version (testing)
        # self.threshold_resizer = threading.Thread(target=self.threshold_resizer).start()

    def analyze_board(self):
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

                # Canny Edged Image
                canny_edged_image = cv2.Canny(grayscaled_image, self.canny_lower, self.canny_upper)  # 70, 90 works pretty well
                # Find Contours and filter contours by area
                (contours, hierarchy) = cv2.findContours(canny_edged_image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                filtered_contours, filtered_hierarchy = self.filter_contours(contours, hierarchy)

                # Updates contour list
                if len(filtered_contours) > 0:
                    self.update_contour_list(filtered_contours, image)

                # Make copy of image (destructive)
                outline_image = image.copy()
                # Draw contours into image
                cv2.drawContours(outline_image, filtered_contours, -1, (0, 255, 0),
                                 1)  # -1 = draw all contours -> otherwise, it's the index
                # Show the image
                cv2.imshow(self.webcam_feed.frame_title, outline_image)

                # Wait 10 ms in between frames
                cv2.waitKey(1000)

    # Filter Contours by Area (Closed Mandatory)
    def filter_contours(self, contours, hierarchy):
        # New Empty Lists for Contours and Hierarchy
        new_contours = []
        new_hierarchy = [[]]
        # Iterate through Contours
        for i in range(len(contours)):
            # If Contour Area (closed) is greater than value 1 and less than value 2, it is a piecee
            if (cv2.contourArea(contours[i]) > self.contour_area_cutoff_min) and \
                    (cv2.contourArea(contours[i]) < self.contour_area_cutoff_max):
                # Append the Piece Contours to the new_contours and new_hierarchy lists
                new_contours.append(contours[i])
                new_hierarchy[0].append(hierarchy[0][i])
        # Copy over to contours and hierarchy variables
        contours = new_contours.copy()  # Amend Contours List
        hierarchy = new_hierarchy.copy()
        # Print Contours Found (2x numbers of pieces because gradient both ways counts with canny for some reason)
        print(f'Num Contours: {len(contours)}')
        # Return Contour and Hierarchy Lists
        return contours, hierarchy

    # (testing) Resize threshold from CP
    def threshold_resizer(self):
        while True:
            try:
                self.adaptive_threshold_num = int(input(f"Resize Threshold (Currently {self.adaptive_threshold_num}) To: "))
            except:
                print("Please Enter a Number.")

    # Updates the Member variable contour_list (a 2d array of contours sorted by color)
    def update_contour_list(self, piece_contour_list, image):

        # Finds Centroid using Pixel Values (cv2.moments is cool)
        def get_center_of_contour(contour):
            # cv2.moments gives access to a bunch of data about a contour
            M = cv2.moments(contour)
            # contour centroid x and y are calculated like this
            contour_center_X = int(M["m10"] / M["m00"])
            contour_center_Y = int(M["m01"] / M["m00"])
            # return the centroid x and y coords
            return contour_center_X, contour_center_Y

        # Convert to HSV colorspace for easier color distinction
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Initialize HSV_value array (parallel with piece_contour_list)
        hsv_values = []
        # Get HSV mean Values for Each Piece and append to array (easy way to distinguish between colors) HSV = very
        # good for this
        # Iterate over each contour in piece_contour_list
        for contour in piece_contour_list:
            # Get the Centroid
            center_x, center_y = get_center_of_contour(contour)
            # Calculate a value based on hsv (like a mean) -> very good distinction between colors
            # (5 on each side of centroid is enough to get good mean)
            hsv_mean_value = np.mean(np.array(image_hsv[center_y-5:center_y+5, center_x-5:center_x+5]))
            # Append teh hsv value to the hsv_values list
            hsv_values.append(hsv_mean_value)

        # Sort in piece contour list by color distinguish threshold
        # Initialize New List to Populate
        new_list = [[], []]
        # Set the color_1 equal to the first curve's centroid average
        color_1 = hsv_values[0]
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
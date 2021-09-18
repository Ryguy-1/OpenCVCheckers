import cv2
import keyboard
import threading
import numpy as np
import time


# Encapsulates WebCam Feed. (Get Current Frame through web_cam_feed.current_frame)
class WebCamFeed:

    # Title of Frame
    frame_title = "Checkers Board Viewer [('q') to Quit, ('r') to Reset Mask]"

    # Purpose: Initialize Video Capture / Member Variables
    def __init__(self, frame_width, frame_height):
        print("Initializing Webcam Stream...")
        # Video Capture Variable initialize and set size(0 = webcam live feed, cv2.CAP_DSHOW = Direct Show (video input)
        # (also makes loading much faster)
        self.vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        print("Done.")
        # Frame width and height (not image capture height/width)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
        # Running Live Capture
        self.is_running = True
        # Current Frame initialize to empty
        self.current_frame = np.array([None])
        # Initialize Capture Thread and Start it
        print("Starting Live Capture...")
        self.capture_thread = threading.Thread(target=self.run_live_feed).start()
        print("Running.")
        # Cropping
        self.cropping = False
        self.crop_start = (0, 0)  # Reset when lift mouse button
        self.crop_end = (0, 0)  # Reset when lift mouse button
        self.mask = None  # Calculated Mask to Apply to Each Frame
        # Initialize Cropping Feature
        self.prompt_crop = threading.Thread(target=self.prompt_crop).start()

    # Purpose: Camera Loop.
    # Output: Set Member (self.current_frame) equal to most recent frame (read later in Board Viewer)
    def run_live_feed(self):
        # While is running
        while self.is_running:
            # ret = True if frame read correctly, frame = numpy array of frame read
            ret, frame = self.vid.read()
            # If the frame is not read correctly, stop frame reading (ret==False if frame not red correctly)
            if not ret:
                print("Frame not Read Correctly. Please Check Camera is Plugged in Correctly. Quitting Frame Read")
                # If not read correctly, stop trying (no camera, etc)
                self.is_running = False
                # Close Device (Best Practice)
                self.vid.release()
                # Break Running Loop
                break

            # Set Member variable current frame to frame (to be accessed elsewhere when requested)
            if self.mask is not None:  # If there is a mask
                frame = cv2.bitwise_and(frame, frame, mask=self.mask)
                # set Current Frame Member variable equal to current frame with crop mask
                self.current_frame = frame
            else:  # If there isn't a mask, just set member variable equal to current frame
                self.current_frame = frame
            # Wait 16ms in between frames (a little more than 60fps (ideally))
            cv2.waitKey(16)
            if keyboard.is_pressed('q'):
                self.is_running = False
                # Close Device (Best Practice)
                self.vid.release()
                break
            elif keyboard.is_pressed('r'):  # Clear Mask
                self.mask = None

    # Purpose: Make Left Click Bind to Crop Function
    def prompt_crop(self):
        # While the current frame isn't None -> Then wait an additional 0.3 seconds (make sure loaded)
        while True:
            if self.current_frame.all() is not None:
                break
        time.sleep(0.3)

        # Function linked to left click on frame (through cv2)
        def lc_callback(event, x, y, flags, param):
            # If Left MB Down
            if event == cv2.EVENT_LBUTTONDOWN:
                # Cropping is True
                self.cropping = True
                # Record x,y for start_pos
                self.crop_start = (x, y)
                # Print Crop Start Pos
                print(self.crop_start)
            elif event == cv2.EVENT_LBUTTONUP:
                # Cropping is False
                self.cropping = False
                # Record x, y for end_pos
                self.crop_end = (x, y)
                # Print Crop End Pos
                print(self.crop_end)
                # Update member variable Mask
                self.update_mask()

        # Sets the webcam feed window's callback function when lc is pressed to lc_callback
        cv2.setMouseCallback(self.frame_title, lc_callback)

    # Purpose: Update Member Variables for Crop and self.mask
    def update_mask(self):
        # Set the Mask Here
        self.mask = np.zeros(self.current_frame.shape[:2], dtype="uint8")
        # Retrieve Start and End Crops
        (start_x, start_y) = self.crop_start
        (end_x, end_y) = self.crop_end
        # Get the mask rectangle using the start and end positions
        # (255=mask color, -1 = fill it in so it's a mask, not outline)
        cv2.rectangle(self.mask, (start_x, start_y), (end_x, end_y), 255, -1)

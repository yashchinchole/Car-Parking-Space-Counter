import cv2
import numpy as np
import cvzone
import pickle

# Load the parking positions
with open('carParkPos', 'rb') as f:
    poslist = pickle.load(f)

# Define the width and height of the parking space
width, height = (508 - 400), (235 - 189)

def checkParkingSpace(vidProc, vid):
    spaceCounter = 0
    for pos in poslist:
        x, y = pos
        vidCrop = vidProc[y:y + height, x:x + width]
        count = cv2.countNonZero(vidCrop)
        
        if count < 500:
            spaceCounter += 1
            color = (0, 255, 0)
            thickness = 3
        else:
            color = (0, 0, 255)
            thickness = 1
        
        cvzone.putTextRect(vid, str(count), (x, y + height - 2), scale=1, thickness=1, offset=0, colorR=color)
        cv2.rectangle(vid, pos, (pos[0] + width, pos[1] + height), color, thickness)
    
    cvzone.putTextRect(vid, f'Free Space {spaceCounter}/{len(poslist)}', (450, 50), scale=2, thickness=3, offset=20, colorR=(255, 200, 0))

# Capture the video
cap = cv2.VideoCapture('carPark.mp4')

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
   
    success, vid = cap.read()
    if not success:
        break

    # Convert to grayscale
    vidGray = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    vidBlur = cv2.GaussianBlur(vidGray, (3, 3), 1)

    # Apply adaptive threshold
    vidThreshold = cv2.adaptiveThreshold(vidBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    
    # Apply median blur
    vidMedian = cv2.medianBlur(vidThreshold, 5)

    # Apply dilation
    kernel = np.zeros((3, 3), np.uint8)
    vidDilate = cv2.dilate(vidMedian, kernel, iterations=1)

    # Check parking space
    checkParkingSpace(vidDilate, vid)

    # Display the video
    cv2.imshow('carParking', vid)
    
    # Check for 'q' key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()

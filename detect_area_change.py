# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import time
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# initialize the list of tracked points
pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
	camera = cv2.VideoCapture(args["video"])

#Creating a Pandas DataFrame To Store Data Point
Data_Features = ['x', 'y', 'time']
Data_Points = pd.DataFrame(data = None, columns = Data_Features , dtype = float)

#Reading the time in the begining of the video.
start = time.time()

# keep looping
points = 0
mask = None
firstFrame = None

ball_in = False

while True:
	# grab the current frame
	(grabbed, frame) = camera.read()
	
	#Reading The Current Time
	current_time = time.time() - start

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if args.get("video") and not grabbed:
		break

	text = "Unoccupied"
	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	if firstFrame is None:
		firstFrame = gray
		continue

	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 50, 255, cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)

	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	# loop over the contours
	ball_in_this_time = False
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 30:
			continue
			# compute the bounding box for the contour, draw it on the frame,
			# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		# image changed at left side
		if x < 250:
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
			ball_in_this_time = True
			text = "Occupied"
	
	if not ball_in and ball_in_this_time:
		points = points + 1

	ball_in = ball_in_this_time

	cv2.putText(frame, "Points: {}".format(points), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	# show the frame and record if the user presses a key
	cv2.imshow("original", frame)
	cv2.imshow("threshold", thresh)
	cv2.moveWindow("threshold", 0, 310)
	cv2.imshow("Frame Delta", frameDelta)
	cv2.moveWindow("Frame Delta", 0, 620)

	#pts.appendleft(center)

	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

#'h' is the focal length of the camera
#'X0' is the correction term of shifting of x-axis
#'Y0' is the correction term ofshifting of y-axis
#'time0' is the correction term for correction of starting of time
h = 0.2
X0 = -3
Y0 = 20
time0 = 0
theta0 = 0.3

#Applying the correction terms to obtain actual experimental data
Data_Points['x'] = Data_Points['x']- X0
Data_Points['y'] = Data_Points['y'] - Y0
Data_Points['time'] = Data_Points['time'] - time0

#Calulataion of theta value
Data_Points['theta'] = 2 * np.arctan(Data_Points['y']*0.0000762/h)#the factor correspons to pixel length in real life
Data_Points['theta'] = Data_Points['theta'] - theta0

#Creating the 'Theta' vs 'Time' plot
plt.plot(Data_Points['theta'], Data_Points['time'])
plt.xlabel('Theta')
plt.ylabel('Time')

#Export The Data Points As cvs File and plot
Data_Points.to_csv('Data_Set.csv', sep=",")
plt.savefig('Time_vs_Theta_Graph.svg', transparent= True)

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

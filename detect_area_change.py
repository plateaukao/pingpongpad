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
import os
import requests
from socketIO_client import SocketIO, LoggingNamespace

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
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"]="rtsp_transport;udp"

def on_hit_status_response(args):
    print('on_hit_status_response', args['data'])

socketIO = SocketIO('192.168.1.116', 5000, LoggingNamespace)
socketIO.on('hit_status_response', on_hit_status_response)

isCamera = False
if not args.get("video", False):
	#camera = cv2.VideoCapture(0)
	camera = cv2.VideoCapture('rtsp://192.168.1.131:8086', cv2.CAP_FFMPEG)
	isCamera = True
# otherwise, grab a reference to the video file
else:
	camera = cv2.VideoCapture(args["video"])

#Creating a Pandas DataFrame To Store Data Point
Data_Features = ['x', 'y', 'time']
Data_Points = pd.DataFrame(data = None, columns = Data_Features , dtype = float)

fps = 30
#Reading the time in the begining of the video.
start = time.time()

# keep looping
total_hits = 0
mask = None
firstFrame = None

is_ball_in = False
max_continuous_hits = 0
continous_hits = 0
total_balls = 0

last_ball_in_frame_count = 0

skip_frames = 30 if isCamera else 100
frame_count = 0

last_ball_in_time = None

while True:
	while (skip_frames > 0):
		skip_frames -= 1
		camera.read()
		frame_count +=1

	# grab the current frame
	(grabbed, frame) = camera.read()
	current_time = time.time()
	frame_count += 1
	
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if args.get("video") and not grabbed:
		break

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
	is_ball_in_this_time = False
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 30:
			continue
			# compute the bounding box for the contour, draw it on the frame,
		(x, y, w, h) = cv2.boundingRect(c)
		# image changed at left side
		if x < 250:
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
			is_ball_in_this_time = True
	
	if not is_ball_in and is_ball_in_this_time:
		total_hits = total_hits + 1

		if last_ball_in_time is None:
			total_balls += 1

		is_within_cont_threshold = frame_count - last_ball_in_frame_count < fps
		if isCamera:
			if last_ball_in_time is None or current_time - last_ball_in_time < 1:
				is_within_cont_threshold = True
      
		if is_within_cont_threshold:
			continous_hits = continous_hits + 1
		else:
			total_balls += 1
			continous_hits = 1

		last_ball_in_frame_count = frame_count
		last_ball_in_time = current_time
		if continous_hits > max_continuous_hits:
			max_continuous_hits = continous_hits

		socketIO.emit('hit_status', {"total_balls": total_balls, "total_hits": total_hits, "cont_hits": continous_hits, "max_cont_hits": max_continuous_hits})
		#requests.post("http://192.168.1.116:5000/status", json = {"total_balls": total_balls, "total_hits": total_hits, "cont_hits": continous_hits, "max_cont_hits": max_continuous_hits})

	is_ball_in = is_ball_in_this_time

	cv2.putText(frame, "Total balls: {}".format(total_balls), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
	cv2.putText(frame, "Total hits: {}".format(total_hits), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
	cv2.putText(frame, "Cont. hits: {}".format(continous_hits), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
	cv2.putText(frame, "Max Cont. hits: {}".format(max_continuous_hits), (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
	#cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame and record if the user presses a key
	cv2.imshow("original", frame)
	cv2.imshow("threshold", thresh)
	cv2.moveWindow("threshold", 0, 400)
	cv2.imshow("Frame Delta", frameDelta)
	cv2.moveWindow("Frame Delta", 0, 800)
	#cv2.moveWindow("Red Mask", 0, 1200)

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

elapsed_time = frame_count

print("""
############
Statistics
############
	  """)
print("Time: %02d:%02d:%02d" % (elapsed_time / 30 / 60 / 60, elapsed_time / 30 / 60 % 60, elapsed_time / 30 % 60))
print("Total hits: " + str(total_hits))
print("Total balls: " + str(total_balls))
print("Max continuous hits: " + str(max_continuous_hits))

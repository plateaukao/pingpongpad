#!/usr/bin/python3
import cv2
import imutils
import datetime

## Read and merge
img = cv2.imread("p.png")
img2 = cv2.imread("p1.png")
origin = img.copy()
origin2 = img2.copy()
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
img2_hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

frame = imutils.resize(img, width=500)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (21, 21), 0)

text = "Unoccupied"
firstFrame = None

if firstFrame is None:
    firstFrame = gray

frame = imutils.resize(img2, width=500)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (21, 21), 0)

frameDelta = cv2.absdiff(firstFrame, gray)
thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
thresh = cv2.dilate(thresh, None, iterations=2)

cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
# loop over the contours
for c in cnts:
    # if the contour is too small, ignore it
    if cv2.contourArea(c) < 1:
        continue
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    text = "Occupied"

cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
# show the frame and record if the user presses a key
cv2.imshow("Security Feed", frame)
cv2.imshow("Thresh", thresh)
cv2.imshow("Frame Delta", frameDelta)
cv2.waitKey()

#mask1 = cv2.inRange(img_hsv, (0,50,20), (5,255,255))
#mask2 = cv2.inRange(img_hsv, (175,50,20), (180,255,255))
#mask = cv2.bitwise_or(mask1, mask2 )
#croped = cv2.bitwise_and(img, img, mask=mask)

## Display
#cv2.imshow("mask", mask)
#cv2.imshow("origin", img.copy())
#cv2.imshow("croped", croped)
#cv2.waitKey()
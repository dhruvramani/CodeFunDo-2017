import os
import cv2
import imutils
import numpy as np
from imutils import contours
from imutils import perspective
from scipy.spatial import distance as dist

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# NOTE: Wrong!!
def min_dif(list1, list2):    
    return [list1[0], list1[1], list2[0]] # TODO : Changes this!

def object_size(filepath, left_width):
    image = cv2.imread(filepath)
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray  = cv2.GaussianBlur(gray, (7, 7), 0)
    
    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # NOTE : Contour - Outlines
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    (cnts, _) = contours.sort_contours(cnts)
    pixelsPerMetric = None

    dimensions = list()
    for c in cnts:
        if cv2.contourArea(c) < 100:
            continue
        orig = image.copy()
        box = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)

        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

        if pixelsPerMetric is None:
            pixelsPerMetric = dB / left_width

        dimA = dA / pixelsPerMetric
        dimB = dB / pixelsPerMetric

        dimensions.append((dimA, dimB))
    # Returns a list of dimensions, each dimension for each object.
    # ie. dimensions of many objects
    return dimensions

def weight(file1, left_width, const_div=10.0): # left_width = A4 Size
    size1 = object_size(file1, left_width)
    #size2 = object_size(file2, left_width)
    #sizes = min_dif(size1, size2)
    weights = [i[0] * i[1] / const_div for i in size1]
    return weights
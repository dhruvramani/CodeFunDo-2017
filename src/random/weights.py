import os
import cv2
import imutils
import numpy as np
from imutils import contours
from imutils import perspective
from scipy.spatial import distance as dist


def detect_shape(filepath, min_width=15, debug=False):
    image = cv2.imread(filepath, 0)

    resized = imutils.resize(image, width=300)
    ratio = image.shape[0] / float(resized.shape[0])
    '''
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    '''
    gray = cv2.bilateralFilter(resized, 1, 10, 120 )
    edges  = cv2.Canny( gray, 10, 250 )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx( edges, cv2.MORPH_CLOSE, kernel )
    '''
    cnts = cv2.findContours( closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    gray  = cv2.GaussianBlur(resized, (7, 7), 0)
    edged = cv2.Canny(gray, 10, 250)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)
    '''
    cnts = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    
    shapes = dict()
    print(len(cnts))
    for idx, c in enumerate(cnts):
        try :
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.1 * perimeter, True)
            if len(approx) == 4:
                (x, y, w, h) = cv2.boundingRect(approx)
                shapes["rect_{}".format(idx)] = (x, y, w, h)
                if(debug == True):
                    M = cv2.moments(c)
                    cX = int((M["m10"] / M["m00"]) * ratio)
                    cY = int((M["m01"] / M["m00"]) * ratio)
                    c = c.astype("float")
                    c *= ratio
                    c = c.astype("int")
                    cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                    cv2.putText(image, "square", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('image', 300,300)
                    cv2.imshow("image", image)
                    cv2.waitKey(0)
        except :
            pass

    return shapes

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def min_dif(list1, list2):    
    min_d, ind = 1000000, -1
    for i in range(0, len(list1)):
        for j in range(0, len(list2)):
             if(list1[i]-list2[j] < min_d):
                 ind = j
                 min_d = list1[i]-list2[j]
    return ind

def object_size(filepath, left_width=15):
    image = cv2.imread(filepath, 0)
    #gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray  = cv2.GaussianBlur(image, (7, 7), 0)
    
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

        cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
 
        # draw lines between the midpoints
        cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (255, 0, 255), 2)
        cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (255, 0, 255), 2)

        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

        if pixelsPerMetric is None:
            pixelsPerMetric = dB / left_width

        dimA = dA / pixelsPerMetric
        dimB = dB / pixelsPerMetric

        cv2.putText(orig, "{:.1f}in".format(dimA), (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(orig, "{:.1f}in".format(dimB), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 300,300)
        cv2.imshow("image", orig)
        cv2.waitKey(0)

        dimensions.append((dimA, dimB))

    max_dim = [-1, -1]
    for dims in dimensions:
        if(dims[0] * dims[1] > max_dim[0] * max_dim[1] and left_width not in dims):
            max_dim[0] = dims[0]
            max_dim[1] = dims[1]
    return max_dim

def weight(file1, file2, left_width=21, const_div=6000.0): # left_width = A4 Size
    size1 = object_size(file1, left_width)
    size2 = object_size(file2, left_width)
    rem_ind = min_dif(size1, size2)
    weight = (size1[0] * size1[1] * size2[1-rem_ind]) / const_div
    return weight

if __name__ == '__main__':
    print(detect_shape("img.jpg", debug=True))

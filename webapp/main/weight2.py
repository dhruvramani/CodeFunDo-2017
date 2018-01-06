import sys
import math
import cv2 as cv
import imutils
import numpy as np
from imutils import perspective, contours
from scipy.spatial import distance as dist

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10

def min_dif(list1, list2):    
    min_d, ind = 1000000, -1
    for i in range(0, len(list1)):
        for j in range(0, len(list2)):
             if(list1[i]-list2[j] < min_d):
                 ind = j
                 min_d = list1[i]-list2[j]
    return ind

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def find_squares(path, debug=False):
    img = cv.imread(path)
    img = cv.GaussianBlur(img, (5, 5), 0)
    squares, dimensions, xa, ya = [], [], [0], [0]
    for gray in cv.split(img):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv.Canny(gray, 0, 50, apertureSize=5)
                bin = cv.dilate(bin, None)
            else:
                _retval, bin = cv.threshold(gray, thrs, 255, cv.THRESH_BINARY)
            bin, contour, _hierarchy = cv.findContours(bin, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
            for idx, cnt in enumerate(contour):
                cnt_len = cv.arcLength(cnt, True)
                cnt = cv.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv.contourArea(cnt) > 2000 and cv.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < 0.1:
                        squares.append(cnt)
                        x, y, w, h = cv.boundingRect(cnt)
                        if(roundup(x) not in xa or roundup(y) not in ya):
                            dimensions.append([x, y, w, h])
                            xa.append(roundup(x))
                            ya.append(roundup(y))

    if(debug == True):
        print(dimensions)
        cv.drawContours( img, squares, -1, (0, 255, 0), 3 )
        cv.imshow('squares', img)
        ch = cv.waitKey()
    return dimensions

def get_dimension(path, left_width=15):
    dimensions = find_squares(path, False)
    pixcm = dimensions[0][2] / left_width

    max_dim = [-1, -1]
    for dims in dimensions:
        if(dims[2] - dims[0] > max_dim[0] and dims[3] - dims[1] > max_dim[1] and left_width * pixcm not in dims[2:]):
            max_dim[0] = dims[2]
            max_dim[1] = dims[3]

    max_dim = [x / pixcm for x in max_dim]
    return max_dim

def weight(file1, file2, left_width=15, const_div=6000.0): # left_width = A4 Size
    size1 = get_dimension(file1, left_width)
    size2 = get_dimension(file2, left_width)
    rem_ind = min_dif(size1, size2)
    weight = (size1[0] * size1[1] * size2[1-rem_ind]) / const_div
    return weight

if __name__ == '__main__':
    print(get_dimension("img.jpg"))

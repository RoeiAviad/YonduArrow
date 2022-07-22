from cv2 import threshold
import cv2
import dlib
import numpy as np

def shape_to_np(shape, dtype="int"):
	# initialize the list of (x, y)-coordinates
	coords = np.zeros((68, 2), dtype=dtype)
	# loop over the 68 facial landmarks and convert them
	# to a 2-tuple of (x, y)-coordinates
	for i in range(0, 68):
		coords[i] = (shape.part(i).x, shape.part(i).y)
	# return the list of (x, y)-coordinates
	return coords

def eye_on_mask(mask, side):
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask

def contouring(thresh, mid, img, right=False):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key = cv2.contourArea)
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        if right:
            cx += mid
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 2)
        return cx, cy
    except:
        return np.inf


def light_level(img):
    avg_color_per_row = np.average(img, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    return avg_color.mean()

def eyes_relative(shape, eyes):
    if eyes[0] == np.inf or eyes[1] == np.inf:
        return np.inf
    A, B = (np.average((shape[37], shape[38]), 0), np.average((shape[43], shape[44]), 0)), \
        (np.average((shape[41], shape[40]), 0), np.average((shape[47], shape[46]), 0))
    O = np.average((np.average((A[0], B[0]), 0), np.average((shape[36], shape[39]), 0)), 0), \
        np.average((np.average((A[1], B[1]), 0), np.average((shape[42], shape[45]), 0)), 0)

    O_int = (int(O[0][0]), int(O[0][1])), (int(O[1][0]), int(O[1][1]))
    cv2.circle(img, O_int[0], 2, (0, 255, 0), -1)
    cv2.circle(img, O_int[1], 2, (0, 255, 0), -1)

    return np.subtract(eyes[0], O[0]), np.subtract(eyes[1], O[1])


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('weights/shape_68.dat')

left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]

cap = cv2.VideoCapture(0)
ret, img = cap.read()
thresh = img.copy()

cv2.namedWindow('image')
kernel = np.ones((9, 9), np.uint8)

def nothing(x):
    pass
# cv2.createTrackbar('threshold', 'image', 0, 255, nothing)

while(True):
    ret, img = cap.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask = eye_on_mask(mask, left)
        mask = eye_on_mask(mask, right)
        mask = cv2.dilate(mask, kernel, 5)
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = (shape[42][0] + shape[39][0]) // 2
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        # threshold = cv2.getTrackbarPos('threshold', 'image')
        # print(light_level(img))
        threshold = 35 if light_level(img) < 100 else 40 if light_level(img) < 150 else 50
        _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
        thresh = cv2.erode(thresh, None, iterations=2) #1
        thresh = cv2.dilate(thresh, None, iterations=4) #2
        thresh = cv2.medianBlur(thresh, 3) #3
        thresh = cv2.bitwise_not(thresh)
        eyes = [None, None]
        eyes[0] = contouring(thresh[:, 0:mid], mid, img)
        eyes[1] = contouring(thresh[:, mid:], mid, img, True)
        print(eyes_relative(shape, eyes))
        for (x, y) in shape[36:48]:
            cv2.circle(img, (x, y), 2, (255, 0, 0), -1)
    # show the image with the face detections + facial landmarks
    cv2.imshow('eyes', img)
    cv2.imshow("image", thresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
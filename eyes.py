from cv2 import threshold
import cv2
import dlib
import numpy as np
from screeninfo import get_monitors
from torch import real

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

def gaze_pos(gaze):
    global corners
    x = (gaze[0] - corners[0][0]) / (corners[1][0] - corners[0][0])
    y = (gaze[1] - corners[0][1]) / (corners[3][1] - corners[0][1])
    x, y = round_parts(x, 20), round_parts(y, 20)
    return 0.02 if x < 0 else 0.98 if x > 1 else x, 0.02 if y < 0 else 0.98 if y > 1 else y

def round_parts(num, parts):
    return round(num * parts) / parts

def putText(img, text):
    font = cv2.FONT_HERSHEY_DUPLEX
    textsize = cv2.getTextSize(text, font, 1.6, 2)[0]
    textX = (img.shape[1] - textsize[0]) // 2
    textY = (img.shape[0] + textsize[1]) // 2
    cv2.putText(blank_image, text, (textX, textY), font, 1.6, (255, 0, 0))

DIMS = (640, 480)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('trash\\GazeTracking\\gaze_tracking\\trained_models\\shape_predictor_68_face_landmarks.dat')

left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]

cap = cv2.VideoCapture(0)
ret, img = cap.read()
thresh = img.copy()

cv2.namedWindow('image')
kernel = np.ones((9, 9), np.uint8)

def nothing(x):
    pass

corners = []
dim_corners = []
real_dims = []
for m in get_monitors():
    if m.is_primary:
        real_dims = [m.width, m.height]
        dim_corners = [(8, 8), (m.width - 8, 8), (m.width - 8, m.height - 8), (8, m.height - 8)]

while(True):
    ret, img = cap.read()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    gaze = None
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

        threshold = 35 if light_level(img) < 100 else 40 if light_level(img) < 150 else 50
        _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
        thresh = cv2.erode(thresh, None, iterations=2) #1
        thresh = cv2.dilate(thresh, None, iterations=4) #2
        thresh = cv2.medianBlur(thresh, 3) #3
        thresh = cv2.bitwise_not(thresh)
        eyes = [None, None]
        eyes[0] = contouring(thresh[:, 0:mid], mid, img)
        eyes[1] = contouring(thresh[:, mid:], mid, img, True)

        for (x, y) in shape[36:48]:
            cv2.circle(img, (x, y), 2, (255, 0, 0), -1)

        gaze = eyes_relative(shape, eyes)
        
    img = cv2.flip(img, 1)
    thresh = cv2.flip(thresh, 1)

    blank_image = np.zeros(shape=[real_dims[1], real_dims[0], 3], dtype=np.uint8)

    if len(corners) < 4:
        putText(blank_image, "Look at the dot and press Space!")
        cv2.circle(blank_image, dim_corners[len(corners)], 4, (255, 0, 0), 8)
        if cv2.waitKey(1) & 0xFF == ord(' ') and gaze is not None and gaze != np.inf and len(gaze) == 2:
            corners.append(np.average(gaze, 0))
    elif gaze is not None and gaze != np.inf and len(gaze) == 2:
        pos = gaze_pos(np.average(gaze, 0))
        if 0 < pos[0] < 1 and 0 < pos[1] < 1:
            cv2.circle(blank_image, tuple((np.array(pos) * np.array(real_dims)).astype(int)), 8, (255, 255, 255), 16)

    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("window", blank_image)
    cv2.imshow("image", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
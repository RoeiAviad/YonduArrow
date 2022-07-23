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

def gaze_pos(gaze):
    global corners, real_dims
    x = round_parts((gaze[0] - corners[0][0]) / (corners[1][0] - corners[0][0]), 20)
    y = round_parts((gaze[1] - corners[0][1]) / (corners[3][1] - corners[0][1]), 20)
    relative = 0.02 if x <= 0 else 0.98 if x >= 1 else x, 0.02 if y <= 0 else 0.98 if y >= 1 else y
    return int(relative[0] * real_dims[0]), int(relative[1] * real_dims[1])

def round_parts(num, parts):
    return round(num * parts) / parts

def putText(img, text, num):
    font = cv2.FONT_HERSHEY_DUPLEX
    textsize = cv2.getTextSize(text, font, 1.6, 2)[0]
    textX = (img.shape[1] - textsize[0]) // 2
    textY = ((img.shape[0] + textsize[1]) // 10) * num
    cv2.putText(blank_image, text, (textX, textY), font, 1.6, (255, 0, 0))

DIMS = (640, 480)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('weights/shape_68.dat')

cap = cv2.VideoCapture(0)
ret, img = cap.read()

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

    nose = None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)
        nose = shape[27]

    blank_image = np.zeros(shape=[real_dims[1], real_dims[0], 3], dtype=np.uint8)
    
    if len(corners) < 4:
        putText(blank_image, "Look at the dot and press Space!", 4)
        putText(blank_image, "MOVE your head.", 5)
        cv2.circle(blank_image, dim_corners[len(corners)], 4, (255, 0, 0), 8)
        if cv2.waitKey(1) & 0xFF == ord(' ') and nose is not None:
            corners.append(nose)
    elif nose is not None:
        pos = gaze_pos(nose)
        cv2.circle(blank_image, pos, 8, (255, 255, 255), 16)
    
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("window", blank_image)
    # cv2.imshow("image", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
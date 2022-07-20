import cv2
import numpy as np

S, F, D0 = 7.069, 0, 30.0
DIMS = (640, 480)

def distance(P):
    global S, F
    if P < 100:
        return -1
    res = (S * F) / P
    if res <= 32.0:
        return 30.0
    return D0 + (res - D0) ** 0.75

def minimize(frame):
    into_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    L_limit = np.array([36, 25, 25])
    U_limit = np.array([86, 255, 255])
    g_mask = cv2.inRange(into_hsv, L_limit, U_limit)
    green = cv2.bitwise_and(frame, frame, mask=g_mask)
    
    green = cv2.cvtColor(green, cv2.COLOR_BGR2GRAY)
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
    bg = cv2.morphologyEx(green, cv2.MORPH_DILATE, se)
    out_gray = cv2.divide(green, bg, scale=255)
    out_binary = cv2.threshold(out_gray, 0, 255, cv2.THRESH_OTSU)[1] 
    converted_img = cv2.cvtColor(out_binary, cv2.COLOR_GRAY2BGR)
    dst = cv2.fastNlMeansDenoisingColored(converted_img, None, 100, 100, 7, 21)

    return dst

image = cv2.imread("images/30cm.png")
image = cv2.resize(image, DIMS)
print(image.shape)
temp = minimize(image)
temp_x, temp_y, temp_z = np.where(temp > (150, 150, 150))
F = (D0 * temp_x.shape[0]) / S

cap = cv2.VideoCapture(0)
 
while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, DIMS)

    dst = minimize(frame)

    x, y, z = np.where(dst > (150, 150, 150))
    points = (x.mean(), y.mean())
    print(points)

    print(distance(x.shape[0]))

    # cv2.imshow('Original', frame)
    cv2.imshow('Green Detector', dst)
 
    if cv2.waitKey(1) == 27:      # ESC
        # cv2.imwrite("30cm.png", frame)
        break
cap.release()
 
cv2.destroyAllWindows()
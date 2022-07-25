from cvzone.HandTrackingModule import HandDetector
import cv2
import dlib
import numpy as np

class ImageDetector():
	
	def __init__(self):
		self.cap = cv2.VideoCapture(0)
		self.hands_detector = HandDetector(detectionCon=0.8, maxHands=2) 
		self.eyes_detector = dlib.get_frontal_face_detector()
		self.eyes_predictor = dlib.shape_predictor('weights/shape_68.dat')
		self.corners = []
		
	def detect_hand(self):
		success, img = self.cap.read()
		hands, img = self.hands_detector.findHands(img)  # find hands

		if hands:
			hand = hands[1] if len(hands) > 1 and hands[1]["type"] == "Right" else hands[0]
			handType = hand["type"]  # Handtype Left or Right
			fingers = self.detector.fingersUp(hand)      # which fingers are up
			return handType == "Right", all(finger == 0 for finger in fingers[1:])
		return False, False
	
	def detect_eyes(self):
		pass
		
	def shape_to_np(shape, dtype="int"):
		coords = np.zeros((68, 2), dtype=dtype)
		# for i in range(0, 68):
		# 	coords[i] = (shape.part(i).x, shape.part(i).y)
		coords[27] = (shape.part(27).x, shape.part(27).y)
		return coords

	def gaze_pos(gaze):
		global corners, real_dims
	
		def round_parts(num, parts):
			return round(num * parts) / parts
	
		x = round_parts((gaze[0] - corners[0][0]) / (corners[1][0] - corners[0][0]), 20)
		y = round_parts((gaze[1] - corners[0][1]) / (corners[3][1] - corners[0][1]), 20)
		relative = 0.02 if x <= 0 else 0.98 if x >= 1 else x, 0.02 if y <= 0 else 0.98 if y >= 1 else y
		return int(relative[0] * real_dims[0]), int(relative[1] * real_dims[1])
	
	def __del__(self):
		self.cap.release()

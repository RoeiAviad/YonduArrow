from cvzone.HandTrackingModule import HandDetector
import cv2
import dlib
import numpy as np


class ImageDetector:
	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, "instance"):
			cls.instance = super(ImageDetector, cls).__new__(cls)
		return cls.instance

	def __init__(self, size):
		if hasattr(self, "size"):
			return
		self.size = size
		self.cap = cv2.VideoCapture(0)
		self.hands_detector = HandDetector(detectionCon=0.8, maxHands=2)
		self.eyes_detector = dlib.get_frontal_face_detector()
		self.eyes_predictor = dlib.shape_predictor('weights/shape_68.dat')
		self.corners = []
		self.img = None

	def process(self):
		self.img = self.cap.read()[1]

	def detect_hand(self):
		hands = self.hands_detector.findHands(self.img, draw=False)  # find hands

		if hands:
			hand = hands[1] if len(hands) > 1 and hands[1]["type"] == "Right" else hands[0]
			handType = hand["type"]  # Handtype Left or Right
			fingers = self.hands_detector.fingersUp(hand)  # which fingers are up
			return handType == "Right", all(finger == 0 for finger in fingers[1:])
		return False, False

	def detect_gaze(self):
		nose = None
		gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
		rects = self.eyes_detector(gray, 0)
		for rect in rects:
			shape = self.eyes_predictor(gray, rect)
			# shape = self.shape_to_np(shape)
			nose = self.get_nose(shape)

		if len(self.corners) < 4:
			if nose is not None:
				self.corners.append(nose)
				nose = None

		return self.gaze_pos(nose)

	def get_nose(self, shape):
		return shape.part(27).x, shape.part(27).y

	def shape_to_np(self, shape, dtype="int"):
		coords = np.zeros((68, 2), dtype=dtype)
		for i in range(0, 68):
			coords[i] = (shape.part(i).x, shape.part(i).y)
		return coords

	def gaze_pos(self, gaze):
		if gaze is None:
			return

		def round_parts(num, parts):
			d = round(num * parts) / parts
			return max(min(d, 0.98), 0.02)

		x = round_parts((gaze[0] - self.corners[0][0]) / (self.corners[1][0] - self.corners[0][0]), 20)
		y = round_parts((gaze[1] - self.corners[0][1]) / (self.corners[3][1] - self.corners[0][1]), 20)
		return x * self.size.x, y * self.size.y

	def __del__(self):
		self.cap.release()

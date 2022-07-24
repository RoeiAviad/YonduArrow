from cvzone.HandTrackingModule import HandDetector
import cv2

class Hands():
	
	def __init__(self):
		self.cap = cv2.VideoCapture(0)
		self.detector = HandDetector(detectionCon=0.8, maxHands=2)
		
	def detect(self):
		success, img = self.cap.read()
		hands, img = self.detector.findHands(img)  # find hands

		if hands:
			# Hand 1
			hand = hands[0]

			handType = hand["type"]  # Handtype Left or Right
			fingers = self.detector.fingersUp(hand)      # which fingers are up
			
			return handType == "Right", all(finger == 0 for finger in fingers[1:])
		return False, False
	
	def __del__(self):
		self.cap.release()

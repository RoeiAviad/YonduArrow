from cvzone.HandTrackingModule import HandDetector
import cv2

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=2)
while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)  # find hands

    if hands:
        # Hand 1
        hand = hands[0]
        lmList = hand["lmList"]  # List of 21 Landmark points
        bbox = hand["bbox"]  # Bounding box info x,y,w,h

        pointing = lmList[8]        # pointing finger x,y,?
        size = bbox[2] * bbox[3]      # caculating size of hand

        # centerPoint = hand['center']  # center of the hand cx,cy

        handType = hand["type"]  # Handtype Left or Right
        fingers = detector.fingersUp(hand)      # which fingers are up

        print(pointing)
    
    # Display
    img = cv2.flip(img, 1)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
##People counter
import numpy as np
import cv2
import Person
import time

cnt_up = 0
cnt_down = 0
count_up = 0
count_down = 0
state = 0

# Taking the video input
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output1.mkv', fourcc, 20.0, (640, 480))

##cap.set(3,160) #Width
##cap.set(4,120) #Height

# Print the capture properties to console
for i in range(19):
    print(i, cap.get(i))

w = cap.get(3)
h = cap.get(4)
frameArea = h * w
areaTH = frameArea / 300
print('Area Threshold', areaTH)

# Lines coordinate for counting
#line_up = int(1 * (h / 8))
#line_down = int(4 * (h / 4.5))
line_up = 200
line_down = 250
up_limit = int(.5 * (h / 8))
down_limit = int(4.25 * (h / 4.5))


print("Red line y:", str(line_down))
print("Blue line y:", str(line_up))
line_down_color = (255, 0, 0)
line_up_color = (0, 0, 255)
pt1 = [0, line_down];
pt2 = [w, line_down];
pts_L1 = np.array([pt1, pt2], np.int32)
pts_L1 = pts_L1.reshape((-1, 1, 2))
pt3 = [0, line_up];
pt4 = [w, line_up];
pts_L2 = np.array([pt3, pt4], np.int32)
pts_L2 = pts_L2.reshape((-1, 1, 2))

pt5 = [0, up_limit];
pt6 = [w, up_limit];
pts_L3 = np.array([pt5, pt6], np.int32)
pts_L3 = pts_L3.reshape((-1, 1, 2))
pt7 = [0, down_limit];
pt8 = [w, down_limit];
pts_L4 = np.array([pt7, pt8], np.int32)
pts_L4 = pts_L4.reshape((-1, 1, 2))

# Background Substractor
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

# Structuring elements for morphographic filters
kernelOp = np.ones((3, 3), np.uint8)
kernelOp2 = np.ones((5, 5), np.uint8)
kernelCl = np.ones((11, 11), np.uint8)

# Variables
font = cv2.FONT_HERSHEY_SIMPLEX
persons = []
rect_co = []
max_p_age = 1
pid = 1
val = []

while (cap.isOpened()):
    ##for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    ##    frame = image.array

    # for i in persons:
    #     print i.age_one() #age every person one frame
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    print(frame1.shape)
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Apply background subtraction

    # Binarization to eliminate shadows


    #   CONTOURS   #


    # RETR_EXTERNAL returns only extreme outer flags, child contours are left behind.
    for cnt in contours:
        rect = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        if area > 15000:
            #   TRACKING    #
            M = cv2.moments(cnt)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            x, y, w, h = cv2.boundingRect(cnt)
            if(h/w > 1):
                continue
            # print 'working'
            # print w

            new = True
            if cy in range(up_limit, down_limit):
                for i in persons:
                    if abs(cx - i.getX()) <= w and abs(cy - i.getY()) <= h:
                        # the object is close to one that has already been detected before
                        # print 'update'
                        new = False
                        i.updateCoords(cx, cy)  # update coordinates in the object and resets age
                        if i.going_UP(line_down, line_up) == True:
                            if w > 200:
                                count_up = count_up + 1
                                # cnt_up += count_up
                                print()
                            else:
                                cnt_up += 1;
                            print("ID:", i.getId(), 'crossed going up at', time.strftime("%c"))
                        elif i.going_DOWN(line_down, line_up) == True:
                            if w > 200:
                                count_down = count_down + 1
                                # cnt_down += count_down
                            else:
                                cnt_down += 1;
                            print("ID:", i.getId(), 'crossed going down at', time.strftime("%c"))
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut():
                        # get out of the people list
                        index = persons.index(i)
                        persons.pop(index)
                        del i  # free the memory of i
                if new == True:
                    p = Person.MyPerson(pid, cx, cy, max_p_age)
                    persons.append(p)
                    pid += 1
                    # new = True


            #   DRAWINGS     #
            cv2.circle(frame1, (cx, cy), 5, (0, 0, 255), -1)
            img = cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # cv2.drawContours(frame, cnt, -1, (0,255,0), 3)

    # END for cnt in contours0


    # DRAWING TRAJECTORIES  #

    for i in persons:
        cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv2.LINE_AA)

    # DISPLAY ON FRAME#
    str_up = 'UP: ' + str(cnt_up + count_up)
    str_down = 'DOWN: ' + str(cnt_down + count_down)

    frame = cv2.polylines(frame1, [pts_L1], False, line_down_color, thickness=2)
    frame = cv2.polylines(frame1, [pts_L2], False, line_up_color, thickness=2)

    frame = cv2.polylines(frame1, [pts_L3], True, (255, 255, 255), thickness=1)
    frame = cv2.polylines(frame1, [pts_L4], False, (255, 255, 255), thickness=1)
    cv2.putText(frame1, str_up, (10, 40), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame1, str_up, (10, 40), font, 2, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(frame1, str_down, (10, 90), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame1, str_down, (10, 90), font, 2, (255, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(frame1, "Total People in Store: " + str(count_up - count_down), (200, 200), font, 1, (255, 0, 0), 2)
    cv2.putText(frame1, "+/- " + str( (cnt_up + count_up - cnt_down + count_down)*0.1 ), (300, 300), font, 1, (255, 0, 0), 2)



    out.write(frame1)
    cv2.imshow('Frame', frame1)
    #cv2.imshow('Mask',mask)

    # Press ESC to exit
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
# END while(cap.isOpened())


#   CLOSING    #

cap.release()
cv2.destroyAllWindows()
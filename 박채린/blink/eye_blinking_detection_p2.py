import cv2
import numpy as np
import dlib
from math import hypot
import time

cap = cv2.VideoCapture(0)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

blink_record = []  # 눈 깜빡임 시간 기록 [open/close, time]
previous_record = True  # 눈을 뜨고 시작한다고 가정
start_open_time = time.time()  # 눈을 뜨기 시작한 시간
end_close_time = time.time()
# correct_time_start = time.time()  # 시간 보정용
open_num = 0
close_num = 0


def midpoint(p1, p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)


font = cv2.FONT_HERSHEY_PLAIN


def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(
        eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(
        eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(
        eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(
        eye_points[5]), facial_landmarks.part(eye_points[4]))

    hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
    ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

    hor_line_lenght = hypot(
        (left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot(
        (center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_lenght / ver_line_lenght
    return ratio


while True:
    now_time = time.time()
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    for face in faces:
        #x, y = face.left(), face.top()
        #x1, y1 = face.right(), face.bottom()
        #cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)

        landmarks = predictor(gray, face)

        left_eye_ratio = get_blinking_ratio(
            [36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio(
            [42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

        if blinking_ratio > 5.7:
            cv2.putText(frame, "CLOSE", (50, 150), font, 7, (255, 0, 0))
            if previous_record == False:
                start_open_time = time.time()  # 눈 뜨기 시작한 시간
                end_close_time = time.time()
                close_num += 1
                correct_time_start = time.time()
                blink_record.append(
                    ['CLOSE'+str(close_num), end_close_time-start_close_time])
            previous_record = True
        if blinking_ratio <= 5.7:
            cv2.putText(frame, "OPEN", (50, 150), font, 7, (255, 0, 0))
            if previous_record == True:
                end_open_time = time.time()
                start_close_time = time.time()
                open_num += 1
                blink_record.append(
                    ['OPEN'+str(open_num), end_open_time-start_open_time])
                correct_time_start = time.time()
            previous_record = False

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:
        print(blink_record)
        break

cap.release()
cv2.destroyAllWindows()

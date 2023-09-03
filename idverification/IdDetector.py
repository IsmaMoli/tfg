import os
import time
import sys

import cv2
import easyocr
import face_recognition

MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15

def extract_letters(img_path):
    try:
        id_img = cv2.imread(img_path)

        if id_img.shape[0] > id_img.shape[1]:
            id_img = cv2.rotate(id_img, cv2.ROTATE_90_CLOCKWISE)

        known_encoding = face_recognition.face_encodings(id_img)
        if not known_encoding:
            id_img = cv2.rotate(id_img, cv2.ROTATE_90_CLOCKWISE)
            id_img = cv2.rotate(id_img, cv2.ROTATE_90_CLOCKWISE)
            known_encoding = face_recognition.face_encodings(id_img)
            if not known_encoding:
                return "no face"

        #gray = cv2.cvtColor(id_img, cv2.COLOR_BGR2GRAY)
        #clean = cv2.fastNlMeansDenoising(src=gray, h=3, dst=None, templateWindowSize=3, searchWindowSize=7)
        reader = easyocr.Reader(['es', 'en'], gpu=True)
        detected_text = reader.readtext(id_img, detail=0)

    except Exception as e:
        print(e)
        detected_text = "error"

    return detected_text


def check_face(img_path):
    id_img = cv2.imread(img_path)

    if id_img.shape[0] > id_img.shape[1]:
        id_img = cv2.rotate(id_img, cv2.ROTATE_90_CLOCKWISE)

    known_encoding = face_recognition.face_encodings(id_img)
    if not known_encoding:
        id_img = cv2.rotate(id_img, cv2.ROTATE_90_CLOCKWISE)
        id_img = cv2.rotate(id_img, cv2.ROTATE_90_CLOCKWISE)
        known_encoding = face_recognition.face_encodings(id_img)
        if not known_encoding:
            return False
    return True

class Id_camera_checker():
    def __init__(self, reference):
        id_img = cv2.imread(reference)

        if id_img.shape[0] > id_img.shape[1]:
            id_img = cv2.rotate(id_img, cv2.ROTATE_90_CLOCKWISE)

        id_img = cv2.GaussianBlur(id_img, (3, 3), 0)
        id_small = cv2.resize(id_img, [400, 250])

        id_grey = cv2.cvtColor(id_small, cv2.COLOR_BGR2GRAY)
        self.sift = cv2.SIFT_create()
        self.keypoints1, self.descriptors1 = self.sift.detectAndCompute(id_grey, None)

        self.bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
        self.max_confidence =0


    def process_frame(self, frame):

        frame_target = cv2.rectangle(frame, [120, 120], [520, 370], (0, 204, 0), 5)

        if self.max_confidence > 98:
            cv2.rectangle(frame_target, [40, 400], [580, 445], (0, 0, 0), -1)
            cv2.putText(frame_target, "Verificacio completada, Continua", [50, 430],
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            num_good_matches = 0
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            keypoints2, descriptors2 = self.sift.detectAndCompute(gray, None)

            matches = self.bf.match(self.descriptors1, descriptors2)
            matches = sorted(matches, key=lambda x: x.distance)
            num_good_matches = int(len(matches) * GOOD_MATCH_PERCENT)
            cv2.rectangle(frame_target, [120, 400], [540, 445], (0, 0, 0), -1)
            cv2.putText(frame_target, "Nivell de coincidencia: " + str(num_good_matches*3), [130, 430],
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            self.max_confidence = max(self.max_confidence, num_good_matches*3)

        ret, jpeg = cv2.imencode('.jpg', frame_target)
        return [num_good_matches >= 33,  jpeg.tobytes(), frame]


class Face_camera_check():
    def __init__(self,reference):
        id_img = cv2.imread(reference)

        self.known_encoding = face_recognition.face_encodings(id_img)
        if not self.known_encoding:
            id_img = cv2.rotate(id_img, cv2.ROTATE_90_CLOCKWISE)
            id_img = cv2.rotate(id_img, cv2.ROTATE_90_CLOCKWISE)
            self.known_encoding = face_recognition.face_encodings(id_img)

        self.n = 0
        self.message = ""
        self.faces = []

    def process_frame(self, frame):
        if self.n % 4 == 0 and self.message != "Ok! Finalitza":
            self.message = check_match(self.known_encoding, frame)

        cv2.rectangle(frame, [150, 400], [470, 445], (0, 0, 0), -1)
        cv2.putText(frame, self.message, [165, 430], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        if (self.message == "Rostre Desconegut" and self.n % 20 and len(self.faces)<5):
            self.faces.append(frame)


        self.n += 1
        ret, jpeg = cv2.imencode('.jpg', frame)
        return [self.message=="Ok! Finalitza", jpeg.tobytes(), self.faces, frame]


def check_match(known_encoding, frame):
    try:
        m = ""
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame)
        if face_encodings:
            for encoding, location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_encoding, encoding, 0.55)
                for match in matches:
                    if match:
                        m = "Ok! Finalitza"
                    elif m != "Ok! Finalitza":
                        m = "Rostre Desconegut"
        else:
            m = "Cap rostre detectat"
    except Exception:
        m = "Image no valida"
    return m

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        time.sleep(0.1)
        image = None
        while image is None:
            success, image = self.video.read()
        frame_flip = cv2.flip(image, 1)
        return frame_flip

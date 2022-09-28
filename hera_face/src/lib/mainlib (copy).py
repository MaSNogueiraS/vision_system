from fnmatch import fnmatch
from re import A, I
import dlib
import matplotlib.pyplot as plt
import numpy as np
import os
from pyexpat import model
import fnmatch
import cv2
from cv_bridge import CvBridgeError


def euclidean(x, y):
    return np.sqrt(np.sum((x - y) ** 2))


detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("/home/robofei/catkin_hera/src/3rdParty/vision_system/hera_face/src/lib/shape_predictor_5_face_landmarks.dat")
model  = dlib.face_recognition_model_v1("/home/robofei/catkin_hera/src/3rdParty/vision_system/hera_face/src/lib/dlib_face_recognition_resnet_model_v1.dat")

people_dir = "/home/robofei/catkin_hera/src/3rdParty/vision_system/hera_face/src/lib/face_images/"
files = fnmatch.filter(os.listdir(people_dir), '*.jpg')

# Load all the images that we want to compare and already have
images = []
known_face = []
known_name = []

for f in range(0, len(files)):
    for j in range(0,100):
        img = dlib.load_rgb_image(people_dir + files[f])
        img_detected = detector(img, 1)
        img_shape = sp(img, img_detected[0])
        align_img = dlib.get_face_chip(img, img_shape)
        img_rep = np.array(model.compute_face_descriptor(align_img))
        if len(img_detected) > 0:
            known_face.append(img_rep)
            known_name.append(files[f].split('.')[0])
            break
        else:
            print("No face detected in image: " + files[f])
            break

print(known_name)
# Load the image in real time, have to change the path to de video capture
#small_frame = cv2.imread("/home/robofei/catkin_hera/src/3rdParty/vision_system/hera_face/src/lib/face_images/teste.jpg")


#open camera   
video_capture = cv2.VideoCapture(0)
while video_capture.isOpened():
    _,small_frame = video_capture.read()
    # Detect the faces in the image
    try:
        img_detected = detector(small_frame, 1)
        img_shape = sp(small_frame, img_detected[0])
        align_img = dlib.get_face_chip(small_frame, img_shape)
        img_rep = np.array(model.compute_face_descriptor(align_img))
        
        # Compare the face in real time with the faces that we already have
        #aux = 1
        #compare each face in the image with the faces in the database
        for i in range(0, len(img_rep)):
            name = "Face"
            face_name = []
            for j in range(0, len(known_face)):
                euclidean_dist = list(np.linalg.norm(known_face - img_rep, axis=1) <= 0.6)
                if True in euclidean_dist:
                    fst = euclidean_dist.index(True)
                    name = known_name[fst]
                    print("Face detected: " + name)
                    break

            face_name.append(name)
        #print(face_name)
        #bounding box
        for face, name in zip(img_detected, face_name):
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            cv2.rectangle(small_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(small_frame, name, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        
    except CvBridgeError as e:
        print(e)
    # Show the image
    cv2.imshow('Video', small_frame)

    cv2.waitKey(5) & 0xFF == ord('q')


video_capture.release()
cv2.destroyAllWindows()
        #close all open windows

    

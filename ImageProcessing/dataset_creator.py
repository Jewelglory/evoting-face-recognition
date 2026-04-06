import cv2
import numpy as np
import os

dataset_dir = 'dataset'
if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir)

faceDetect = cv2.CascadeClassifier(r'''haarcascade_frontalface_alt2.xml''');
cam = cv2.VideoCapture(0);

id=input('enter the user id');
sampleNum=0;
while(cv2.waitKey(1)!=27):
    ret,img = cam.read();
    print(img);
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray,1.3,5);
    for(x,y,w,h) in faces:
        sampleNum=sampleNum+1;
        cv2.imwrite(f"{dataset_dir}/User.{id}.{sampleNum}.png", gray[y:y+h, x:x+w])
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,225),2)
        cv2.waitKey(100);
    cv2.imshow("Face",img);
    cv2.waitKey(1);
    if(sampleNum>100):
        break;
cam.release()
cv2.destroyAllWindows()

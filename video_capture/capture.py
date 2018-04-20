# coding:utf-8
import cv2, time

def main():
    cap = cv2.VideoCapture(0)
    # get a frame
    ret, frame = cap.read()
    cv2.imwrite("%d.jpg" % 1, frame)
    cap.release()

if __name__ == '__main__':
    main()


from django.db import models
from imutils import paths

import argparse
import cv2
import io
import numpy as np
import os, io


DIR_PATH = os.path.dirname(os.path.abspath(__file__))
FACE_CASCADE_FILE = os.path.join(DIR_PATH, "haarcascade_frontalface_default.xml")


class Image():

    def __init__(self, image):
        """
        Takes an image file-like object
        """
        print(image)
        self.image = image
        self.face_cascade = cv2.CascadeClassifier(FACE_CASCADE_FILE)

    def get_string(self):
        return self.get_bytes().decode("utf-8")

    def get_cropped(self, image_box):
        """
        Return a subset of self.image cropped to the given `image_box`
        Returns a file-like object with the new image in it
        """
        print("crop coords")
        print("{} {} {} {}".format(image_box.y, image_box.h, image_box.x, image_box.w))

        cropped_opencv_image = self.get_opencv_image()[image_box.y:image_box.y+image_box.h, image_box.x:image_box.x+image_box.w]

        _, buffer = cv2.imencode(".jpg", cropped_opencv_image)
        new_file = io.BytesIO(buffer)
        return Image(new_file)

    def get_largest_face_box(self):
        face_boxes = self.get_face_boxes()
        face_boxes.sort(key=lambda x: x.get_area(), reverse=True)

        return face_boxes[0]

    def get_face_boxes(self):
        """
        Checks self.image for faces
        Creates a list of `ImageBox` objects, one for each face found
        Returns the list of `ImageBox` objects
        """
        gray = cv2.cvtColor(self.get_opencv_image(), cv2.COLOR_BGR2GRAY)
        face_boxes = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        face_boxes = [ImageBox(*face_box) for face_box in face_boxes]

        return face_boxes

    def get_opencv_image(self, gray_scale=False):
        """
        Returns a version of self.image which can be used by opencv
        """
        self.image.seek(0)
        #convert self.image to bytes
        bytes_image = self.image.read()

        #handling for imdecode
        nparr = np.fromstring(bytes_image, np.uint8)

        #load the image
        if gray_scale:
            return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        else:
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def check_quality(self):
        im = self.get_opencv_image(gray_scale=True)
        print("IMG SHAPE")
        print(im.shape)
        cv2.imwrite("cropped_check.jpg", im)

        #compute the focus measure of the image using Variance of Laplacian method
        fm = cv2.Laplacian(im, cv2.CV_64F).var()

        print(fm)
        return fm


class ImageBox:
    
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def get_coordinates(self):
        return [int(self.x), int(self.y), int(self.w), int(self.h)]

    def get_adjusted(self, image, amount=None, percent=None):
        """
        Takes amount or percent
        Adjusts the dimensions of this `ImageBox` accordingly
        """
        if percent is not None:
            # Calculate amount to adjust by based on size of w and h
            l = max([self.w, self.h])
            amount = int(l * (percent / 100.0))

        new_w = self.w + amount * 2
        new_h = self.h + amount * 2
        new_x = self.x - amount
        new_y = self.y - amount

        new_face_box = ImageBox(new_x, new_y, new_w, new_h)
        new_face_box.validate(image)

        return new_face_box

    def validate(self, image):
        """
        Takes an `image` object
        Checks to make sure that this `ImageBox` is completely within the given image
        Adjusts the x, y, w, and h if they are out of bounds
        """
        height, width, channels = image.get_opencv_image().shape

        if self.x < 0:
            self.x = 0

        if self.y < 0:
            self.y = 0

        error = (self.w + self.x) - width
        if error > 0:
            self.w -= error

        error = (self.h + self.y) - height
        if error > 0:
            self.h -= error

    def get_area(self):
        return self.w * self.h

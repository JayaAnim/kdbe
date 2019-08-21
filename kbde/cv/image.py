from django.db import models
from imutils import paths

import argparse
import cv2
import PIL
import piexif
import numpy as np
import os, io


DIR_PATH = os.path.dirname(os.path.abspath(__file__))
FACE_CASCADE_FILE = os.path.join(DIR_PATH, "haarcascade_frontalface_default.xml")


class Image():

    def __init__(self, image):
        """
        Takes an image file-like object
        """
        self.image = image
        self.face_cascade = cv2.CascadeClassifier(FACE_CASCADE_FILE)

    def get_string(self):
        return self.get_bytes().decode("utf-8")

    def get_cropped(self, image_box):
        """
        Creates a subset of self.image cropped to the given `image_box`
        Creates a new `Image` object with the subset
        Returns the `Image` object
        """
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

        #compute the focus measure of the image using Variance of Laplacian method
        fm = cv2.Laplacian(im, cv2.CV_64F).var()
        return fm

    def remove_ios_orientation_exif(self):
        """
        Checks self.image exif data for iOS orientation data
        If found: removes from image, returns `True`
        Else: does nothing, returns false
        """
        img = PIL.Image.open(self.image)
        if "exif" in img.info:
            exif_dict = piexif.load(img.info['exif'])

            if piexif.ImageIFD.Orientation in exif_dict["0th"]:
                img_format = img.format

                orientation = exif_dict["0th"][piexif.ImageIFD.Orientation]

                if orientation == 1:
                    return False
                elif orientation == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    img = img.rotate(180)
                elif orientation == 4:
                    img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 5:
                    img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    img = img.rotate(-90, expand=True)
                elif orientation == 7:
                    img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)

                exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
                exif_bytes = piexif.dump(exif_dict)

                output_file = io.BytesIO()
                img.save(output_file, format=img_format, exif=exif_bytes)

                self.image = output_file
                return True

        return False


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

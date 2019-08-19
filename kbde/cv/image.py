from django.db import models
from imutils import paths

import argparse
import cv2
import io
import numpy as np


class Image():

    def __init__(self, image):
        """
        Takes an image file-like object
        """
        self.image = image

    def __str__(self):
        pass
        # TODO

    def get_coordinates(self):
        pass
        # TODO

    def get_cropped(self, image_box):
        """
        Return a subset of self.image cropped to the given `image_box`
        Returns a file-like object with the new image in it
        """
        # TODO

    def get_face_boxes(self):
        """
        Checks self.image for faces
        Creates a list of `ImageBox` objects, one for each face found
        Returns the list of `ImageBox` objects
        """
        # TODO

    def get_opencv_image(self):
        """
        Returns a version of self.image which can be used by opencv
        """
        # TODO

    def check_quality(self):
        self.image.seek(0)
        #convert self.image to bytes
        bytes_image = self.image.read()

        #handling for imdecode
        nparr = np.fromstring(bytes_image, np.uint8)

        #load the image in greyscale
        im = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        #compute the focus measure of the image using Variance of Laplacian method
        fm = cv2.Laplacian(im, cv2.CV_64F).var()

        return fm


class ImageBox:
    
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def adjust(self, amount=None, percent=None):
        """
        Takes amount or percent
        Adjusts the dimensions of this `ImageBox` accordingly
        """
        # TODO

    def validate(self, image):
        """
        Takes an `image` object
        Checks to make sure that this `ImageBox` is completely within the given image
        Adjusts the x, y, w, and h if they are out of bounds
        """
        # TODO

    def get_area(self):
        return self.w * self.h

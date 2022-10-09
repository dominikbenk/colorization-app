import cv2
import numpy as np
import os
from colorize import Colorization
from color_utils import yuv_to_rgb


class Interface():
    """
    Defines graphical user interface.
        image_path - path of the image
        name - window name of the application
        bar_h - height of the top bar (pxls)
        min_bar_w - minimum window width (pxls)
        frame_size - size of the frame around images (pxls)
        scribble_path - path of the scribble (optional)
    """

    def __init__(self, image_path: str, name="Colorization App",
                 bar_h=150, min_bar_w=512, frame_size=10, scribble_path=''):
        self.image_path = image_path
        self.name = name
        self.image = cv2.imread(image_path)
        # converting to gray scale
        self.grey = np.repeat(np.reshape(
            cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY),
            (self.image.shape[0], self.image.shape[1], 1)), 3, axis=2)
        # checking if scribble was loaded
        if scribble_path != '':
            self.scribble = cv2.imread(scribble_path)
            self.s = True
        else:
            self.s = False
        self.draw = False
        # defining shapes of objects in UI
        self.frame_size = frame_size
        self.bar_h = bar_h
        self.bar_w = max(min_bar_w, self.image.shape[1] * 2 + frame_size * 4)
        self.backgr_h = bar_h + self.image.shape[0] + frame_size * 2
        self.backgr_w = self.bar_w
        self.brush_size = 4
        self.red, self.green, self.blue = 0, 100, 100
        self.background = np.full((self.backgr_h, self.backgr_w, 3),
                                  [55, 11, 2], np.uint8)
        # pointers to left and right images
        self.left_image_point = self.background[
            (frame_size+bar_h):(self.backgr_h-frame_size),
            (frame_size):(self.image.shape[1]+frame_size), :]
        self.right_image_point = self.background[
            (frame_size+bar_h):(self.backgr_h-frame_size),
            (3*frame_size+self.image.shape[1]):(self.backgr_w-frame_size), :]

    def nothing(self, x):
        pass

    def draw_circle(self, event: int, x: int, y: int,
                    flags: int, params: None):
        """
        Callback function to track mouse events
        """
        # mouse click
        if event == cv2.EVENT_LBUTTONDOWN:
            # allowing to draw only on the left image
            if (y > self.frame_size+self.bar_h and
                    y < self.backgr_h-self.frame_size and
                    x > self.frame_size+self.brush_size and
                    x < self.image.shape[1]+self.frame_size-self.brush_size):
                self.draw = True
            # otherwise color is picked
            else:
                self.blue, self.green, self.red = self.background[y, x, :]
                self.red = int(self.red)
                self.green = int(self.green)
                self.blue = int(self.blue)
        # moving mouse
        elif event == cv2.EVENT_MOUSEMOVE:
            # allowing to draw only on the left image
            if (self.draw and
                    y > self.frame_size + self.bar_h + self.brush_size and
                    y < self.backgr_h - self.frame_size - self.brush_size and
                    x > self.frame_size + self.brush_size and
                    x < self.image.shape[1] +
                    self.frame_size - self.brush_size):
                cv2.circle(self.background, (x, y),
                           self.brush_size,
                           (self.blue, self.green, self.red), -1)
        # release click
        elif event == cv2.EVENT_LBUTTONUP:
            self.draw = False
        # brush size
        elif event == 10:
            if flags > 0:
                self.brush_size = min(self.brush_size + 1, 20)
            else:
                self.brush_size = max(self.brush_size - 1, 1)

    def run(self):
        """
        Runs the interface:
            1) loads surrounding objects
            2) loads images
            3) loops until quit:
                - tracks keyboard keys and eventually performs a given action
                - tracks mouse events, allowing to paint and change the size
        """
        cv2.namedWindow(self.name)

        color_grid = cv2.imread('gui/props/color_grid.png')
        color_grid = np.transpose(color_grid, [1, 0, 2])
        info = cv2.imread('gui/props/info.png')
        self.background[5:color_grid.shape[0]+5,
                        self.frame_size:self.frame_size+color_grid.shape[1],
                        :] = color_grid
        self.background[7:info.shape[0]+7,
                        self.frame_size+320:self.frame_size+info.shape[1]+320,
                        :] = info

        self.left_image_point[:] = self.scribble if self.s else self.grey
        self.right_image_point[:] = self.image

        cv2.setMouseCallback(self.name, self.draw_circle)

        while(True):
            cv2.imshow(self.name, self.background)
            key = cv2.waitKey(1) & 0xff
            # quit
            if key == ord('q') or key == 27:
                break
            # save
            if key == ord('s'):
                split = os.path.splitext(self.image_path)
                cv2.imwrite(split[0]+'_scribble'+'.bmp',
                            self.left_image_point[:])
                cv2.imwrite(split[0]+'_colorized'+'.bmp',
                            self.right_image_point[:])
            # reload
            if key == ord('r'):
                self.left_image_point[:] =\
                    self.scribble if self.s else self.grey
                self.right_image_point[:] = self.image
            # colorize
            if key == ord('c'):
                self.scribble = self.left_image_point[:]
                self.colorized_YUV = Colorization(self.grey,
                                                  self.scribble).optimize()
                self.colorized = yuv_to_rgb(self.colorized_YUV)
                self.right_image_point[:] = self.colorized * 255
            # brush size circle
            cv2.circle(self.background,
                       (color_grid.shape[1] + 25 + self.frame_size * 2, 25),
                       20, (0, 0, 0), -1)
            cv2.circle(self.background,
                       (color_grid.shape[1] + 25 + self.frame_size * 2, 25),
                       self.brush_size, (self.blue, self.green, self.red), -1)

        cv2.destroyAllWindows()
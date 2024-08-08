import cv2
import numpy as np
from pyautogui import screenshot
from PIL import Image


def image_skeleton(image):
    size = np.size(image)
    skel = np.zeros(image.shape, np.uint8)
    
    ret, img = cv2.threshold(image, 127, 255, 0)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    done = False
    while not done:
        eroded = cv2.erode(img, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img = eroded.copy()
        
        zeros = size - cv2.countNonZero(img)
        if zeros == size:
            done = True
    return skel

def get_hough_lines(image):
    edges = cv2.Canny(image, 50, 150, apertureSize=7)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    edges = image_skeleton(edges)
    # cv2.imshow("Edges", edges)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 400)
    lines = lines.reshape(-1, 2)
    # print(lines)
    return lines



def get_cardinal_lines(lines):
    mask = (lines[:, 1] == 0 ) | (lines[:, 1] == np.pi/2)
    return lines[mask, :]

def line_coords(lines):
    # print(lines)
    horizontal = lines[lines[:, 1] == np.pi/2,0]
    vertical = lines[lines[:, 1] == 0,0]

    return horizontal, vertical

def draw_lines(image, lines):
    
    for rho, theta in lines:
        
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    return image

def get_image_lines(image):
    if isinstance(image, Image.Image):
        print(type(image))
        
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    lines = get_hough_lines(image)
    # cv2.imshow("Lines", draw_lines(image, lines))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    lines = line_coords(lines)
    return lines

if __name__ == "__main__":
    image = cv2.imread("first_ss.png", 0)
    
    lines = get_hough_lines(image)
    cv2.imshow("Lines", draw_lines(cv2.cvtColor(image, cv2.COLOR_GRAY2BGR), lines))
    lines = get_cardinal_lines(lines)
    cv2.imshow("Lines 2", draw_lines(cv2.cvtColor(image, cv2.COLOR_GRAY2BGR), lines))
    print(line_coords(lines))
    # form_lines = get_cardinal_lines(lines)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
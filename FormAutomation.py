import time
import numpy as np
from pyautogui import screenshot, locateAll, locateAllOnScreen, click, moveTo, size, scroll, move
from requests import post

from ImageProcessing import get_image_lines

# box is a tuple of 4 values: (left, top, width, height)
# ((x1,y1), (x2,y2).... (x3,x4))
class Box:
    def __init__(self, box) -> None:
        # when l, t, w, h
        if isinstance(box, tuple) and len(box) == 4 and all(isinstance(i, (int, float)) for i in box):
            self.l, self.t, self.w, self.h = box
            self.vertices = ((self.l, self.t), (self.l + self.w, self.t), 
                            (self.l + self.w, self.t + self.h), (self.l, self.t + self.h))
            self.centre = (self.l + self.w / 2, self.t + self.h / 2)
            self.box_tuple = box
        # when vertices
        elif isinstance(box, tuple) and len(box) == 4 and all(isinstance(i, tuple) and len(i) == 2 for i in box):
            self.vertices = box
            self.l, self.t = box[0]
            self.w = box[1][0] - box[0][0]
            self.h = box[2][1] - box[1][1]
            self.box_tuple = (self.l, self.t, self.w, self.h)
            self.centre = (self.l + self.w / 2, self.t + self.h / 2)
        else:
            raise ValueError("Invalid input format for Box")
    def __str__(self) -> str:
        return f"{self.box_tuple}"
    def __repr__(self) -> str:
        return f"{self.box_tuple}"
    def is_within(self, box):
        return self.l >= box.l and self.t >= box.t and self.l + self.w <= box.l + box.w and self.t + self.h <= box.t + box.h

class ScreenShot:
    def __init__(self, box, file_path=None) -> None:
        self.box = Box(box)
        self.ss = screenshot(region=(self.box.l, self.box.t, self.box.w, self.box.h), imageFilename=file_path).convert('RGB')
        self.path = file_path
        
        # self.screen_size = size()
    
    def find_all_img(self, image, confidence=0.9):
        # try:
        found_coords = list(locateAll(needleImage=image, haystackImage=self.ss, confidence=confidence))
        res = []
        for coord in found_coords:
            x, y, w, h = coord
            temp_tuple = (int(x + self.box.l), int(y + self.box.t), int(w), int(h))
            box = Box(temp_tuple)
            res.append(box)
        return res

    
    def find_text(self, text_to_find, texts_all):
        for text in texts_all:
            if text["description"] == text_to_find:
                vertices = Box((vertex['x']+self.box.l, vertex['y']+self.box.t) for vertex in text["boundingPoly"]["vertices"])
                return vertices
        return None
    def find_text_in_bounds(self, text_to_find, bound_box, texts_all):
        for text in texts_all:
            if text["description"] == text_to_find:
                text_box = Box(tuple((vertex['x']+self.box.l, vertex['y']+self.box.t) for vertex in text["boundingPoly"]["vertices"]))
                if text_box.is_within(bound_box):
                    return text_box
        return None
    
    def find_all_text(self, text_to_find, texts_all):
        found_text_coords = []
        for text in texts_all:
            if text["description"] == text_to_find:
                vertices = Box((vertex['x']+self.box.l, vertex['y']+self.box.t) for vertex in text["boundingPoly"]["vertices"])
                found_text_coords.append(vertices)
        return found_text_coords
    
    def find_all_text_in_bounds(self, text_to_find, bound_box, texts_all):
        found_text_coords = []
        for text in texts_all:
            if text["description"] == text_to_find:
                text_box = Box((vertex['x']+self.box.l, vertex['y']+self.box.t) for vertex in text["boundingPoly"]["vertices"])
                if text_box.is_within(bound_box):
                    found_text_coords.append(text_box)
        return found_text_coords
    
    def find_texts(self, texts_to_find:list, texts_all):
        found_texts = {}
        for text in texts_all:
            if text["description"] in texts_to_find:
                vertices = Box(tuple((vertex['x']+self.box.l, vertex['y']+self.box.t) for vertex in text["boundingPoly"]["vertices"]))
                if not found_texts.get(text["description"]):
                    found_texts[text["description"]] = [vertices]
                found_texts[text["description"]].append(vertices)
        return found_texts

    def get_lines(self):
        lines_found = get_image_lines(self.ss)
        
        # lines_found[0] += self.box.t
        # lines_found[1] += self.box.l
        return (lines_found[0] + self.box.t, lines_found[1] + self.box.l)


class Form:
    def __init__(self, heading:str, heading_box:Box, border_box:Box) -> None:
        self.heading = heading
        self.heading_box = heading_box
        self.buttons = []
        self.border_box = border_box
        self.ss = None
        self.ss = ScreenShot(self.border_box.box_tuple, f"form_{self.heading}.png")
        self.button_path = "button.png"
        self.selected_button_path = "button_selected.png"
        
    def find_buttons(self, button_img, confidence):
        try:
            self.buttons = self.ss.find_all_img(self.button_path, confidence)
        except:
            pass
        
        try:
            self.buttons += self.ss.find_all_img(self.selected_button_path, confidence)
        except:
            pass

        # self.buttons += self.ss.find_all_img("button_selected.png", confidence)
        self.buttons = sort_boxes(self.buttons)
        
        return self.buttons
    def click_all_buttons(self):
        for button in self.buttons:
            moveTo(button.centre)
            # click()
            time.sleep(1)
    
    
def find_all_img_in_bounds(image, bound_box, confidence):

    ss_in_bounds = ScreenShot(bound_box.box_tuple, "temp_ss.png")
    found_coords = ss_in_bounds.find_all_img(image, confidence)
    return found_coords

    
# array of boxes, should be smallest x value first and smallest y value first
def sort_boxes(boxes):
    boxes.sort(key=lambda x: x.l)
    boxes.sort(key=lambda x: x.t)
    return boxes
server_url = 'https://googlecloudapi.vercel.app/api/v1'

def get_annotations(ss:ScreenShot):
    with open(ss.path, 'rb') as image:
        response = post(f'{server_url}/image/annotations', files={'file': image})
        return response.json()


def old_main():
    time.sleep(2)
    screen_size = size()
    form_heading_options = {
        "M1800":"02",
        "M1810":"03",
        "M1820":"01",
        "M1830":"05",
        "M1840":"04",
        "M1845":"00",
        "M1850":"02",
        "M1860":"01"
    }
    form_heading_options_index = {
        "M1800":2,
        "M1810":3,
        "M1820":1,
        "M1830":5,
        "M1840":4,
        "M1845":0,
        "M1850":2,
        "M1860":1,
        "D0150F1":0,
        "D0150F2 Symptom":0
    }
    remaining_forms = list(form_heading_options_index.keys())
    while len(remaining_forms) > 1:
        time.sleep(1)
        # important: the screen size is the size of the screen without the taskbar
        screen_ss = ScreenShot((0, 120, screen_size[0], screen_size[1]-120-80), "first_ss.png")
    
        response = get_annotations(screen_ss)
        annotations = response["data"]["textAnnotations"]
        
        found_headings_boxes = screen_ss.find_texts(remaining_forms, annotations)
        print(found_headings_boxes)
        found_headings = list(found_headings_boxes.keys())
        forms_on_screen = {}
        for i in range(len(found_headings)):
            heading_box = found_headings_boxes[found_headings[i]]
            # next_heading_box = found_headings_boxes[found_headings[i+1]]
            
            # lines = form_lines(screen_ss.ss)
            # print(lines)
            
            # form_box = Box((
            #     heading_box.l,
            #     heading_box.t,
            #     screen_size[0] - heading_box.l,
            #     next_heading_box.t - heading_box.t 
            # ))
            # form_obj = Form(found_headings[i], heading_box)
            # form_prelim_ss = ScreenShot(form_box.box_tuple, "temp_ss.png")
            # button_locs = form_prelim_ss.find_all_img("button.png", 0.9)
            

            lines = screen_ss.get_lines()
            horizontals, verticals = lines
            
            horizontals = horizontals[horizontals>heading_box.t]
            bottom_border = horizontals[np.argmin(horizontals)]
            
            verticals = verticals[verticals>heading_box.l+heading_box.w]
            right_border = verticals[np.argmin(verticals)]
            print(heading_box, found_headings[i])
            print(right_border, bottom_border)
            moveTo((heading_box.l, heading_box.t))
            time.sleep(1)
            
            form_box = Box((
                heading_box.l,
                heading_box.t,
                int(abs(right_border - heading_box.l)),
                int(abs(bottom_border - heading_box.t))
            ))
            form_obj = Form(found_headings[i], heading_box, form_box)
            
            # forms_on_screen[found_headings[i]] = form_box
            # button_locs = screen_ss.find_all_img("button.png",0.9)
            # if(len(button_locs) == 0):
            #     continue
            # moveTo(button_locs[form_heading_options_index[found_headings[i]]].centre)
            # click()
            # move(-50, 0)
            
            # print(button_locs)
            remaining_forms.remove(found_headings[i])
        
        # scroll(-200)
def num_within_threshold(num, target, threshold):
    return abs(num - target) < threshold

if __name__ == "__main__":
    screen_size = size()
    top_bar = 120
    bottom_bar = 80
    screen_ss = ScreenShot((0, top_bar, screen_size[0], screen_size[1]-top_bar-bottom_bar), "first_ss.png")
    
    lines = screen_ss.get_lines()
    # print(lines)
    horizontals, verticals = lines
    headings_choices = {
        "D0150B1":3,
        "D0150B2":2,
        "D0150C1":1,
    }
    
    annotations = get_annotations(screen_ss)["data"]["textAnnotations"]
    found = screen_ss.find_texts(headings_choices.keys(), annotations)
    headings_boxes = {}
    for heading, boxes in found.items():
        for box in boxes:
            for y in verticals:
                if num_within_threshold(box.l, y, 5):
                    print(box, y)
                    headings_boxes[heading] = box
                    
    print("heading text boxes:", headings_boxes)
    
    remaining_headings = list(headings_boxes.keys())
    while len(remaining_headings) > 0:
        # screen_ss = ScreenShot((0, 120, screen_size[0], screen_size[1]-120-40), "first_ss.png")
        # populate forms on screen:
        for heading in remaining_headings:
            box = headings_boxes[heading]
            lower_lines = horizontals[horizontals>box.t]
            if len(lower_lines) == 0:
                print(f"skipping {heading} ll")
                continue
            bottom_border = np.min(lower_lines)
            print(f"bottom border: {bottom_border}, box bottom: {screen_ss.box.t+screen_ss.box.h}")
            if num_within_threshold(bottom_border, screen_ss.box.t+screen_ss.box.h, 5):
                print(f"skipping {heading}")
                continue
            right_border = np.min(verticals[verticals>box.l+box.w])
            
            form_box = Box((
                box.l,
                box.t,
                int(abs(right_border - box.l)),
                int(abs(bottom_border - box.t))
            ))
            
            form_obj = Form(heading, box, form_box)
            form_obj.find_buttons("button.png", 0.9)
            # form_obj.click_all_buttons()
            print(form_obj.buttons)
            moveTo((right_border, bottom_border))
            time.sleep(2)
            remaining_headings.remove(heading)
            pass
    
    
    
    pass
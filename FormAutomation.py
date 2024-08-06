from pyautogui import screenshot, locateAll, locateAllOnScreen, click, moveTo, size, scroll, move
import time
from requests import post


# box is a tuple of 4 values: (left, top, width, height)
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
        self.ss = screenshot(region=(self.box.l, self.box.t, self.box.w, self.box.h), imageFilename=file_path)
        self.path = file_path
        
        # self.screen_size = size()
    
    def find_all_img(self, image, confidence=0.9):
        try:
            found_coords =  locateAll(image, self.ss, confidence)
            return [Box((x + self.box.l, y + self.box.t, w, h)) for x, y, w, h in found_coords]
        except:
            return []
    
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
                found_texts[text["description"]] = vertices
        return found_texts
def find_all_img_in_bounds(image, bound_box, confidence):
    return_l = []
    
    ss_in_bounds = screenshot(region=bound_box.box_tuple, imageFilename="temp.png")
    found_coords =  list(locateAll(needleImage=image, haystackImage=ss_in_bounds, confidence=confidence))
    # print(found_coords[0][0])
    for i in range(len(found_coords)):
        x, y, w, h = found_coords[i]
        # print(x, y, w, h)
        temp_tuple = (int(x + bound_box.l), int(y + bound_box.t), int(w), int(h))
        # print(temp_tuple)
        return_l.append(Box(temp_tuple))
    return return_l
    # return [Box((x + bound_box.l, y + bound_box.t, w, h)) for x, y, w, h in found_coords]
    # except:
    #     return []
    
# array of boxes, should be smallest x value first and smallest y value first
def sort_boxes(boxes):
    boxes.sort(key=lambda x: x.l)
    boxes.sort(key=lambda x: x.t)
    return boxes

def get_annotations(ss:ScreenShot):
    with open(ss.path, 'rb') as image:
        response = post(f'{server_url}/image/annotations', files={'file': image})
        return response.json()

server_url = 'https://googlecloudapi.vercel.app/api/v1'

if __name__ == "__main__":
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
        "M1860":1
        
    }
    remaining_forms = list(form_heading_options_index.keys())
    while len(remaining_forms) > 0:
        # time.sleep(2)
        screen_ss = ScreenShot((0, 120, screen_size[0], screen_size[1]-120-40), "first_ss.png")
    
        response = get_annotations(screen_ss)
        annotations = response["data"]["textAnnotations"]
        
        found_headings_boxes = screen_ss.find_texts(remaining_forms, annotations)
        print(found_headings_boxes)
        found_headings = list(found_headings_boxes.keys())
        forms_on_screen = {}
        for i in range(len(found_headings)-1):
            heading_box = found_headings_boxes[found_headings[i]]
            next_heading_box = found_headings_boxes[found_headings[i+1]]
            
            form_box = Box((
                heading_box.l,
                heading_box.t,
                screen_size[0] - heading_box.l,
                next_heading_box.t - heading_box.t 
            ))
            forms_on_screen[found_headings[i]] = form_box
            button_locs = sort_boxes(find_all_img_in_bounds("button.png", form_box,0.9))
            
            moveTo(button_locs[form_heading_options_index[found_headings[i]]].centre)
            click()
            move(-50, 0)
            
            print(button_locs)
            remaining_forms.remove(found_headings[i])
            
        
        
        scroll(-100)
    
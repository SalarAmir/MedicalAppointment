import eel
import time
import numpy as np
from pyautogui import screenshot, locateAll, locateAllOnScreen, click, moveTo, size, scroll, move
from requests import post

eel.init('web')

# Box class definition
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
        self.gray_ss = self.ss.convert('L')
        self.path = file_path
        
        # self.screen_size = size()
    
    def get_pixel(self, x, y):
        return self.ss.getpixel((x-self.box.l, y-self.box.t))
    def get_gray_pixel(self, x, y):
        return self.gray_ss.getpixel((x-self.box.l, y-self.box.t))
    
    def is_line_pixel(self, x, y, direction):
        
        if self.get_gray_pixel(x, y) > 230:
            return False
        
        if direction == 'horizontal':
            line_length = 20
            bool_list = []
            for i in range(line_length):
                if(x+i >= self.box.l + self.box.w):
                    break
                bool_list.append(abs(self.get_gray_pixel(x+i, y) - self.get_gray_pixel(x, y)) < 1)
            
            return all(bool_list)
        
        else:
            line_length = 20
            bool_list = []
            for i in range(line_length):
                if(y+i >= self.box.t + self.box.h):
                    break
                bool_list.append(abs(self.get_gray_pixel(x, y+i) - self.get_gray_pixel(x, y)) < 1)
            return all(bool_list)
    
    
    def find_all_img(self, image, confidence=0.9):
        # try:
        try:
            found_coords = list(locateAll(needleImage=image, haystackImage=self.ss, confidence=confidence))
        except:
            return []
        
        res = []
        for coord in found_coords:
            x, y, w, h = coord
            temp_tuple = (int(x + self.box.l), int(y + self.box.t), int(w), int(h))
            box = Box(temp_tuple)
            res.append(box)
        return res

    
    def find_text(self, text_to_find, texts_all):
        for text in texts_all:
            if text["description"].lower() == text_to_find.lower():
                vertices = text["boundingPoly"]["vertices"]
                box_vertices = tuple((vertex['x']+self.box.l, vertex['y']+self.box.t) for vertex in vertices)
                
                return Box(box_vertices)
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
                else:
                    found_texts[text["description"]].append(vertices)
                # found_texts[text["description"]] = vertices
        return found_texts

    # def get_lines(self):
    #     lines_found = get_image_lines(self.ss)
        
    #     # lines_found[0] += self.box.t
    #     # lines_found[1] += self.box.l
    #     return (lines_found[0] + self.box.t, lines_found[1] + self.box.l)

# Form class definition
class Form:
    def __init__(self, heading:str, heading_box:Box, border_box:Box) -> None:
        self.heading = heading
        self.heading_box = heading_box
        self.border_box = border_box
        
        self.buttons = []
        self.selected = None
        self.button_path = "button.png"
        self.selected_button_path = "button_selected.png"
        
        self.ss = None
        self.ss = ScreenShot(self.border_box.box_tuple, f"form_{self.heading}.png")
        # self.selected_button_path = 
    
    def establish_borders(self, screen_ss:ScreenShot):
        # Find bottom border
        for y in range(self.heading_box.t + self.heading_box.h, screen_ss.box.t + screen_ss.box.h):
            if screen_ss.is_line_pixel(self.heading_box.l + 1, y, 'horizontal'):
                self.border_box.h = y - self.heading_box.t
                break

        # Find right border
        for x in range(self.heading_box.l + self.heading_box.w, screen_ss.box.l + screen_ss.box.w):
            if screen_ss.is_line_pixel(x, self.heading_box.t, 'vertical'):
                self.border_box.w = x - self.heading_box.l
                break
        new_box = Box((self.border_box.l, self.border_box.t, self.border_box.w, self.border_box.h))
        self.border_box = new_box
        self.ss = ScreenShot(self.border_box.box_tuple, f"form_{self.heading}.png")
        
    def find_buttons(self, confidence):
        
        try:
            self.buttons += self.ss.find_all_img(self.button_path, confidence)
        except:
            pass
        
        try:
            selected_found = self.ss.find_all_img(self.selected_button_path, confidence)
            self.buttons += selected_found
            self.selected = selected_found[0]
        except:
            pass
            
        # remove buttons which are within pixels of each other
        if(len(self.buttons) == 0):
            return self.buttons
        self.buttons = [self.buttons[0]] + [self.buttons[i] for i in range(1, len(self.buttons)) if not any(abs(self.buttons[i].l - self.buttons[j].l) < 4 and abs(self.buttons[i].t - self.buttons[j].t) < 4 for j in range(i))]
        

        # self.buttons += self.ss.find_all_img("button_selected.png", confidence)
        self.buttons = sort_boxes(self.buttons)
        return self.buttons
    
    def click_button(self, button_index):
        try:
            moveTo(self.buttons[button_index].centre)
            click()
            moveTo(100, 400)
        except:
            pass
    def click_last(self):
        moveTo(self.buttons[-1].centre)
        click()
        moveTo(100, 400)
    def unselect_button(self):
        if self.selected:
            moveTo(self.selected.centre)
            click()
            moveTo(100, 400)
    def click_all_buttons(self):
        for button in self.buttons:
            moveTo(button.centre)
            # click()
            # time.sleep(1)
    
# Helper functions
def pix_within_threshold(pix1, pix2, threshold):
    return all(abs(pix1[i] - pix2[i]) < threshold for i in range(3))

def find_all_img_in_bounds(image, bound_box, confidence):
    ss_in_bounds = ScreenShot(bound_box.box_tuple, "temp_ss.png")
    found_coords = ss_in_bounds.find_all_img(image, confidence)
    return found_coords

def sort_boxes(boxes):
    return sorted(boxes, key=lambda box: (box.l,box.t))

def num_within_threshold(num, target, threshold):
    return abs(num - target) < threshold


def get_legit_headings(found, screen_ss):
    legit_found = {}
    for heading, verts in found.items():
        for box in verts:
            if not any(screen_ss.is_line_pixel(box.l, y, 'horizontal') for y in range(box.t, box.t -8, -1)):
                # print(f"skipping {heading} because of {box}")
                continue
            legit_found[heading] = box
            break
    return legit_found

def get_annotations(ss:ScreenShot):
    server_url = 'https://googlecloudapi.vercel.app/api/v1'
    with open(ss.path, 'rb') as image:
        response = post(f'{server_url}/image/annotations', files={'file': image})
        return response.json()

def num_within_threshold(num, target, threshold):
    return abs(num - target) < threshold

@eel.expose
def run_main_code(form_data):
    screen_size = size()
    top_bar = 120
    bottom_bar = 30
    
    
    # lines = screen_ss.get_lines()
    # print(lines)
    # horizontals, verticals = lines
    
    headings_options_count = {
        "M0069" : 2,
        "A1110B": 3,
        
        "M0080": 4,
        "M0100": 8,
        "M0110":4,
        
        "HCS_0110_Facility": 2,
        # "Blood Pressure": 2,
        "B0200":5,
        "B1000":6,
        "B1300":7,
        
        "C0100":3,
        "C0200":4,
        "C0300A":5,
        "C0300B":4,
        "C0300C":4,
        "C0400A":4,
        "C0400B":4,
        "C0400C":4,
        
        "C1310A":3,
        "C1310B":4,
        "C1310C":4,
        "C1310D":4,
        
        "M1700":5,
        "M1710":6,
        "M1720":5,
        
        "D0150A1":4,
        "D0150A2":4,
        
        "D0150B1":4,
        "D0150B2":4,
        
        "D0150C1":4,
        "D0150C2":4,
        
        "D0150D1":4,
        "D0150D2":4,
        
        "D0150E1":4,
        "D0150E2":4,
        
        "D0150F1":4,
        "D0150F2":4,
        
        "D0150G1":4,
        "D0150G2":4,
        
        "D0150H1":4,
        "D0150H2":4,
        
        "D0150I1":4,
        "D0150I2":4,
        
        "M1740":3,
        "M1745":6,
        
        "M2102_CARE_TYPE_SRC_SPRVSN":5,
        
        "M1800":4,
        "M1810":4,
        "M1820":4,
        "M1830":4,
        "M1840":5,
        "M1845":4,
        "M1850":6,
        "M1860":7,
        
        "GG0170A1":11,
        "GG0170A2":11,
        "GG0170B1":11,
        "GG0170B2":11,
        "GG0170C_MOBILITY_SOCROC_PERF":11,
        "GG0170C_MOBILITY_DSCHG_GOAL":11,
        "GG0170D1":11,
        "GG0170D2":11,
        "GG0170E1":11,
        "GG0170E2":11,
        "GG0170F1":11,
        "GG0170F2":11,
        "GG0170G1":11,
        "GG0170G2":11,
        "GG0170I1":11,
        "GG0170I2":11,
        "GG0170J1":11,
        "GG0170J2":11,
        "GG0170K1":11,
        "GG0170K2":11,
        "GG0170L1":11,
        "GG0170L2":11,
        "GG0170M1":11,
        "GG0170M2":11,
        # "GG0170N1":11,
        "GG0170N2":11,
        # "GG0170O1":11,
        "GG0170O2":11,
        "GG0170P1":11,
        "GG0170P2":11,
        "GG0170Q1":11,
        
        "M1600":4,
        "M1610":3,
        "M1620":8,
        "M1630":3,
        
        "M1400":5,
        
        "M1306":2,
        
        "M1322":5,
        "M1324":5,
        "M1330":4,
        "M1332":4,
        "M1334":3,
        "M1340":3,
        "M1342":4,
        
        "J0510":6,
        "J0520":6,
        "J0530":5,
        
        "K0520A1":3,
        "K0520B1":3,
        "K0520C1":3,
        "K0520D1":3,
        "K0520Z1":3,
        
        "M1870":6,
        
        "N0415A1":3,
        "N0415A2":3,
        "N0415E1":3,
        "N0415E2":3,
        "N0415F1":3,
        "N0415F2":3,
        "N0415H1":3,
        "N0415H2":3,
        "N0415I1":3,
        "N0415I2":3,
        "N0415J1":3,
        "N0415J2":3,
        "N0415Z1":3,
        
        "M2001":3,
        "M2003":2,
        "M2010":3,
        "M2020":5,
        "M2030":5,
        
        "00110A1a":3,
        "00110A2a":3,
        "00110A3a":3,
        "00110A10a":3,
        "00110B1a":3,
        "00110C1a":3,
        "00110C2a":3,
        "00110C3a":3,
        "00110C4a":3,
        "00110D1a":3,
        "00110D2a":3,
        "00110D3a":3,
        "00110E1a":3,
        "00110F1a":3,
        "00110G1a":3,
        "00110G2a":3,
        "00110G3a":3,
        "00110H1a":3,
        "00110H2a":3,
        "00110H3a":3,
        "00110H4a":3,
        "00110H10a":3,
        "00110I1a":3,
        "00110J1a":3,
        "00110J2a":3,
        "00110J3a":3,
        
        "0011001a":3,
        "0011002a":3,
        "0011003a":3,
        "0011004a":3,
        "00110Z1a":3,
    }
    headings_choices = { data["name"]:data["value"] for data in form_data}
    print(headings_choices)
    # debugging stuff:
    found_text = set()
    found_legit = set()
    incorrect_buttons = set()
    
    problem_paths = ["problem_1.png", "problem_2.png"]
    remaining_headings = list(headings_choices.keys())
    while len(remaining_headings) > 0:
        screen_ss = ScreenShot((0, top_bar, screen_size[0], screen_size[1]-top_bar-bottom_bar), "first_ss.png")
        problems = []
        for path in problem_paths:
            
            problems += screen_ss.find_all_img(path, 0.9)
        for problem in problems:
            moveTo(problem.centre)
            click()
            time.sleep(1)
            moveTo(100, screen_size[1]/2)
        
        annotations = get_annotations(screen_ss)["data"]["textAnnotations"]
        end = screen_ss.find_text("Rehab", annotations)
        end_2 = screen_ss.find_all_img("end.png", 0.8)
        if(len(end_2) > 0 or end):
            print("End found")
            break

        found = screen_ss.find_texts(headings_choices.keys(), annotations)
        (found_text.add(head) for head in found.keys())
        found = get_legit_headings(found, screen_ss)
        (found_legit.add(head) for head in found.keys())
        

        # headings_boxes = found
        print("heading text boxes:", found)
        # screen_ss = ScreenShot((0, 120, screen_size[0], screen_size[1]-120-40), "first_ss.png")
        # populate forms on screen:
        for heading, box in found.items():
            if(heading not in remaining_headings):
                continue
            box = found[heading]
            
            form_box = Box((
                box.l,
                box.t,
                int(abs(screen_size[0] - box.l)),
                int(abs(screen_size[1] - box.t))
            ))
            
            form_obj = Form(heading, box, form_box)
            form_obj.establish_borders(screen_ss)
            form_obj.find_buttons(0.80)
            if(len(form_obj.buttons) != headings_options_count[heading]):
                incorrect_buttons.add(heading)
                print(f"Incorrect buttons for {heading}: {len(form_obj.buttons)}")
                continue
            incorrect_buttons.discard(heading)
            
            form_obj.unselect_button()
            form_obj.click_button(int(headings_choices[heading])-1)
            moveTo(100, screen_size[1]/2)
            # print(form_obj.buttons)
            # moveTo((right_border, bottom_border))
            # time.sleep(2)
            remaining_headings.remove(heading)
            pass
        
        scroll(-100)
    
    
    never_found = set(headings_choices.keys()) - found_text
    never_legit = set(headings_choices.keys()) - found_legit
    
    # write to file:
    output_file = open("output.txt", "w")
    print(f"Found: {list(found_text)}")
    print(f"Never found: {never_found}")
    output_file.write(f"Found: {list(found_text)}\n")
    # print(f"Found legit: {found_legit}")
    print(f"Never legit: {never_legit}")
    output_file.write(f"Never found: {never_found}\n")
    output_file.close()
    print(f"Incorrect buttons: {list(incorrect_buttons)}")
    block = input("Press enter to continue")
    pass

if __name__ == '__main__':
    eel.start('index.html', size=(600, 500))
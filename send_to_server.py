import requests
import webbrowser
import time
import pyautogui as pag
from json import dump

server_url = 'https://googlecloudapi.vercel.app/api/v1'

def get_annotations(image_path):
    with open(image_path, 'rb') as image:
        response = requests.post(f'{server_url}/image/annotations', files={'file': image})
        return response.json()


def ss_cutoff(offset_l, offset_r, offset_t, offset_b, size: tuple, path):
    ss = pag.screenshot(path,region=(offset_l, offset_t, size[0]-offset_r-offset_l, size[1]-offset_b-offset_t))
    return ss

def to_screen_coords(coords:tuple, offset_lt:tuple):
    return tuple(coord+offset for coord, offset in zip(coords, offset_lt))

def print_texts(texts):
    for text in texts:
        print(f'\n"{text["description"]}"')

        vertices = [
            f"({vertex['x']},{vertex['y']})" for vertex in text["boundingPoly"]["vertices"]
        ]

        print("bounds: {}".format(",".join(vertices)))

def get_headings_bounds(texts, headings, offset_lt):
    text_found_bounds = []
    heading_bounds = {}
    for text in texts:
        if text["description"] in headings:
            # print(f"looking for {text['description']}")
        
            print(f'\n"{text["description"]}"')
            vertices = [
                to_screen_coords((vertex['x'],vertex['y']), offset_lt) for vertex in text["boundingPoly"]["vertices"]
            ]
            heading_bounds[text["description"]] = vertices
            text_found_bounds.append(vertices)
            # print("bounds: {}".format(",".join(vertices)))
            # break
    return heading_bounds

def find_text_in_bounds(texts, text_to_find, bounds, offset_lt):
    
    found_bounds = []
    for text in texts:
        if text["description"] == text_to_find:
            vertices = [
                to_screen_coords((vertex['x'],vertex['y']), offset_lt) for vertex in text["boundingPoly"]["vertices"]
            ]
            if bounds[0][1] < vertices[0][1] and bounds[2][1] > vertices[2][1]: 
                found_bounds = vertices
                break

    return found_bounds


if __name__ == "__main__":
    # webbrowser.open('index.html')
    time.sleep(2)
    
    offset_lt = (0, 120)
    screen_size = pag.size()
    ss = ss_cutoff(0, 0, 120, 30, screen_size, "ss.png")
    
    response = get_annotations("ss.png")
    annotations = response["data"]["textAnnotations"]
    
    functional_stats = {"M1800":"02", "M1810":"03", "M1820":"01", "M1830":"05", "M1840":"04", "M1845":"00", "M1860":"01"}
    bounds = get_headings_bounds(annotations, functional_stats.keys(), offset_lt)
    form_regions = {}
    found_headings = list(bounds.keys())
    if(len(found_headings) == 0):
        print("No headings found")
        print_texts(annotations)
        input("Press enter to exit")
    else:
        for i in range(len(found_headings)-1):
            # ss_region = (0, 0, bounds[found_headings[i]][0][1],  bottom_off)
            region_vertices = [
                bounds[found_headings[i]][0],
                bounds[found_headings[i]][1],
                bounds[found_headings[i+1]][2],
                bounds[found_headings[i+1]][3]
            ]
            form_regions[found_headings[i]] = region_vertices
        
        print(form_regions)
        for head in form_regions:
            option_text_loc = find_text_in_bounds(annotations, functional_stats[head], form_regions[head], offset_lt)
            print(option_text_loc)
            time.sleep(1)
            pag.moveTo(option_text_loc[0])
        # pag.moveTo(option_text_loc[0])
            
            
            
        
        
        # print(f"ss of {found_headings[0]}")
        # curr_region = regions[found_headings[0]]
        # print(curr_region)
        # ss_cutoff(curr_region[0], curr_region[1], curr_region[2], screen_size[1]-curr_region[3], screen_size, "test.png")
    
    
    
    # form_bounds = {}
    
    # for bound in bounds:
    #     loc = bound[0]
    #     pag.moveTo(loc)
    #     time.sleep(1)
        
    block = input("Press enter to exit")
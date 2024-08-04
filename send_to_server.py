import requests
import webbrowser
import time
import pyautogui as pag

server_url = 'https://googlecloudapi.vercel.app/api/v1'

def get_annotations(image_path):
    with open(image_path, 'rb') as image:
        response = requests.post(f'{server_url}/image/annotations', files={'file': image})
        return response.json()


def ss_cutoff(offset_l, offset_r, offset_t, offset_b, size: tuple):
    ss = pag.screenshot("ss.png",region=(offset_l, offset_t, size[0]-offset_r-offset_l, size[1]-offset_b-offset_t))
    return ss


if __name__ == "__main__":
    webbrowser.open('index.html')
    time.sleep(2)
    
    ss = ss_cutoff(0, 0, 120, 30, pag.size())
    
    response = get_annotations("ss.png")
    texts = response["data"]["textAnnotations"]
    text_to_find = "Form"
    text_found_bounds = []
    for text in texts:
        if text_to_find in text["description"]:
            print(f'\n"{text["description"]}"')
            vertices = [
                f"({vertex['x']},{vertex['y']})" for vertex in text["boundingPoly"]["vertices"]
            ]
            text_found_bounds.append(vertices)
            # print("bounds: {}".format(",".join(vertices)))
            # break
    
    print(text_found_bounds)
    # print(response["data"]["textAnnotations"])
    
    # print(response["data"].keys())

    # texts = response["data"]["textAnnotations"]
    # print("Texts:")

    # for text in texts:
    #     print(f'\n"{text["description"]}"')

    #     vertices = [
    #         f"({vertex['x']},{vertex['y']})" for vertex in text["boundingPoly"]["vertices"]
    #     ]

    #     print("bounds: {}".format(",".join(vertices)))

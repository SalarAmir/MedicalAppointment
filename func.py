import pyautogui as pag
from PIL import Image
import pytesseract
import time
import webbrowser
import numpy as np

pag.FAILSAFE = False

def open_page(file_path):
    webbrowser.open(file_path)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(head_region):
    screenshot = pag.screenshot(region=head_region)
    print("screenshot taken")
    text = pytesseract.image_to_string(screenshot)
    print("text extracted")
    return text.strip()

if __name__ == "__main__":
    # Open the HTML file in a web browser
    webbrowser.open('index.html')
    time.sleep(1)
    
    form_headers = []
    max_iterations = 25  # Set the maximum number of iterations
    iteration = 0  # Initialize the iteration counter
    seen_texts = set()  # Initialize a set to store seen texts
    
    while iteration < max_iterations:
        time.sleep(1)
        header = pag.locateOnScreen('form-head.png', confidence=0.8)
        print(header[0])
        print(header)
        if header is None:
            break
        # left=header[0]
        # top=header[1]
        # width=header[2]
        # height=header[3]
        header_region = (np.int64(header[0]), np.int64(header[1]), header[2], header[3])
        print(header_region)
        header_text = extract_text_from_image(header_region)
        if header_text in seen_texts:
            pag.scroll(-100)
            continue
        
        form_headers.append(header)
        seen_texts.add(header_text)
        iteration += 1
        pag.scroll(-100)
    
    radio_buttons = list(pag.locateAllOnScreen('button.png', confidence=0.8))
    
    num_forms = 2
    buttons_per_form = 6
    print(f'buttons found {len(radio_buttons)}\n')
    print(f'forms found {len(form_headers)}\n')
    
    # form_buttons = []
    # for i in range(num_forms):
    #     header = form_headers[i]
    #     buttons = radio_buttons[i*buttons_per_form:(i+1)*buttons_per_form]
    #     form_buttons.append((header, buttons))
    
    # print(form_buttons[0])
    
    # # Choose which button to click from each form:
    # click_options = [1, 2]
    
    # for i, form in enumerate(form_buttons):
    #     button_number = click_options[i]
    #     print(form)
    #     click_location = pag.center(form[1][button_number-1])
    #     pag.click(click_location)
    
    # time.sleep(2)
    # submit_button = pag.locateCenterOnScreen('submit.png', confidence=0.8)
    # pag.click(submit_button)

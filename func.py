import pyautogui as pag
from PIL import Image
import time
import webbrowser

def open_page(file_path):
    webbrowser.open(file_path)
    
    # screenshot = pyautogui.screenshot()
    


# Example usage
if __name__ == "__main__":
    # Open the HTML file in a web browser
    # import webbrowser
    webbrowser.open('index.html')
    time.sleep(1)
    
    form_headers = list(pag.locateAllOnScreen('form-head.png', confidence=0.8))
    
    radio_buttons = list(pag.locateAllOnScreen('button.png', confidence=0.8))
    
    num_forms = 2
    buttons_per_form = 6
    print(f'buttons found {len(radio_buttons)}')
    
    
    # form_buttons = [ (form_headers[i], radio_buttons[(i*buttons_per_form):(i+1)*buttons_per_form])  for i in range(num_forms)]
    form_buttons = []
    for i in range(num_forms):
        header = form_headers[i]
        buttons = radio_buttons[i*buttons_per_form:(i+1)*buttons_per_form]
        
        form_buttons.append((header, buttons))
    
    print(form_buttons[0])
    # choose which button to click from each form:
    click_options = [4, 2]
    for i, form in enumerate(form_buttons):
        button_number = click_options[i]
        print(form)
        click_location = pag.center(form[1][button_number-1])
        pag.click(click_location)
    time.sleep(2)
    submit_button = pag.locateCenterOnScreen('submit.png', confidence=0.8)
    pag.click(submit_button)


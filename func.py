import pytesseract
import pyautogui
from PIL import Image
import time
import os
import logging

# Set up Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure logging
logging.basicConfig(filename='automation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_and_click_radio_button(image_path):
    if not os.path.isfile(image_path):
        logging.error(f'File not found: {image_path}')
        return f'File not found: {image_path}'
    
    try:
        # Attempt to locate the image on the screenj
        location = pyautogui.locateCenterOnScreen(image_path)
        print(location)
        
        # If the image is found, click on it
        if location:
            pyautogui.click(location)
            logging.info(f'Clicked on the radio button for {image_path}')
            return f'Clicked on the radio button for {image_path}'
        else:
            logging.warning(f'Radio button for {image_path} not found on the screen')
            return f'Radio button for {image_path} not found on the screen'
    except pyautogui.ImageNotFoundException:
        logging.error(f'Image not found error for {image_path}')
        return f'Image not found error for {image_path}'
    except Exception as e:
        logging.error(f'Error processing {image_path}: {e}')
        return f'Error processing {image_path}: {e}'

def process_images(directory):
    # Iterate over all files in the given directory
    for subdir, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.png'):
                image_path = os.path.join(subdir, file)
                print(f'Processing image: {image_path}')
                result = find_and_click_radio_button(image_path)
                print(result)
                time.sleep(1)  # Wait for a short duration before the next click

# Example usage
if __name__ == "__main__":
    # Open the HTML file in a web browser
    import webbrowser
    webbrowser.open('file://' + os.path.abspath('index.html'))

    # Give some time to switch to the browser window
    print('You have 5 seconds to switch to the browser window...')
    time.sleep(5)

    # Process all images in the radio_buttons directory
    process_images('radio_buttons')

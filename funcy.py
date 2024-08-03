import pyautogui as pag
from PIL import Image
import pytesseract
import time
import webbrowser

def capture_entire_page():
    # Open the HTML file in a web browser
    webbrowser.open('index.html')
    time.sleep(2)  # Give time for the page to load

    # Initialize variables
    full_page_image = Image.new('RGB', (0, 0))  # Create an empty image to combine screenshots
    scroll_height = pag.size()[1]  # Get the height of the screen
    current_scroll = 0

    while True:
        # Take a screenshot of the visible part of the page
        ss = pag.screenshot()
        # If it's the first screenshot, initialize the full page image
        if full_page_image.size == (0, 0):
            full_page_image = Image.new('RGB', (ss.width, ss.height * 10))
        
        # Paste the screenshot onto the full page image
        full_page_image.paste(ss, (0, current_scroll))
        current_scroll += ss.height

        # Scroll down
        pag.scroll(-scroll_height)
        time.sleep(1)
        print(f"Captured {current_scroll} pixels of the page.")

        # Check if we have scrolled to the bottom of the page
        try:
            if pag.locateOnScreen('submit.png', confidence=0.8):
                break
        except pag.ImageNotFoundException:
            # Handle case where bottom_marker.png is not found
            print("Bottom marker not found; continuing to scroll.")

    # Save the full page image
    full_page_image.save('full_page_screenshot.png')

def ocr_screenshot(file_path):
    # Open the image file
    img = Image.open(file_path)

    # Perform OCR on the image
    text = pytesseract.image_to_string(img)
    print(text)

if __name__ == "__main__":
    capture_entire_page()
    ocr_screenshot('full_page_screenshot.png')

import pyautogui
import pytesseract
from PIL import Image
import time

# Set up Tesseract executable path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust the path as needed

def find_and_click_radio_button(button_text):
    # Take a screenshot of the current screen
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")

    # Use OCR to extract text from the screenshot
    image = Image.open("screenshot.png")
    text = pytesseract.image_to_string(image)

    # Find the position of the radio button based on the provided text
    location = pyautogui.locateCenterOnScreen('radio_buttons/' + button_text + '.png')
    
    # If the radio button is found, click on it
    if location:
        pyautogui.click(location)
        return f'Clicked on the radio button for {button_text}'
    else:
        return f'Radio button for {button_text} not found on the screen'

# Example usage
if __name__ == "__main__":
    # Open the HTML file in a web browser
    import webbrowser
    webbrowser.open('file://' + 'index.html')

    # Give some time to switch to the browser window
    print('You have 5 seconds to switch to the browser window...')
    time.sleep(5)

    # Example data (replace with actual text you are looking for)
    radio_button_texts = ['option1', 'option2', 'option3']

    # Loop through the radio button texts and click them
    for text in radio_button_texts:
        result = find_and_click_radio_button(text)
        print(result)
        time.sleep(1)  # Wait for a short duration before the next click

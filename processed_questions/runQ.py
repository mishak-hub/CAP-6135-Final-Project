import os
import time
import pyautogui
from pynput.keyboard import Key, Controller
import pyperclip
import cv2 
import numpy as np
import io
from PIL import Image
from pywinauto import Application, keyboard, application
import sys
from pywinauto import Desktop
  
top_windows = Desktop(backend="uia").windows()

for window in top_windows:
    if "Opera" in window.window_text() :
        print(window.window_text())
        opera_title = window.window_text()
        break
'''
# Set of categories
base_folder = "../MM-SafetyBench(imgs)"
categories = [folder for folder in os.listdir(base_folder) 
    if os.path.isdir(os.path.join(base_folder, folder))]
'''

browser = Application(backend="uia").connect(title=opera_title, visible_only=False)

# Get the main window of Opera GX
opera_window = browser.window(title = opera_title)


keyboard = Controller()

def copy_image_to_clipboard(image_path):
    # Open the image
    image = Image.open(image_path)
    # Save the image to a temporary file
    temp_file = "temp.png"
    image.save(temp_file)
    temp = None  
    # Use pyautogui to open the image and copy it to clipboard
    os.startfile(temp_file)  # This opens the image with the default viewer 
    for window in top_windows:
         if "temp" in window.window_text():
            print(window.window_text())
            image_title = window.window_text()
            temp = Application(backend="uia").connect(title=image_title,visible_only=False)
            break 
    EM = None
    if temp is not None: 
        EM = temp.window(title = image_title)
        print(EM.window_text()) 
        EM.set_focus()  # Focus on the image vie wer window
        center_x = EM.left + EM.width // 2
        center_y = EM.top + EM.height // 2
        pyautogui.click(center_x, center_y)
    else:
        pyautogui.click(300, 400)  # Fallback click if window not found
    
    pyautogui.hotkey('ctrl', 'c')  # Simulates Ctrl+C to copy
    os.remove(temp_file)  # Clean up the temporary file
    if EM is not None:
          EM.close()  # Close the image viewer window
    

categories= ['01-Illegal_Activitiy', '02-HateSpeech', '03-Malware_Generation', '04-Physical_Harm', '05-EconomicHarm', '06-Fraud', '07-Sex', '08-Political_Lobbying', '09-Privacy_Violence', '10-Legal_Opinion', '11-Financial_Advice', '12-Health_Consultation', '13-Gov_Decision']
print(f"Detected categories: {categories}")
# Placeholder coordinates
text_box_coords = (576, 881)
model_selection_coords = (289, 282)



def extract_questions(file_path):
    """Extract questions from a text file."""
    print(f"Extracting questions from: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            questions = [line.strip() for line in file if line.strip()]
        return questions
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def paste_text(text, coords):
    for window in top_windows:
        if "Opera" in window.window_text() :
            print(window.window_text())
            opera_title = window.window_text()
            break
    
    browser = Application(backend="uia").connect(title=opera_title, visible_only=False)

    # Get the main window of Opera GX
    ow = browser.window(title = opera_title)
    ow.set_focus()  # Focus on the main window 
    """Paste text at specified coordinates."""
    print(f"Pasting text at coordinates {coords}: '{text[:30]}...' (truncated)")
    
    # 1. Click at the specified coordinates
    pyautogui.click(coords[0], coords[1])
    time.sleep(0.5)  # Wait for click to register
    
    # 2. Copy text to clipboard
    pyperclip.copy(text)
    
    # 3. Paste text using keyboard shortcut
    pyautogui.hotkey('ctrl', 'v')  # Windows/Linux
    # or
    # pyautogui.hotkey('command', 'v')  # macOS
    
    # 4. Wait for paste to complete
    time.sleep(0.5)
    
    print("Text pasted successfully")

def click_at_position(coords):
    """Click at specified coordinates."""
    print(f"Clicking at coordinates: {coords}")
    
    pyautogui.click(coords[0], coords[1])
    time.sleep(0.3)  # Wait for click to register
    
    print("Click completed")

def upload_image(image_path):
    """Upload an image file."""
    print(f"Uploading image: {image_path}")
    if image_path:
        copy_image_to_clipboard(image_path)
        click_at_position(text_box_coords)
        time.sleep(1)

        pyautogui.hotkey('ctrl', 'v')
    # 2. In the file dialog, type the path and press Enter
        pyautogui.press('enter')
    
        print("Image uploaded successfully")

def wait_for_click():
    time.sleep(2)  # Allow time to switch to the target application
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    cv2.imwrite("Screenshot.png", image)
    # Load the screenshot image
    screenshot = cv2.imread('Screenshot.png')


    # Display the screenshot image
    cv2.imshow('Screenshot.png', screenshot)

    # Function to get the pixel location on mouse click
    def get_pixel_location(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("Pixel location (x, y):", x, y)

    # Set up the mouse callback
    cv2.setMouseCallback('Screenshot.png', get_pixel_location)

    # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def run():
    """Main processing function with text extraction and pasting."""
    print("Starting run() function")
    
    for category in categories:
        print(f"\nProcessing category: {category}")
        
        # Path to questions and images for this category
        questions_path = f"{category}.txt"
        images_path = f"../MM-SafetyBench(imgs)/{category}/SD_TYPO/"
        
        # Extract questions from file
        questions = extract_questions(questions_path)
        
        # Process each question
        for i, question in enumerate(questions):
            print(f"\n  Processing question {i+1}: {question}")

            # 3. Click for model selection
            click_at_position(model_selection_coords)

            # 1. Click for text box
            click_at_position(text_box_coords)
            
            
            
            # 4. Upload image if available
            image_path = f"{images_path}{i}.jpg"
            if os.path.exists(image_path):
                upload_image(image_path)
                # 2. Paste the question
                paste_text(question, text_box_coords)
            else:
                print(f"    Note: Image not found at {image_path}")
                sys.exit(1)
            
            print("    Question processed")
            time.sleep(1)  # Wait between questions

def main():
    """Main function with improved click recording."""
    global text_box_coords, model_selection_coords
    '''
    print("Starting main() function")
    time.sleep(2)  # Allow time to switch to the target application
    # Record click for model selection
    print("Please click where the model selection should be...")
    model_selection_coords = wait_for_click()
    print(f"Recorded model selection coordinates: {model_selection_coords}")

    # Record click for text box
    print("Please click where the text box should be...")
    text_box_coords = wait_for_click()
    print(f"Recorded text box coordinates: {text_box_coords}")
    '''
    with keyboard.pressed(Key.space):
        while True:
            run() 

if __name__ == "__main__":
    main()

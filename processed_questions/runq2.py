import os
import time
import pyautogui
from pynput.keyboard import Key, Controller, Listener
import pyperclip
import cv2
import numpy as np
import io
from PIL import Image
from pywinauto import Application, keyboard, application
import sys
from pywinauto import Desktop
keyboard = Controller()  

should_exit = False

categories= ['01-Illegal_Activitiy', '02-HateSpeech', '03-Malware_Generation', '04-Physical_Harm', 
             '05-EconomicHarm', '06-Fraud', '07-Sex', '08-Political_Lobbying', '09-Privacy_Violence', 
             '10-Legal_Opinion', '11-Financial_Advice', '12-Health_Consultation', '13-Gov_Decision']

print(f"Detected categories: {categories}")

# Placeholder coordinates
text_box_coords = (393, 921)
model_selection_coords = (137, 224)
top_windows = Desktop(backend="uia").windows()

def on_press(key):
    global should_exit
    if key == Key.esc:
        should_exit = True
        return False  # Stop the listener
    

def get_win(title):
    for w in top_windows:
        if title in w.window_text() :
            print(w.window_text())
            t = w.window_text()
            E = Application(backend="uia").connect(title=t,visible_only=False)
            return E.window(title=t)
    return None

def copy_image_to_clipboard(image_path):
    # Open the image
    image = Image.open(image_path)

    # Use pyautogui to open the image and copy it to clipboard
    os.startfile(image)  # This opens the image with the default viewer 
    time.sleep(5)  # Wait for the image viewer to open
    EM = get_win(".jpg")  # Get the image viewer window
    if EM is not None: 
        EM.set_focus()  # Focus on the image vie wer window
        center_x = EM.left + EM.width // 2
        center_y = EM.top + EM.height // 2
        pyautogui.click(center_x, center_y)
    else:
        pyautogui.click(300, 400)  # Fallback click if window not found

        
    time.sleep(1)  # Wait for the click to register
    pyautogui.hotkey('ctrl', 'c')  # Simulates Ctrl+C to copy

    if EM is not None:
          EM.close()  # Close the image viewer window
    

def extract_questions(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip()]
            questions = []
            for line in lines:
                if ' ' in line:
                    questions.append(line.split(' ', 1)[1])
                else:
                    questions.append(line)
        return questions
    except FileNotFoundError:
        return []
    except Exception as e:
        return []

def paste_text(text, coords):

    """Paste text at specified coordinates."""

    print(f"Pasting text at coordinates {coords}: '{text[:30]}...' (truncated)")
    
    # 1. Click at the specified coordinates
    pyautogui.click(coords[0], coords[1])
    time.sleep(0.5)  # Wait for click to register
    
    # 2. Copy text to clipboard
    pyperclip.copy(text)
    
    # 3. Paste text using keyboard shortcut
    pyautogui.hotkey('ctrl', 'v')  # Windows/Linux
  
    # 4. Wait for paste to complete
    time.sleep(0.5)
    
    print("Text pasted successfully")


def click_at_position(coords):
    ow = get_win("Opera")
    if ow is not None:
        ow.set_focus()  # Focus on the main window 
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
                print(f"Note: Image not found at {image_path}")
                sys.exit(1)
            
            print("Question processed")
            time.sleep(1)  # Wait between questions


def main():
    """Main function with improved click recording."""
    global text_box_coords, model_selection_coords

    listener = Listener(on_press=on_press)
    listener.start()

    try:
        while not should_exit:
            run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()

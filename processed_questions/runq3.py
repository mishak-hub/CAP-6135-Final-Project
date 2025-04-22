import os
import time
import pyautogui
from pynput.keyboard import Key, Controller as PynputController, Listener
import pyperclip
import cv2
import numpy as np
from PIL import Image, ImageGrab
import win32clipboard
from io import BytesIO
from pywinauto import Application, Desktop
import sys

# Rename to avoid conflicts
pynput_keyboard = PynputController()  

should_exit = False

categories = ['01-Illegal_Activitiy', '02-HateSpeech', '03-Malware_Generation', '04-Physical_Harm', 
             '05-EconomicHarm', '06-Fraud', '07-Sex', '08-Political_Lobbying', '09-Privacy_Violence', 
             '10-Legal_Opinion', '11-Financial_Advice', '12-Health_Consultation', '13-Gov_Decision']

print(f"Detected categories: {categories}")

# Placeholder coordinates
text_box_coords = (393, 921)
model_selection_coords = (137, 224)

def on_press(key):
    global should_exit
    if key == Key.esc:
        should_exit = True
        return False  # Stop the listener

def get_win(title, timeout=3):
    """Find a window with the given title with timeout"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        top_windows = Desktop(backend="uia").windows()
        for w in top_windows:
            if title.lower() in w.window_text().lower():
                print(f"Found window: {w.window_text()}")
                t = w.window_text()
                try:
                    E = Application(backend="uia").connect(title=t, visible_only=False)
                    return E.window(title=t)
                except Exception as e:
                    print(f"Error connecting to window: {e}")
        time.sleep(0.5)
    print(f"Window with title containing '{title}' not found after {timeout} seconds")
    return None

def send_to_clipboard(image_path):
    """Copy image to clipboard using win32clipboard"""
    try:
        image = Image.open(image_path)
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # The file header offset of BMP is 14 bytes
        output.close()
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        
        print(f"Image copied to clipboard: {image_path}")
        return True
    except Exception as e:
        print(f"Error copying image to clipboard: {e}")
        return False

def upload_image(image_path):
    """Upload an image by copying to clipboard and pasting"""
    print(f"Uploading image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return False
    
    # Copy image to clipboard
    if not send_to_clipboard(image_path):
        print("Failed to copy image to clipboard")
        return False
    
    # Click at the text box location
    if not click_at_position(text_box_coords):
        print("Failed to click at text box")
        return False
    
    # Wait a moment for the click to register
    time.sleep(0.5)
    
    # Paste the image using Ctrl+V
    try:
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)  # Wait for paste to complete
        print("Image pasted successfully")
        return True
    except Exception as e:
        print(f"Error pasting image: {e}")
        return False

def extract_questions(file_path):
    """Extract questions from a file with error handling"""
    try:
        if not os.path.exists(file_path):
            print(f"Error: Question file not found: {file_path}")
            return []
            
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip()]
            questions = []
            for line in lines:
                if ' ' in line:
                    questions.append(line.split(' ', 1)[1])
                else:
                    questions.append(line)
        return questions
    except Exception as e:
        print(f"Error extracting questions from {file_path}: {e}")
        return []

def paste_text(text, coords):
    """Paste text at specified coordinates with error handling"""
    print(f"Pasting text at coordinates {coords}: '{text[:30]}...' (truncated)")
    
    try:
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
        return True
    except Exception as e:
        print(f"Error pasting text: {e}")
        return False

def click_at_position(coords):
    """Click at specified coordinates with error handling"""
    try:
        # Try to focus the Opera window first
        ow = get_win("Opera")
        if ow is not None:
            ow.set_focus()  # Focus on the main window
            time.sleep(0.5)
        
        print(f"Clicking at coordinates: {coords}")
        pyautogui.click(coords[0], coords[1])
        time.sleep(0.5)  # Wait for click to register
        
        print("Click completed")
        return True
    except Exception as e:
        print(f"Error clicking at position {coords}: {e}")
        return False

def wait_for_click():
    """Take a screenshot and wait for user to click to get coordinates"""
    print("Taking screenshot. Click on the desired location...")
    time.sleep(2)  # Allow time to switch to the target application
    
    try:
        image = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite("Screenshot.png", image)
        
        # Load the screenshot image
        screenshot = cv2.imread('Screenshot.png')
        if screenshot is None:
            print("Error: Failed to load screenshot")
            return None

        # Display the screenshot image
        cv2.imshow('Screenshot.png', screenshot)

        # Function to get the pixel location on mouse click
        coords = [None]
        def get_pixel_location(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                print("Pixel location (x, y):", x, y)
                coords[0] = (x, y)

        # Set up the mouse callback
        cv2.setMouseCallback('Screenshot.png', get_pixel_location)

        # Wait for a key press and close the window
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return coords[0]
    except Exception as e:
        print(f"Error in wait_for_click: {e}")
        return None

def run(process_all=True):
    """Main processing function with improved error handling"""
    print("Starting run() function")
    
    for category in categories:
        print(f"\nProcessing category: {category}")
        
        # Path to questions and images for this category
        questions_path = f"{category}.txt"
        images_dir = f"../MM-SafetyBench(imgs)/{category}/SD_TYPO/"
        images_dir = os.path.abspath(images_dir)
        
        # Check if directory exists
        if not os.path.exists(images_dir):
            print(f"Warning: Image directory not found: {images_dir}")
            if process_all:
                continue  # Skip to next category
            else:
                return False
        
        # Extract questions from file
        questions = extract_questions(questions_path)
        if not questions:
            print(f"Warning: No questions found for category {category}")
            if process_all:
                continue  # Skip to next category
            else:
                return False
        
        # Process each question
        for i, question in enumerate(questions):
            if should_exit:
                print("Exit flag detected, stopping processing")
                return False
                
            print(f"\n  Processing question {i+1}: {question}")

            # 1. Click for model selection
            if not click_at_position(model_selection_coords):
                print("Failed to click model selection, retrying...")
                time.sleep(1)
                if not click_at_position(model_selection_coords):
                    print("Failed to click model selection again, skipping question")
                    continue

            # 2. Click for text box
            if not click_at_position(text_box_coords):
                print("Failed to click text box, retrying...")
                time.sleep(1)
                if not click_at_position(text_box_coords):
                    print("Failed to click text box again, skipping question")
                    continue
              
            # 3. Upload image if available
            image_path = f"{images_dir}/{i}.jpg"
            if os.path.exists(image_path):
                if not upload_image(image_path):
                    print(f"Failed to upload image {image_path}, skipping question")
                    continue
                    
                # 4. Paste the question
                if not paste_text(question, text_box_coords):
                    print("Failed to paste text, skipping question")
                    continue
            else:
                print(f"Warning: Image not found at {image_path}, skipping question")
                continue
            
            print("Question processed")
            time.sleep(2)  # Wait between questions
            
    return True

def main():
    """Main function with improved error handling and flow control"""
    global text_box_coords, model_selection_coords

    # Start keyboard listener
    listener = Listener(on_press=on_press)
    listener.start()

    try:
        # Option to set coordinates interactively
        print("Press 'c' to calibrate coordinates or any other key to use defaults")
        if input().lower() == 'c':
            print("Click on the text box location")
            coords = wait_for_click()
            if coords:
                text_box_coords = coords
                
            print("Click on the model selection location")
            coords = wait_for_click()
            if coords:
                model_selection_coords = coords
                
            print(f"Using text_box_coords: {text_box_coords}")
            print(f"Using model_selection_coords: {model_selection_coords}")
        
        # Run once by default, loop only if specified
        print("Press 'l' to loop processing or any other key to run once")
        loop_mode = input().lower() == 'l'
        
        if loop_mode:
            print("Running in loop mode (press ESC to exit)")
            while not should_exit:
                if not run(process_all=True):
                    break
        else:
            print("Running once")
            run(process_all=True)
            
    except Exception as e:
        print(f"Error in main function: {e}")
    finally:
        print("Exiting program")
        listener.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()

import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import cvzone
from pynput.keyboard import Controller
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)  
cap.set(4, 720)   

detector = HandDetector(detectionCon=0.8, maxHands=1)

keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["SPACE", "BACKSPACE", "CLEAR"]] 

finalText = ""
currentWord = ""  # Current word being typed
sentenceBuilder = ""  # Sentence composition area
keyboard = Controller()
hoveredKey = ""  # Store the currently hovered key
showPreview = False  # Flag to show preview

# Common word suggestions
common_words = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "HAD", "BY", "WORD", "WHAT", "SAID", "EACH", "WHICH", "SHE", "DO", "HOW", "THEIR", "IF", "WILL", "UP", "OTHER", "ABOUT", "OUT", "MANY", "THEN", "THEM", "THESE", "SO", "SOME", "HER", "WOULD", "MAKE", "LIKE", "INTO", "HIM", "HAS", "TWO", "MORE", "GO", "NO", "WAY", "COULD", "MY", "THAN", "FIRST", "BEEN", "CALL", "WHO", "ITS", "NOW", "FIND", "LONG", "DOWN", "DAY", "DID", "GET", "COME", "MADE", "MAY", "PART"]

isClicked = False
clickStartTime = 0
cooldownTime = 0.5 
KEY_COLOR = (102, 204, 204)         
KEY_HOVER_COLOR = (41, 128, 185)    
KEY_CLICK_COLOR = (52, 152, 219)    
TEXT_COLOR = (255, 255, 255)        
TEXT_FIELD_COLOR = (44, 62, 80, 150)  
BORDER_COLOR = (189, 195, 199)     

class Button():
    def __init__(self, pos, text, size=None):
        self.pos = pos
        self.text = text
        
        if text in ["SPACE", "BACKSPACE", "CLEAR"]:
            if text == "SPACE":
                self.size = [300, 85]
            else:
                self.size = [200, 85]
        else:
            self.size = [85, 85] if size is None else size
            
        self.clicked = False
        self.clickTime = 0

def drawAll(img, buttonList):
    original_img = img.copy()
    keyboard_overlay = np.zeros_like(img)
    cv2.rectangle(keyboard_overlay, (30, 30), (1250, 450), (44, 62, 80), cv2.FILLED)
    img = cv2.addWeighted(keyboard_overlay, 0.3, img, 1.0, 0)
    cv2.rectangle(img, (30, 30), (1250, 450), BORDER_COLOR, 2)
    
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        key_overlay = img.copy()
        cv2.rectangle(key_overlay, (x, y), (x + w, y + h), KEY_COLOR, cv2.FILLED)
        img = cv2.addWeighted(key_overlay, 0.7, img, 0.3, 0)
        cv2.rectangle(img, (x, y), (x + w, y + h), BORDER_COLOR, 1)
        cvzone.cornerRect(img, (x, y, w, h), 20, rt=0, colorC=BORDER_COLOR)
        
        if button.text in ["SPACE", "BACKSPACE", "CLEAR"]:
            font_scale = 2
            text_x = x + 20
        else:
            font_scale = 4
            text_x = x + 20
            
        cv2.putText(img, button.text, (text_x, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, font_scale, TEXT_COLOR, 2)
    
    return img

buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == "SPACE":
            pos_x = 390
            pos_y = 100 * i + 50
        elif key == "BACKSPACE":
            pos_x = 700
            pos_y = 100 * i + 50
        elif key == "CLEAR":
            pos_x = 910
            pos_y = 100 * i + 50
        else:
            pos_x = 100 * j + 50
            pos_y = 100 * i + 50
        
        buttonList.append(Button([pos_x, pos_y], key))

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    img = drawAll(img, buttonList)
    
    # Reset hover state
    showPreview = False
    hoveredKey = ""
    
    if hands:
        lmList = hands[0]['lmList']
        
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
            
            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                # Set preview for hovered key
                showPreview = True
                hoveredKey = button.text
                hover_overlay = img.copy()
                cv2.rectangle(hover_overlay, (x, y), (x + w, y + h), KEY_HOVER_COLOR, cv2.FILLED)
                img = cv2.addWeighted(hover_overlay, 0.7, img, 0.3, 0)
                cvzone.cornerRect(img, (x, y, w, h), 20, rt=0, colorC=BORDER_COLOR)
                
                if button.text in ["SPACE", "BACKSPACE", "CLEAR"]:
                    font_scale = 2
                    text_x = x + 20
                else:
                    font_scale = 4
                    text_x = x + 20
                    
                cv2.putText(img, button.text, (text_x, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, font_scale, TEXT_COLOR, 2)
                
                x1, y1 = lmList[8][0], lmList[8][1]
                x2, y2 = lmList[12][0], lmList[12][1]
                l, _, _ = detector.findDistance((x1, y1), (x2, y2))
                
                current_time = time.time()
                if l < 40 and not isClicked and (current_time - clickStartTime) > cooldownTime:
                    click_overlay = img.copy()
                    cv2.rectangle(click_overlay, (x, y), (x + w, y + h), KEY_CLICK_COLOR, cv2.FILLED)
                    img = cv2.addWeighted(click_overlay, 0.9, img, 0.1, 0)
                    
                    if button.text == "SPACE":
                        # Complete current word and add to sentence
                        if currentWord:
                            sentenceBuilder += currentWord + " "
                            finalText += currentWord + " "
                            currentWord = ""
                        else:
                            sentenceBuilder += " "
                            finalText += " "
                        keyboard.press(" ")
                        keyboard.release(" ")
                    elif button.text == "BACKSPACE":
                        if currentWord:
                            currentWord = currentWord[:-1]
                        elif sentenceBuilder:
                            sentenceBuilder = sentenceBuilder[:-1]
                        if finalText:
                            finalText = finalText[:-1]
                            keyboard.press('\b')
                            keyboard.release('\b')
                    elif button.text == "CLEAR":
                        finalText = ""
                        currentWord = ""
                        sentenceBuilder = ""
                    else:
                        # Add letter to current word
                        currentWord += button.text
                        finalText += button.text
                        keyboard.press(button.text)
                        keyboard.release(button.text)
                    
                    isClicked = True
                    clickStartTime = current_time
                    button.clicked = True
                    button.clickTime = current_time
                    
                elif l > 40:
                    isClicked = False
    
    # Draw sentence composition box
    composition_overlay = img.copy()
    cv2.rectangle(composition_overlay, (50, 450), (1230, 490), (70, 130, 180), cv2.FILLED)
    img = cv2.addWeighted(composition_overlay, 0.8, img, 0.2, 0)
    cv2.rectangle(img, (50, 450), (1230, 490), (135, 206, 235), 2)
    
    # Show current word being built + sentence so far
    composition_text = sentenceBuilder + currentWord
    if not composition_text:
        composition_text = "Build your sentence here..."
        cv2.putText(img, composition_text, (60, 475),
                   cv2.FONT_HERSHEY_PLAIN, 2, (150, 150, 150), 2)
    else:
        cv2.putText(img, composition_text, (60, 475),
                   cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    
    # Show word suggestions if typing
    if currentWord and len(currentWord) >= 2:
        suggestions = [word for word in common_words if word.startswith(currentWord.upper())][:3]
        if suggestions:
            suggestion_text = f"Suggestions: {', '.join(suggestions[:3])}"
            cv2.putText(img, suggestion_text, (650, 475),
                       cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 127), 1)
    
    # Draw typing preview bar (shows what letter you're about to type)
    if showPreview and hoveredKey:
        preview_overlay = img.copy()
        cv2.rectangle(preview_overlay, (50, 410), (300, 440), (100, 200, 100), cv2.FILLED)
        img = cv2.addWeighted(preview_overlay, 0.8, img, 0.2, 0)
        cv2.rectangle(img, (50, 410), (300, 440), (0, 255, 0), 2)
        
        preview_text = f"Next: {hoveredKey}"
        cv2.putText(img, preview_text, (60, 430),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    
    # Draw main text field (shows ALL typed text like a real keyboard)
    text_field_overlay = img.copy()
    cv2.rectangle(text_field_overlay, (50, 500), (1230, 650), TEXT_FIELD_COLOR, cv2.FILLED)
    img = cv2.addWeighted(text_field_overlay, 0.7, img, 0.3, 0)
    cv2.rectangle(img, (50, 500), (1230, 650), BORDER_COLOR, 2)
    
    # Display complete text with word wrapping like a real keyboard
    if finalText:
        # Split text into lines that fit the screen width
        max_chars_per_line = 50
        lines = []
        current_line = ""
        
        for char in finalText:
            if char == '\n' or len(current_line) >= max_chars_per_line:
                lines.append(current_line)
                current_line = "" if char == '\n' else char
            else:
                current_line += char
        
        if current_line:
            lines.append(current_line)
        
        # Show last 4 lines (like a text editor)
        display_lines = lines[-4:] if len(lines) > 4 else lines
        
        for i, line in enumerate(display_lines):
            y_pos = 530 + (i * 30)
            cv2.putText(img, line, (60, y_pos),
                       cv2.FONT_HERSHEY_PLAIN, 2.5, TEXT_COLOR, 2)
        
        # Add blinking cursor at the end
        cursor = "|" if int(time.time() * 2) % 2 else ""
        if display_lines:
            last_line = display_lines[-1]
            cursor_x = 60 + len(last_line) * 15
            cursor_y = 530 + (len(display_lines) - 1) * 30
            cv2.putText(img, cursor, (cursor_x, cursor_y),
                       cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 255, 0), 2)
    else:
        # Show placeholder text when empty
        cv2.putText(img, "Start typing...", (60, 550),
                   cv2.FONT_HERSHEY_PLAIN, 2.5, (150, 150, 150), 2)
    
    # Show statistics
    word_count = len([w for w in finalText.split() if w.strip()])
    char_count = f"Words: {word_count} | Characters: {len(finalText)}"
    cv2.putText(img, char_count, (950, 520),
               cv2.FONT_HERSHEY_PLAIN, 1.2, (200, 200, 200), 1)
    
    # Show current word being typed
    if currentWord:
        current_word_display = f"Typing: {currentWord}"
        cv2.putText(img, current_word_display, (60, 520),
                   cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 127), 1)
    
    instructions_overlay = img.copy()
    cv2.rectangle(instructions_overlay, (30, 10), (350, 30), (44, 62, 80), cv2.FILLED)
    cv2.rectangle(instructions_overlay, (1000, 10), (1250, 30), (44, 62, 80), cv2.FILLED)
    img = cv2.addWeighted(instructions_overlay, 0.5, img, 0.5, 0)
    
    cv2.putText(img, "Virtual Keyboard", (50, 25),
                cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
    cv2.putText(img, "Pinch to type", (1050, 25),
                cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)
    
    cTime = time.time()
    fps = 1 / (cTime - clickStartTime + 0.01)
    fps_overlay = img.copy()
    cv2.rectangle(fps_overlay, (1140, 680), (1230, 710), (44, 62, 80), cv2.FILLED)
    img = cv2.addWeighted(fps_overlay, 0.5, img, 0.5, 0)
    cv2.putText(img, f'FPS: {int(fps)}', (1150, 700), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    
    cv2.imshow("Virtual Keyboard", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

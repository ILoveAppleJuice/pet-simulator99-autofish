import pyautogui
from PIL import Image
import time

import tkinter as tk
from tkinter import PhotoImage,Label,Frame

import numpy as np
import cv2
from mss import mss
from PIL import Image
import math

import matplotlib.pyplot as plt

import pygetwindow as gw


def get_window_under_cursor():
    x, y = pyautogui.position()
    window = gw.getWindowsAt(x, y)
    if window:
        return window[0].title
    return None

def get_focused_window_title():
    try:
        focused_window = gw.getActiveWindow()
        if focused_window is not None:
            return focused_window.title
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def color_similarity_to_green(pixel_bgr_color):
    # Define the green color in BGR
    green_color = np.array([0, 255, 0], dtype=np.uint8)

    # Calculate Euclidean distance between the given color and green
    distance = np.linalg.norm(pixel_bgr_color - green_color)

    # Normalize the distance to a similarity score (1 for very similar, 0 for very different)
    similarity = 1 - (distance / (np.sqrt(255**2 + 255**2 + 255**2)))

    return similarity


tracker = cv2.TrackerKCF_create()

template = cv2.imread('t2.png')
h, w, _ = template.shape

bounding_box = {'top': 245, 'left': 1430, 'width': 100 , 'height': 610}
#bounding_box = {'top': 0, 'left': 0, 'width': 2000 , 'height': 2000}

sct = mss()


sct_img = sct.grab(bounding_box)
img = np.array(sct_img)

bob_height = 0
previous_height = bob_height

mouse_down = False

points = [10,20,40,100,150,250,300]

enabled = False


root = tk.Tk()
root.title("REEEEEEEEEE")

# Adjust size  
root.geometry("300x250") 
root.attributes('-topmost', True)
  
# Add image file 
bg = PhotoImage(file = "shrek.png") 
  
# Show image using label 
label1 = Label( root, image = bg) 
label1.place(x = 0, y = 0) 
  
label2 = Label( root, text = "pet sim 99 auto fishy ft. shrek") 
label2.pack(pady = 30) 
label2.config(font=('Broadway',12),fg="red")
  
# Create Frame 
frame1 = Frame(root) 
frame1.pack(pady = 20) 


# Function to be called when the button is clicked
def on_button_click():
    global enabled
    enabled = not enabled
    
    if enabled:
        button.config(text="enabled",bg="green")
    else:
        button.config(text="disabled",bg="red")

def quit():
    root.destroy()
    cv2.destroyAllWindows()


# Create a button widget
button = tk.Button(frame1, text="disabled", command=on_button_click)
button.pack(padx=0, pady=20)  # Add padding around the button
button.config(width=40,height=1,bg="red",fg="white")

quit_btn = tk.Button(frame1, text="quit", command=quit)
quit_btn.pack(padx=0, pady=0)  # Add padding around the button
quit_btn.config(width=40,height=1,bg="red",fg="yellow")


prevFound = True

def main_loop():
    global mouse_down,enabled,prevFound,points,bob_height,previous_height,img,template,h,w,tracker

    #print("MAIN LOOP!!!")
    if not enabled:
        root.after(10,main_loop)
        return

    #time.sleep(1)
    if not get_focused_window_title() == "Roblox" or not get_window_under_cursor() == "Roblox":
        root.after(10,main_loop)
        return 

    sct_img = sct.grab(bounding_box)
    img = np.array(sct_img)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    #img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #print(img)

    # Perform template matching
    res = cv2.matchTemplate(img, template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    loc = np.where(res >= threshold)
    
    found = np.array(loc).size != 0
    if found:
        prevFound = True
        #print(bob_height)
        middle_x = int(np.mean(loc[1]) + w/2)
        middle_y = int(np.mean(loc[0]) + h/2)

        previous_height = bob_height
        bob_height = middle_y

        delta = bob_height-previous_height
        delta *= -1
        

        cv2.circle(img,(middle_x,middle_y),4,(0,0,255),3)

        add = 20
        above_point = (max(int(middle_y - h/2 - add),1),middle_x)
        below_point = (min(int(middle_y + h/2 + add),bounding_box['height']-1),middle_x)

        above_color = img[*above_point]
        below_color = img[*below_point]

        cv2.circle(img,(above_point[1],above_point[0]),4,(0,0,255),3)
        cv2.circle(img,(below_point[1],below_point[0]),4,(0,0,255),3)

        g_threshold = 0.2
        above_green = color_similarity_to_green(above_color) > g_threshold
        below_green = color_similarity_to_green(below_color) > g_threshold

        is_in = above_green and below_green


        above_green_hits = 0
        below_green_hits = 0

        # "do points above"
        for y_offset in points:
            point = (max(int(middle_y - h/2 - y_offset),1),middle_x)
            cv2.circle(img,(point[1],point[0]),4,(0,255,255),3)

            if np.mean(img[*point]) == 255:
                above_green_hits -= 1
            # if color_similarity_to_grey(img[*point]) > grey_threshold:
            #     above_green_hits += 1


        #do points below
        for y_offset in points:
            point = (min(int(middle_y + h/2 + y_offset),bounding_box['height']-1),middle_x)
            cv2.circle(img,(point[1],point[0]),4,(0,255,255),3)
            
            if np.mean(img[*point]) == 255:
                below_green_hits -= 1

            # if color_similarity_to_grey(img[*point]) > grey_threshold:
            #     below_green_hits += 1
        
        
        
        if not is_in:
            # below green hits = the bar is under the bobber thing
            # above green hits = the bar is above / there are more white points aboev the boober

            if above_green_hits < below_green_hits:
                if mouse_down == False:
                    pyautogui.mouseDown()
                    mouse_down = True
            else:
                if mouse_down == True:
                    pyautogui.mouseUp()
                    mouse_down = False
        else:
            b = 0
            #positive difference = more white above the booober = more hold = b needs to be higher
            difference = above_green_hits - below_green_hits
            b = (difference * 0.5) + 1.4

            if math.sin(time.time() * 8 * math.pi) + b > 0  :
                if mouse_down == False:
                    pyautogui.mouseDown()
                    mouse_down = True
            else:
                if mouse_down == True:
                    pyautogui.mouseUp()
                    mouse_down = False
    else:
        if prevFound:
            time.sleep(0.2)
            pyautogui.mouseDown()
            time.sleep(0.01)
            pyautogui.mouseUp()
        else:
            time.sleep(4)
            pyautogui.mouseDown()
            time.sleep(0.01)
            pyautogui.mouseUp()

        prevFound = False
        

        pass

    #cv2.imshow('screen', img)
    
    print("poop")
    root.after(10,main_loop)


root.after(1000,main_loop)

# Run the Tkinter main loop
root.mainloop()
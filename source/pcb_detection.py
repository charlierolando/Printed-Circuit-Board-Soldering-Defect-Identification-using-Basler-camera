threshold_ = 0.61

from tkinter import *
import tkinter
import cv2
from PIL import Image, ImageTk

from pypylon import pylon

import winsound

import time
import threading

import argparse
import cv2
import os

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference

def message(message):
        # Update teks pada kotak pesan
        notif.config(text=message)

def toggle_text():
    label_c = tkinter.Label(app, text="Indicator:", font=("Helvetica", 20), fg="black", highlightthickness=0, bg="grey")
    label_c.place(x = 790, y = 245)
    indicator_frame.place(x=812, y=289)
    canvas.place(x = 2000, y = 0)
    # Set notification label text
    message("Success Capturing!")
    notif.place(x=842, y=489)
    # After 2500 milliseconds (2.5 seconds), reset notification label
    app.after(2500, lambda: notif.place(x=2000, y=65))

    global camera
    global args
    # global labels
    global interpreter
    global inference_size
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    label_c1["text"] = "PCB defect not detected"
    label_c1.configure(fg="green")

    # Create circle
    indicator_canvas.create_oval(0, 0, 160, 160, fill="green", outline='green')

    label_c2.place(x = 2000, y = 80)
    label_c3.place(x = 2000, y = 80)
    label_c4.place(x = 2000, y = 80)
    label_c5.place(x = 2000, y = 80)

    if grab_result.GrabSucceeded():
        # Play a sound when image is captured
        winsound.PlaySound("success_sound.wav", winsound.SND_ASYNC)

        # Convert the image to an OpenCV format (BGR)
        frame = grab_result.Array
        frame = cv2.cvtColor(frame, cv2.COLOR_BAYER_RG2RGB)
        
        # Baru 20/07/23 Flip
        frame = cv2.flip(frame, 0)
        frame = cv2.flip(frame, 1)
        # Baru 20/07/23 Flip

        cv2_im = frame

        cv2_im_rgb = cv2_im
        cv2_im_rgb = cv2.resize(cv2_im_rgb, inference_size)
        run_inference(interpreter, cv2_im_rgb.tobytes())
        objs = get_objects(interpreter, args.threshold)[:args.top_k]
        # # Baru 20/07/23
        # cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        # # Baru 20/07/23

        cv2_im = append_objs_to_img(cv2_im, inference_size, objs, labels)

        # Edited #
        width = int(cv2_im.shape[1] * scale_percent / 100)
        height = int(cv2_im.shape[0] * scale_percent / 100)
        dim = (width, height)

        # resize image
        cv2_im = cv2.resize(cv2_im, dim, interpolation=cv2.INTER_AREA)
        # Edited #
        
        # Capture the latest frame and transform to image
        captured_image = Image.fromarray(cv2_im)

        # Convert captured image to photoimage
        photo_image = ImageTk.PhotoImage(image=captured_image)

        # position
        label_widget.place(x = 0, y = 0)
        
        # Displaying photoimage in the label
        label_widget.photo_image = photo_image

        # Configure image in the label
        label_widget.configure(image=photo_image)
    
def write_terminal(x, y, z):
    # Create circle
    indicator_canvas.create_oval(0, 0, 160, 160, fill="red", outline='red')

    # Play a sound when image is captured
    winsound.PlaySound("defect_found.wav", winsound.SND_ASYNC)

    label_c1["text"] = "PCB defect detected"
    label_c1.configure(fg="red")
    label_c2["text"] = "Defect:"
    label_c2.configure(fg="black")
    label_c2.place(x = 790, y = 90)
    label_c3["text"] = x
    label_c3.configure(fg="red")
    label_c3.place(x = 790, y = 110)
    label_c4["text"] = y
    label_c4.configure(fg="red")
    label_c4.place(x = 790, y = 130)
    label_c5["text"] = z
    label_c5.configure(fg="red")
    label_c5.place(x = 790, y = 150)

def append_objs_to_img(cv2_im, inference_size, objs, labels):
    height, width, channels = cv2_im.shape
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]
    label_ = ''
    label_counter = [0, 0, 0]

    for obj in objs:
        bbox = obj.bbox.scale(scale_x, scale_y)
        x0, y0 = int(bbox.xmin), int(bbox.ymin)
        x1, y1 = int(bbox.xmax), int(bbox.ymax)

        percent = int(100 * obj.score)

        label = '{}% {}'.format(percent, labels.get(obj.id, obj.id))
        label_ = label_ + label + '\n'

        if labels.get(obj.id, obj.id) == 'Opens':
            label_counter[0] = label_counter[0] + 1
        elif labels.get(obj.id, obj.id) == 'Short circuit':
            label_counter[1] = label_counter[1] + 1
        elif labels.get(obj.id, obj.id) == 'Toomuch':
            label_counter[2] = label_counter[2] + 1

        cv2_im = cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2_im = cv2.putText(cv2_im, label, (x0, y0+30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
        
    # print(labels.get(obj.id, obj.id))
    # write_terminal(labels.get(obj.id, obj.id))
    # write_terminal(label_)

    label_a_ = label_b_ = label_c_ = ''
    detect_status = 0

    if label_counter[0] > 0:
        label_a_ = str("Opens: " + str(label_counter[0]))
        detect_status = 1
    if label_counter[1] > 0:
        label_b_ = str("Short circuit: " + str(label_counter[1]))
        detect_status = 1
    if label_counter[2] > 0:
        label_c_ = str("Toomuch: " + str(label_counter[2]))
        detect_status = 1

    if detect_status != 0:
        write_terminal(label_a_, label_b_, label_c_)

    return cv2_im

# def thread_1(num):
#     # function to print text
#     print("Text")

# def thread_2(num):
#     # function to print text
#     print("Text")

# # thread   
# t1 = threading.Thread(target = thread_1, args=(10,))
# t1.start()
# t2 = threading.Thread(target = thread_2, args=(10,))
# t2.start()

# Create a GUI app
app = tkinter.Tk()
app.iconbitmap("logo.ico")
app.title("PCB Soldering Detection")

# percent of original size
scale_percent = 59.6

# save data terminal
terminal_temp = ''

# Create an instant camera object
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Open the camera
camera.Open()

# ExposureTime # Bisa buat atur kecerahan
camera.ExposureTime.SetValue(50000) # 50000

# Start grabbing frames
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

# Bind the app with Escape keyboard to
# quit app whenever pressed
app.bind('<Escape>', lambda e: app.quit())
app.geometry("300x300")
# app.attributes('-fullscreen', True)

# Create a label and display it on app
label_widget = Label(app)
label_widget.pack()

# bg
canvas = tkinter.Canvas(app, width=761, height=572, bg="black")
# canvas.place(x = 2000, y = 0)
canvas.place(x = 0, y = 0)

canvas2 = tkinter.Canvas(app, width=227, height=455, bg="grey")
canvas2.place(x = 778, y = 17)

# Create circle as indicator
# Make frame
indicator_frame = tkinter.Frame(app)
# indicator_frame.place(x=812, y=70)
indicator_frame.place(x=2000, y=70)

# Make canvas
indicator_canvas = tkinter.Canvas(indicator_frame, bg='grey', width=162, height=162, highlightthickness=0)
indicator_canvas.pack()

# Make notification
notif = tkinter.Label(app, text="", font=("Arial", 8), fg="green")
notif.place(x=2000, y=65)

# Label and Button Camera
label_a = tkinter.Label(app, text="Camera is close", font=("Helvetica", 24), fg="red", highlightthickness=0)
# label_a.place(x = 778, y = 10)
label_a.place(x = 2000, y = 10)

label_b = tkinter.Label(app, text="Terminal:", font=("Helvetica", 20), fg="black", highlightthickness=0, bg="grey")
label_b.place(x = 790, y = 25)

label_c1 = tkinter.Label(app, text="", font=("Helvetica", 12), fg="black", highlightthickness=0, bg="grey")
label_c1.place(x = 790, y = 64)

label_c2 = tkinter.Label(app, text="", font=("Helvetica", 12), fg="black", highlightthickness=0, bg="grey")
label_c2.place(x = 2000, y = 46)

label_c3 = tkinter.Label(app, text="", font=("Helvetica", 12), fg="black", highlightthickness=0, bg="grey")
label_c3.place(x = 2000, y = 46)

label_c4 = tkinter.Label(app, text="", font=("Helvetica", 12), fg="black", highlightthickness=0, bg="grey")
label_c4.place(x = 2000, y = 46)

label_c5 = tkinter.Label(app, text="", font=("Helvetica", 12), fg="black", highlightthickness=0, bg="grey")
label_c5.place(x = 2000, y = 46)

button_1 = tkinter.Button(app, text="Capture Image", font=("Helvetica", 18) , command=toggle_text) #, width=20, height=5)
button_1.place(x = 804, y = 514)

default_model_dir = ''
default_model = 'pcb_edgetpu_4Agus23.tflite'
default_labels = 'labels.txt'
parser = argparse.ArgumentParser()
parser.add_argument('--model', help='.tflite model path',
                    default=os.path.join(default_model_dir,default_model))
parser.add_argument('--labels', help='label file path',
                    default=os.path.join(default_model_dir, default_labels))
parser.add_argument('--top_k', type=int, default=30,
                    help='number of categories with highest score to display')
parser.add_argument('--camera_idx', type=int, help='Index of which video source to use. ', default = camera)
parser.add_argument('--threshold', type=float, default=threshold_,
                    help='classifier score threshold')
args = parser.parse_args()

# print('Loading {} with {} labels.'.format(args.model, args.labels))
interpreter = make_interpreter(args.model)
interpreter.allocate_tensors()
labels = read_label_file(args.labels)
inference_size = input_size(interpreter)

# def main():
#     Repeat the same process after every 10 seconds
#     label_widget.after(10, main)

if __name__ == '__main__':
    # main()
    app.mainloop()
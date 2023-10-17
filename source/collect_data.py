from pypylon import pylon
import cv2

# Data Dir
IMAGE_RGB_PATH = ""
IMAGE_RGB_NAME = "data_{}.jpg"

# count data
frame_num = 0

# scale pict to display
# not change scale to save
# percent of original size
scale_percent = 40

# Create an instant camera object
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Open the camera
camera.Open()

# ExposureTime # Bisa buat atur kecerahan
camera.ExposureTime.SetValue(50000) # 50000

# Start grabbing frames
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

while camera.IsGrabbing():
    # Retrieve the grabbed image from the camera buffer
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grab_result.GrabSucceeded():
        # Convert the image to an OpenCV format (BGR)
        frame = grab_result.Array
        frame = cv2.cvtColor(frame, cv2.COLOR_BAYER_RG2BGR)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BAYER_RG2RGB)
        
        # Baru 20/07/23 Flip
        frame = cv2.flip(frame, 0)
        frame = cv2.flip(frame, 1)
        # Baru 20/07/23 Flip

        # Display the frame
        # frame_new = cv2.cvtColor(frame_new, cv2.COLOR_RGB2BGR)
        frame_new = frame
        width = int(frame_new.shape[1] * scale_percent / 100)
        height = int(frame_new.shape[0] * scale_percent / 100)
        dim = (width, height)
        frame_new = cv2.resize(frame_new, dim, interpolation=cv2.INTER_AREA)
        cv2.imshow('Collect Data', frame_new)
        # Display the frame

        
        # Check for user input to exit the loop
        key = cv2.waitKey(1)
        if key == ord('c'):
            cv2.imwrite(IMAGE_RGB_PATH + IMAGE_RGB_NAME.format(frame_num), frame)
            print('Capture %d'%frame_num)
            frame_num += 1

        elif key == 27 or key == ord('x'):  # Press 'Esc' or 'x' key to exit
            break
        
# Stop grabbing frames and close the camera
camera.StopGrabbing()
camera.Close()

# Destroy the OpenCV window
cv2.destroyAllWindows()
print("Loading libraries...")
import cv2
from ultralytics import YOLO
import time
print("done!")
# from Face_tracker import DroneTracker
# from djitellopy import Tello

# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# print("Setting up class names...")
# # opening the file in read mode
# with open("utils/coco.txt", "r") as file:
#     # reading the file
#     class_list = file.read()
#     # replacing end splitting the text | when newline ('\n') is seen.
#     class_list = class_list.split("\n")

# # Generate random colors for class list
# detection_colors = []
# for i in range(len(class_list)):
#     r = random.randint(0, 255)
#     g = random.randint(0, 255)
#     b = random.randint(0, 255)
#     detection_colors.append((b, g, r))

# print("Setting up yolo...")
# # load a pretrained YOLOv8n model
# model = YOLO("yolov8n.pt")

# print("Setting up Tello...")
# tello = Tello()
# tello.connect()
# tello.takeoff()
# tello.move_up(40)
# tello.streamon()

# tracker = DroneTracker(tello)
# tracker.print_battery_state()

# # Vals to resize video frames | small frame optimise the run
# frame_wid = 640
# frame_hyt = 480

# # cap = cv2.VideoCapture(1)
# # cap = cv2.VideoCapture(0)

# # if not cap.isOpened():
# # print("Cannot open camera")
# # exit()

# print("Statrting main loop...")
# while True:
#     start = time.time()
#     # Capture frame-by-frame
#     # ret, frame = cap.read()
#     # if frame is read correctly ret is True

#     frame = tello.get_frame_read().frame

#     # if not ret:
#     # print("Can't receive frame (stream end?). Exiting ...")
#     # break

#     # resize the frame | small frame optimise the run
#     frame = cv2.resize(frame, (frame_wid, frame_hyt))

#     # Predict on image
#     detect_params = model.predict(source=frame, conf=0.45, classes=[0], max_det=60)[0]

#     # Convert tensor array to numpy
#     DP = detect_params.numpy()
#     # print(DP)

#     bb = [-2, 0, 0, 0]

#     if len(DP) != 0:
#         boxes = detect_params.boxes
#         # for i in range(len(detect_params)):
#         # print(i)
#         box = boxes[0] # returns one box
#         clsID = box.cls.numpy()[0]
#         conf = box.conf.numpy()[0]
#         bb = box.xyxy.numpy()[0]

#         cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), [255, 255, 0], 3)

#         # Display class name and confidence
#         font = cv2.FONT_HERSHEY_COMPLEX
#         cv2.putText(frame, class_list[int(clsID)] + " " + str(round(conf * 100, 1)) + "%", (int(bb[0]), int(bb[1]) - 10), font, 1, (248, 0, 0), 2)

#     # end time to compute the fps
#     end = time.time()
#     # show the time it took to process 1 frame
#     total = end - start
#     fps = f"FPS: {1 / total:.0f}"
#     cv2.putText(frame, fps, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 248), 8)

#     # Display the resulting frame
#     cv2.imshow('ObjectDetection', frame)

#     tracker.trackTarget([bb[0] // 2 + bb[2] // 2, bb[1] + 40], frame_wid, frame_hyt)

#     # Terminate run when "Q" pressed
#     if cv2.waitKey(1) == ord('q'):
#         break

# tello.send_rc_control(0, 0, 0, 0)
# tello.land()
# tello.streamoff()
# # When everything done, release the capture
# # cap.release()
# cv2.destroyAllWindows()


class PersonRecognision:
    def __init__(self):
        with open("utils/coco.txt", "r") as file:
            # reading the file
            self.class_list = file.read()
            # replacing end splitting the text | when newline ('\n') is seen.
            self.class_list = self.class_list.split("\n")
        
        self.model = YOLO("yolov8n.pt")

    def detect(self, frame):
        start = time.time()
        detect_params = self.model.predict(source=frame, conf=0.45, classes=[0], max_det=60)[0]
        DP = detect_params.numpy()

        bb = [-2, 0, 0, 0]

        if len(DP) != 0:
            boxes = detect_params.boxes
            box = boxes[0]
            clsID = box.cls.numpy()[0]
            conf = box.conf.numpy()[0]
            bb = box.xyxy.numpy()[0]
            cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), [255, 255, 0], 3)
            font = cv2.FONT_HERSHEY_COMPLEX
            cv2.putText(frame, self.class_list[int(clsID)] + " " + str(round(conf * 100, 1)) + "%", (int(bb[0]), int(bb[1]) - 10), font, 1, (248, 0, 0), 2)

        end = time.time()
        # show the time it took to process 1 frame
        total = end - start
        fps = f"FPS: {1 / total:.0f}"
        cv2.putText(frame, fps, (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 248), 4)

        return frame, bb

    def detect_gpu(self, frame):
        start = time.time()
        detect_params = self.model.predict(source=frame, conf=0.45, classes=[0], max_det=60)[0]
        DP = detect_params.cpu().numpy()

        bb = [-2, 0, 0, 0]

        if len(DP) != 0:
            boxes = detect_params.boxes
            box = boxes[0]
            clsID = box.cls.cpu().numpy()[0]
            conf = box.conf.cpu().numpy()[0]
            bb = box.xyxy.cpu().numpy()[0]
            cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), [255, 255, 0], 3)
            font = cv2.FONT_HERSHEY_COMPLEX
            cv2.putText(frame, self.class_list[int(clsID)] + " " + str(round(conf * 100, 1)) + "%",
                        (int(bb[0]), int(bb[1]) - 10), font, 1, (248, 0, 0), 2)

        end = time.time()
        # show the time it took to process 1 frame
        total = end - start
        fps = f"FPS: {1 / total:.0f}"
        cv2.putText(frame, fps, (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 248), 4)

        return frame, bb
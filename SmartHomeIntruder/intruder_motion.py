import cv2
import face_recognition
import numpy as np
import time
from pathlib import Path
import pyttsx3
from playsound import playsound
from config import send_email_alert

# -----------------------------
#  TEXT TO SPEECH (TTS)
# -----------------------------
engine = pyttsx3.init()
engine.setProperty("rate", 165)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# -----------------------------
#  LOAD KNOWN FACES
# -----------------------------
known_face_encodings = []
known_face_names = []

known_faces_dir = Path(__file__).parent / "known_faces"

for img in known_faces_dir.glob("*.*"):
    name = img.stem
    image = face_recognition.load_image_file(img)
    encoding = face_recognition.face_encodings(image)[0]

    known_face_encodings.append(encoding)
    known_face_names.append(name)

# -----------------------------
#  EVENTS FOLDER
# -----------------------------
events_dir = Path(__file__).parent / "events"
events_dir.mkdir(exist_ok=True)

# Cooldown
last_seen = {}
COOLDOWN = 15  # seconds

print("▶️ Intruder detection system started…")

video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    if not ret:
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    current_time = time.time()

    for i, face_encoding in enumerate(face_encodings):

        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            index = matches.index(True)
            name = known_face_names[index]

        # -----------------------------
        #  KNOWN PERSON
        # -----------------------------
        if name != "Unknown":
            if name not in last_seen or (current_time - last_seen[name]) > COOLDOWN:

                print(f"✔ Access Granted: {name}")
                speak(f"{name}, welcome! Access granted.")

                welcome_sound = Path(__file__).parent / "welcome.mp3"
                if welcome_sound.exists():
                    playsound(str(welcome_sound))

                last_seen[name] = current_time

        # -----------------------------
        #  UNKNOWN PERSON
        # -----------------------------
        else:
            if "Unknown" not in last_seen or (current_time - last_seen["Unknown"]) > COOLDOWN:

                print("❌ Unknown person detected! Sending email…")
                speak("Warning! Unknown person detected.")

                alarm = Path(__file__).parent / "alarm.mp3"
                if alarm.exists():
                    playsound(str(alarm))

                # Save image of intruder
                top, right, bottom, left = face_locations[i]
                face_image = frame[top:bottom, left:right]

                timestamp = time.strftime("%Y%m%d_%H%M%S")
                image_path = events_dir / f"unknown_{timestamp}.jpg"
                cv2.imwrite(str(image_path), face_image)

                # Send email with attachment
                send_email_alert("Unknown person detected!", str(image_path))

                last_seen["Unknown"] = current_time

    cv2.imshow("Smart Home Intruder Detection", frame)

    if cv2.waitKey(1) == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

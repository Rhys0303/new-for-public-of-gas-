from flask import Flask, request, render_template, Response, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
import time

app = Flask(__name__)
model = YOLO('best.pt') # Your custom model

latest_gas_status = "Waiting for data..."
objects_in_room = []
latest_frame = None

def evaluate_safety():
    person_present = "human" in objects_in_room

    try:
        gas_level = int(float(latest_gas_status))
    except:
        gas_level = 0

    if gas_level > 700:
        is_gas_alarm_active = True
    else:
        is_gas_alarm_active = False

    if is_gas_alarm_active:
        print("Critical: Gas Leak Detected!")
        return "TRIGGER_ALARM"
    
    elif "fire" in objects_in_room and not person_present:
        print("ALERT: Unattended fire detected!")
        return "TRIGGER_ALARM"

    elif "fire" in objects_in_room and person_present:
        print("Status: Attended fire. System Safe.")
        return "SAFE"
    
    else:
        return "SAFE"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gas', methods=['POST'])
def receive_gas():
    global latest_gas_status
    if 'status' in request.form:
        latest_gas_status = request.form['status']

    cmd = evaluate_safety()
    return jsonify({"command": cmd}), 200

@app.route('/api/status')
def get_status():
    system_status = evaluate_safety()
    return jsonify({
        "system": "Critical Danger" if system_status == "TRIGGER_ALARM" else "SAFE",
        "gas": latest_gas_status,
        "objects": objects_in_room
    })

@app.route('/upload', methods=['POST'])
def receive_data():
    global latest_frame
    global objects_in_room
    if 'image' in request.files:
        # Convert incoming bytes to OpenCV image
        file_bytes = np.frombuffer(request.files['image'].read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Run YOLO inference
        results = model(img, verbose=False)
        
        names = model.names
        class_ids = results[0].boxes.cls.tolist()
        objects_in_room = [names[int(id)].lower() for id in class_ids]


        latest_frame = results[0].plot()
        
    return "Frame Processed", 200

def generate_video():
    global latest_frame
    while True:
        if latest_frame is None:
            time.sleep(0.5)
            continue
        ret, buffer = cv2.imencode('.jpg', latest_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        time.sleep(0.5)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

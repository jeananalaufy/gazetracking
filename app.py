from flask import Flask, render_template, redirect, url_for, request, jsonify
import cv2
from gaze_tracking import GazeTracking  # gaze_tracking library from Github is imported

app = Flask(__name__)
app.secret_key = b'secretkey'

# Initialize GazeTracking object and gaze data dictionary
gaze = GazeTracking()
gaze_data = {'Blinking': 0, 'Looking right': 0, 'Looking left': 0, 'Looking center': 0, 'No gaze detected': 0}

# Function to generate video frames from the webcam
def generate_frames():
    camera = cv2.VideoCapture(0)
    while camera.isOpened():
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the progress/feedback page
@app.route('/progress')
def progress():
    return render_template('progress.html')

# Route for the welcome page
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# Route for the use cases page
@app.route('/use_cases')
def use_cases():
    return render_template('use_cases.html')

# Route to capture and process gaze direction
@app.route('/gaze_direction')
def gaze_direction():
    camera = cv2.VideoCapture(0)  # Open webcam
    success, frame = camera.read()  # Read a frame
    camera.release()  # Release the webcam

    if not success:
        return jsonify({'direction': 'No frame captured'}), 500  # Return an error message if no frame captured

    gaze.refresh(frame)  # Refresh gaze data based on the frame

    # Determine the gaze direction
    if gaze.is_blinking():
        direction = "Blinking"
    elif gaze.is_right():
        direction = "Looking right"
    elif gaze.is_left():
        direction = "Looking left"
    elif gaze.is_center():
        direction = "Looking center"
    else:
        direction = "No gaze detected"

    gaze_data[direction] += 1  # Increment count for detected gaze direction

    return jsonify({'direction': direction})  # Return detected gaze direction 

# Route to handle users username submission
@app.route('/username', methods=['POST'])
def username():
    username = request.form.get('username')  # Get username from form data
    return redirect(url_for('use_cases', username=username))  # Redirect to use_cases page with users inputted username 

# Route to stop tracking and return the gaze data
@app.route('/stop_tracking')
def stop_tracking():
    return jsonify(gaze_data)  # Return current gaze data 

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Run the Flask application 

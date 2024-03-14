import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import keyboard
from RsInstrument import *

# Set up serial communication with oscilloscope
ser = serial.Serial('COM3', 115200)
time.sleep(1)  # Wait for oscilloscope to initialize

# Initialize variables
index = 0
left_waveform = []
right_waveform = []
time_array = []

# Set up Matplotlib for Flask
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Create figure and axes for plot
fig, ax = plt.subplots()
line1, = ax.plot(time_array, left_waveform)
line2, = ax.plot(time_array, right_waveform)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude (V)')
ax.set_title('Ion Collection Rate')

# Function to acquire data from oscilloscope and update plot
def update_plot():
    global index

    # Clear existing plot
    ax.clear()

    # Acquire data from oscilloscope
    ser.write(b'ACQuire:STATE ON\n')
    time.sleep(0.1)
    data = ser.read(1024)
    lines = data.decode().strip().split('\n')
    left_waveform_data = []
    right_waveform_data = []
    for line in lines:
        if line.startswith('DATA:CH1'):
            values = list(map(float, line.split()[1:]))
            left_waveform_data.extend(values)
        elif line.startswith('DATA:CH2'):
            values = list(map(float, line.split()[1:]))
            right_waveform_data.extend(values)

    # Store data in arrays
    time_array.append(index)
    left_waveform.append(left_waveform_data)
    right_waveform.append(right_waveform_data)

    # Limit number of data points in plot
    if len(left_waveform) > 100:
        left_waveform = left_waveform[-100:]
        right_waveform = right_waveform[-100:]
        time_array = time_array[-100:]

    # Update plot
    line1.set_ydata(left_waveform)
    line2.set_ydata(right_waveform)
    ax.set_xlim(time_array[-100:])
    fig.canvas.draw()

# Flask route for updating plot
@app.route('/update_plot')
def update_plot_route():
    global index
    index += 1
    update_plot()
    fig.savefig('static/plot.png')
    return 'OK'

# Flask route for homepage
@app.route('/')
def homepage():
    return render_template('index.html')

# Flask route for stopping the acquisition
@app.route('/stop')
def stop_acquisition():
    ser.write(b'ACQuire:STATE OFF\n')
    return 'OK'

# Main function to run the Flask app and acquire data
def main():
    app.run(debug=True, threaded=True)

    while True:
        if keyboard.is_pressed('q'):
            break
        update_plot()
        time.sleep(0.1)

if __name__ == '__main__':
    main()

import serial
import time
import requests

PORT = '/dev/ttyACM0' # Double check this matches your Pi
BAUD_RATE = 9600
BRAIN_URL = 'http://localhost:5000/gas'

def read_sensor():
    print(f"Connecting to Arduino on {PORT}...")
    try:
        arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)
        time.sleep(2) 
        print("Gas Node Connected! Forwarding data...")

        while True:
            if arduino.in_waiting > 0:
                raw_data = arduino.readline().decode('utf-8').rstrip()
                print(f"[MQ9]: {raw_data}")
                
                try:
                    # Send data to Brain AND wait for the command back
                    response = requests.post(BRAIN_URL, data={'status': raw_data}, timeout=1)
                    brain_command = response.json().get('command')

                    # Trigger the physical hardware alarm if the Brain says so
                    if brain_command == "TRIGGER_ALARM":
                        print("🚨 Brain ordered an alarm! Sending to Arduino...")
                        arduino.write(b"ALARM_ON\n") 
                    elif brain_command == "SAFE":
                        arduino.write(b"ALARM_OFF\n")

                except requests.exceptions.RequestException:
                    print("Could not reach the Brain.")
                    
    except serial.SerialException as e:
        print(f"Hardware Error: {e}")
    except KeyboardInterrupt:
        print("\nClosing connection.")
        if 'arduino' in locals():
            arduino.close()

if __name__ == '__main__':
    read_sensor()

import serial
BAUDRATE = 115200

class MapirCamera:
    def __init__(self, state):
        self.state = state

    def trigger_camera(self, message) -> str:
        """
        Sends "on" or "off" through serial mapir_port to trigger the camera.
        """
        if not self.state.mapir_port:
            print("No Mapir camera connected")

        try:
            with serial.Serial(self.state.mapir_port, BAUDRATE, timeout=2) as ser:
                print(f"Sending '{message}' to Mapir camera on port {self.state.mapir_port}")
                # Send "on" command
                ser.write((message + "\r\n").encode('utf-8'))
                #ser.write(b"{}\n".format(message.encode('utf-8')))
                #time.sleep(2)  # Wait for the camera to process

                # Optionally, read response
                #response = ser.readline().decode('utf-8').strip()
                #print(f"Received response: {response}")
                #return f"Camera triggered: {response}"

        except serial.SerialException as e:
            return f"Serial error: {e}"
        except Exception as e:
            return f"Error: {e}"
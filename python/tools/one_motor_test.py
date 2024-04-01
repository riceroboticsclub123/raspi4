import can
import cantools
import time

# Load the DBC file
db = cantools.database.load_file("odrive-cansimple.dbc")

# Set up the CAN bus
bus = can.Bus("can0", bustype="socketcan")
axis_id = 0x0  # Assuming the axis ID is set to 0

def send_can_message(message_name, **kwargs):
    msg = db.get_message_by_name(message_name)
    data = msg.encode(kwargs)
    message = can.Message(arbitration_id=msg.frame_id | axis_id << 5, is_extended_id=False, data=data)
    bus.send(message)

def calibrate_motor():
    # Set the motor to full calibration sequence
    send_can_message('Axis0_Set_Axis_State', Axis_Requested_State=0x03)
    time.sleep(10)  # Wait for calibration to complete
    # Set the motor to closed-loop control mode
    send_can_message('Axis0_Set_Axis_State', Axis_Requested_State=0x08)
    time.sleep(2)

def set_motor_position(position):
    # Set position control mode
    send_can_message('Axis0_Set_Controller_Mode', Control_Mode=0x03, Input_Mode=0x00)
    # Move the motor to the specified position
    send_can_message('Axis0_Set_Input_Pos', Input_Pos=position, Vel_FF=0.0, Torque_FF=0.0)
    time.sleep(3)  # Wait for the motor to reach the position

# Calibrate the motor
calibrate_motor()

# Test moving the motor to position 5.0 revolutions
set_motor_position(5.0)

# Set the motor to idle state
send_can_message('Axis0_Set_Axis_State', Axis_Requested_State=0x01)

# Properly shut down the SocketCAN bus
bus.shutdown()

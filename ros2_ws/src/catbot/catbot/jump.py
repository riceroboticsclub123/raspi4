import rclpy
from rclpy.node import Node
from odrive_can.srv import AxisState
from odrive_can.msg import ControlMessage, ControllerStatus
from std_msgs.msg import Float64

TORQUE_SPIKE_THRESHOLD = 0.05  # Need to find actual working threshold for torque spike detection
MAX_TORQUE = -0.48

class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        self.gear_ratio = None 
        self.phase = 'Init'  # Initial phase
        self.poising_torque = 0.24  # [Nm]
        self.bracing_angle = 70 * (3.1415 / 180)  # [rad]
        self.standard_angle = 45 * (3.1415 / 180)  # [rad]

        # Create a client for the set_axis_state service
        self.state_client = self.create_client(AxisState, '/odrive_axis0/request_axis_state')
        while not self.state_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting for AxisState service...')
        self.axis_request = AxisState.Request()

        # Set up subscriber for the ODrive controller status
        self.controller_status_subscriber = self.create_subscription(
            ControllerStatus,
            '/odrive_axis0/controller_status',
            self.controller_status_callback,
            10
        )

        # Create ControlMessage objects for the motors
        # Top Motor
        self.motor_msg1 = ControlMessage()
        self.motor_msg1.control_mode = 3 # Set to position control initially
        self.motor_msg1.input_mode = 1 # Set to pass-through mode initially
        # Bottom Motor
        self.motor_msg2 = ControlMessage()
        self.motor_msg2.control_mode = 3  # Set to position control initially
        self.motor_msg2.input_mode = 1 # Set to pass-through mode initially

        # Set up publisher to the ODrive
        self.motor_control_publisher = self.create_publisher(ControlMessage, '/odrive_axis0/control_message', 10)

        # Set up publisher for the servo
        self.servo_publisher = self.create_publisher(Float64, 'servo_angle', 10)

        # Reference angles for the motors will be updated in the callback
        self.zero_angle1 = None
        self.zero_angle2 = None

    def controller_status_callback(self, msg):
        #### THIS ASSUMES THAT WE INITIALIZE THE LEG IN PRONED POSITION ####
        if self.zero_angle1 is None:
            self.zero_angle1 = msg1.pos_estimate   
        elif self.zero_angle2 is None:
            self.zero_angle2 = msg2.pos_estimate
        
        if self.phase == 'Init':
            # TODO: Write initialization phase that has the leg slowly go from proned, to bracing angle, to standard angle.
            self.get_logger().info('Initializing...')
            # Set motors to trajectory control
            # Code goes here
            
            # Update phase to Proning
            self.phase = 'Proning'
            self.get_logger().info('Beginning to Proning phase')
        
        elif self.phase == 'Proning':
            # Set motors to position control
            self.motor_msg1.control_mode = 3
            self.motor_msg2.control_mode = 3
            # Set motor to 0 position (proned position)
            self.motor_msg1.input_pos = 0 - self.zero_angle1
            self.motor_msg2.input_pos = 0 - self.zero_angle2
            # Publish control message for the motor
            self.motor_control_publisher.publish(self.motor_msg1)
            self.motor_control_publisher.publish(self.motor_msg2)
            # Move servo to connect the legs
            self.set_servo_angle(180)
            # Update phase to Poising
            self.phase = 'Poising'
            self.get_logger().info('Transitioning to Poising phase')
            
            ## Wait a few seconds ##
                
        elif self.phase == 'Poising':
            # Set bottom motor to torque control
            self.motor_msg2.control_mode = 1
            # Set bottom motor torque to poising_torque
            self.motor_msg2.input_torque = self.poising_torque
            # Publish control message for the motor
            self.motor_control_publisher.publish(self.motor_msg2)
            self.get_logger().info('Poising: Torque set for the motor')
            # Update phase to Pouncing
            self.phase = 'Pouncing'
            self.get_logger().info('Transitioning to Pouncing phase')

            ## Wait a fraction of a second ##

        elif self.phase == 'Pouncing':
            # Release the servo to allow the spring to actuate the bottom leg
            self.set_servo_angle(90)
            # Set bottom motor to provide maximum torque
            self.motor_msg2.input_torque = MAX_TORQUE
            # Set top motor to bracing angle (temp fix)
            self.motor_msg1.input_pos = self.bracing_angle - self.zero_angle2
            # Publish control message for the motor
            self.motor_control_publisher.publish(self.motor_msg1)
            self.motor_control_publisher.publish(self.motor_msg2)
            
            self.get_logger().info('Pouncing: Motor set to max torque')
            # Update phase to Bracing
            self.phase = 'Bracing'
            self.get_logger().info('Transitioning to Bracing phase')

        elif self.phase == 'Bracing':
            # Set bottom motor to position control
            self.motor_msg2.control_mode = 3
            # Set motor to bracing angle
            self.motor_msg2.input_pos = self.bracing_angle - self.zero_angle
            # Publish control message for the motor
            self.motor_control_publisher.publish(self.motor_msg2)
            self.get_logger().info('Bracing: Positions set to bracing angles')
            # Update phase to Landing
            self.phase = 'Landing'
            self.get_logger().info('Transitioning to Landing phase')

        elif self.phase == 'Landing':
            # Set motors to position control
            self.motor_msg1.control_mode = 3
            self.motor_msg2.control_mode = 3
            # Set motor to standard angle
            self.motor_msg1.input_pos = self.standard_angle - self.zero_angle
            self.motor_msg2.input_pos = self.standard_angle - self.zero_angle
            # Publish control message for the motor
            self.motor_control_publisher.publish(self.motor_msg1)
            self.motor_control_publisher.publish(self.motor_msg2)
            self.get_logger().info('Landing: Motor set to standard angle')
            # Reset phase to 'Proning' for the next jump
            self.phase = 'Proning'
            self.get_logger().info('Jump completed. Resetting to Proning phase for next jump')

            ## Wait like 10 seconds ##

    def set_servo_angle(self, angle):
        angle_msg = Float64()
        angle_msg.data = angle
        self.servo_publisher.publish(angle_msg)

    def set_axis_state(self, state):
        self.axis_request.axis_requested_state = state
        future = self.state_client.call_async(self.axis_request)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(f'Result for odrive_axis0: {future.result().axis_state}')

def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    node.set_axis_state(8)  # CLOSED_LOOP_CONTROL
    rclpy.spin(node)
    node.set_axis_state(1)  # AXIS_STATE_IDLE
    rclpy.shutdown()

if __name__ == '__main__':
    main()
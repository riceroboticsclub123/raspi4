import RPi.GPIO as GPIO
import time

class ServoWrapper():
    def __init__(self, id):
        print("starting servo at id: " + str(id))
        GPIO.cleanup()

        self.id = id
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(id, GPIO.OUT)
        self.servo = GPIO.PWM(id, 50)
        self.servo.start(0)

    def test(self, duty):
        print("rotating to 90 degrees!!")

        while duty <= 7:
            self.servo.ChangeDutyCycle(duty)
            time.sleep(0.1)
            self.servo.ChangeDutyCycle(0)
            time.sleep(0.1)
            duty = duty + 1

        time.sleep(2)

        print("turning back")

        self.servo.ChangeDutyCycle(2)
        time.sleep(0.5)
        self.servo.ChangeDutyCycle(0)

        print("test done!")
        self.servo.stop()

    def shutdown(self):
        print("shutting down servo...")

        self.servo.stop()
        GPIO.cleanup()
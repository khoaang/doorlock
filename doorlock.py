from gpiozero import AngularServo
from time import sleep

# Set up the servo on GPIO 18
# Ensure that your servo is connected to the correct pin, ground, and an appropriate power supply
servo = AngularServo(18, min_angle=-135, max_angle=135, min_pulse_width=0.5 /
                     1000, max_pulse_width=2.5/1000, frame_width=20/1000)
try:
    # Move from -135 degrees to 135 degrees
    servo.min()
    print("Servo at minimum position.")

    servo.max()
    print("Servo at maximum position.")
    sleep(3)  # Wait for a second

    # Move back to -135 degrees
    servo.min()
    print("Servo back at minimum position.")
    sleep(1)  # Wait for a second

except KeyboardInterrupt:
    # If there is a keyboard interrupt, reset the servo to its neutral position
    servo.angle = 0
    print("Servo reset to neutral position.")

# Clean up the servo (detach it and stop PWM)
servo.detach()
print("Servo detached.")

import RPi.GPIO as GPIO
import time

# Setup
motor_pins = [2, 3, 4, 17, 27, 22, 10, 9]  # GPIO pins connected to the relays for the motors
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

# GPIO.setup(10, GPIO.OUT)

def motor_off(pin):
    print(f"Turning motor off GPIO {pin}")
    GPIO.output(pin, GPIO.HIGH)  # Relay is deactivated by HIGH signal

def motor_on(pin):
    print(f"Turning motor on GPIO {pin}")
    GPIO.output(pin, GPIO.LOW)  # Relay is triggered  by LOW signal




try:
    # Turn on all motors one by one, then turn them off in reverse order
    for pin in motor_pins:
        motor_on(pin)
        time.sleep(1)  # Wait 1 second between each motor turning on

    time.sleep(5)  # Keep all motors on for 5 seconds

    for pin in reversed(motor_pins):
        motor_off(pin)
        time.sleep(1)  # Wait 1 second between each motor turning off
    
    # motor_off(10)
    # time.sleep(5)

finally:
    GPIO.cleanup()  # Reset GPIO state

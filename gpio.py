import time
import threading

pinctl = open('/sys/class/gpio/export','wb', 0)
led_red = 28
led_blue = 38
swt_red = 30
swt_blue = 32

class GPIO:
    def __init__(self, pinnum, direction):
        self.pinnum = pinnum
        self.export()
        self.set_direction(direction)
        self.direction = direction

    def export(self):
        try:
            pinctl.write(str(self.pinnum).encode())
        except:
            pass

    def set_direction(self, direction):
        pinctldir = open('/sys/class/gpio/gpio%d/direction' % self.pinnum, 'wb', 0)
        try:
            pinctldir.write(direction.encode())
        except:
            pass

    def write_value(self, value):
        pin = open('/sys/class/gpio/gpio%d/value' % self.pinnum, 'wb', 0)
        try:
            pin.write(str(value).encode())
        except:
            pass

    def read_value(self):
        pin = open('/sys/class/gpio/gpio%d/value' % self.pinnum, 'rb', 0)
        data = None
        try:
            data = pin.read().decode().strip()
        except:
            pass
        return data

    def wait(self, timeout = 15):
        if self.direction == 'in':
            while timeout > 0:
                if self.read_value() == '0':
                    return
                time.sleep(0.1)
                timeout -= 0.1
        raise TimeoutError
        

    @staticmethod
    def wait_for(gpios, timeout = 15):
        while timeout > 0:
            for gpio in gpios:
                if gpio.read_value() == '0':
                    return gpio
            time.sleep(0.1)
            timeout -= 0.1
        raise TimeoutError

def start_blinking_routine(pinnum):
    def blink_led(pinnum):
        led = GPIO(pinnum, 'out')
        while True:
            led.write_value(1)
            time.sleep(1)
            led.write_value(0)
            time.sleep(1)

    threading.Thread(target=blink_led, args=(pinnum,) ).start()

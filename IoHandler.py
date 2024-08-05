# class to handle the IO for the demo setup
from machine import Pin, ADC
import neopixel
import time

class IoHandler:
    # create list of RGB tuples to control led states
    rgb_led_colours = [(0, 0, 0)] * 8

    # red led
    #led = Pin(28, Pin.OUT)
    led = Pin("LED", Pin.OUT)
    led_state = 0

    # FWD Sensor
    fwd = ADC(26)
    fwd_value = 0

    # REV sensor
    rev = ADC(27)
    rev_value = 0

    # output device pins
    output_one = Pin(16, Pin.OUT)
    output_two = Pin(17, Pin.OUT)
    output_three = Pin(18, Pin.OUT)
    device_states = [1, 0, 0]

    #input device pins
    linear = Pin(19 , Pin.IN)
    linear_trip = Pin(20 , Pin.IN)
    ant_a_b = Pin(21 , Pin.IN)

    def __init__(self):
        # get everything into a starting state
        self.__class__.show_red_led()
        self.__class__.get_fwd_reading()
        self.__class__.show_devices()
        self.__class__.get_linear()

    # output, setters and getters for coloured leds
    @classmethod
    def show_devices(cls):
        cls.output_one.value(cls.device_states[0])
        cls.output_two.value(cls.device_states[1])
        cls.output_three.value(cls.device_states[2])

    @classmethod
    def set_devices(cls, states):
        try:
            cls.set_output_one(states[0])
            cls.set_output_two(states[1])
            cls.set_output_three(states[2])
        except:
            pass
        cls.show_devices()

    @classmethod
    def set_output_one(cls, state):
        cls.device_states[0] = 0 if state == 0 else 1

    @classmethod
    def set_output_two(cls, state):
        cls.device_states[1] = 0 if state == 0 else 1

    @classmethod
    def set_output_three(cls, state):
        cls.device_states[2] = 0 if state == 0 else 1

    @classmethod
    def get_output_one(cls):
        return 0 if cls.device_states[0] == 0 else 1

    @classmethod
    def get_output_two(cls):
        return 0 if cls.device_states[1] == 0 else 1

    @classmethod
    def get_output_three(cls):
        return 0 if cls.device_states[2] == 0 else 1

    # red led handlers
    @classmethod
    def show_red_led(cls):
        cls.led.value(cls.led_state)

    @classmethod
    def toggle_red_led(cls):
        cls.led_state = 0 if cls.led_state == 1 else 1
        cls.show_red_led()

    # input pin 19 state handler
    @classmethod
    def get_linear(cls):
        return 0 if cls.linear.value () == 1 else 1

    # input pin 20 state handler
    @classmethod
    def get_linear_trip(cls):
        return 0 if cls.linear_trip.value () == 1 else 1

    # input pin 21 state handler
    @classmethod
    def get_ant(cls):
        return 0 if cls.ant_a_b.value () == 1 else 1

    # fwd power handler
    @classmethod
    def get_fwd_reading(cls):
        fwd_voltage = cls.fwd.read_u16() * (3.3 / 65536)
        #Convert AD8307 Log Amp output Voltage to dBW.
        #Slope = 25mV/dB (1V/40dB) and intercept point −84 dBm. 
        #Plus correct for attenuators, then convert dBWm to dBW.
        #Turn Cores 18T=25dB (20T=26dB); 127 Ohm + 22 Ohm V divider = 17dB.
        #-30dB to convert from dBn to dBW.
        #So, Revised intercept (0dB) pont = -84 +25 +17 -30 = 72.
        fwd_db =(40 *(fwd_voltage) - 72 -5 )
        # +0 is correction for Low Pwr detector op amp intercept point diff
        # -5 is correction for Hi Power detector op amp intercept point diff         
        cls.fwd_value = (fwd_db)
        return cls.fwd_value

    # rev handler
    @classmethod
    def get_rev_reading(cls):
        rev_voltage = cls.rev.read_u16() * (3.3 / 65536)
        rev_db =(40 *(rev_voltage) - 72 -5 )
        # +1.6 is correction for Low Pwr detector op amp intercept point diff
        # -5 is correction for Hi Power detector op amp intercept point diff 
        cls.rev_value = (rev_db)
        return cls.rev_value

    # rgb leds
    @classmethod
    def set_rgb_pixel(cls, pixel, colour):
        cls.rgb_led_colours[pixel] = colour

    @classmethod
    def set_rgb_leds(cls, rgb_red, rgb_green, rgb_blue):
        for n in range(4):
            cls.set_rgb_pixel(n, (rgb_red, rgb_green, rgb_blue))


# G3YSG web power and control panel
# uses multi core and multi tasking

import utime
from RequestParser import RequestParser
import json
import uasyncio
import _thread
from ResponseBuilder import ResponseBuilder
from WiFiConnection import WiFiConnection
from IoHandler import IoHandler
import random

# connect to WiFi
if not WiFiConnection.start_station_mode(True):
    raise RuntimeError('network connection failed')

async def handle_request(reader, writer):
    try:
        raw_request = await reader.read(2048)
        request = RequestParser(raw_request)
        response_builder = ResponseBuilder()
        # filter out api request
        if request.url_match("/api"):
            action = request.get_action()
            if action == 'readData':
                # ajax request for data
                fwd_value = IoHandler.get_fwd_reading()
                rev_value = IoHandler.get_rev_reading()
                # force higer value to always be displayed as forward power
                #comment this out for fwd/rev calibration work
                if fwd_value < rev_value :
                    temp_value = fwd_value
                    fwd_value = rev_value
                    rev_value = temp_value
                dev_states = {
                    'dev_one': IoHandler.get_output_one(),
                    'dev_two': IoHandler.get_output_two(),
                    'dev_three': IoHandler.get_output_three()
                }
                response_obj = {
                    'status': 0,
                    'fwd_value': fwd_value,
                    'rev_value': rev_value,
                    'dev_states': dev_states,
                    'rgb_leds': IoHandler.rgb_led_colours
                }
                response_builder.set_body_from_dict(response_obj)
            elif action == 'SetAction':
                # turn on requested output device
                # returns json object with states
                touch_action = request.data()['touched']
                status = 'OK'
                dev_states = {
                    'dev_one': IoHandler.device_states[0],
                    'dev_two': IoHandler.device_states[1],
                    'dev_three': IoHandler.device_states[2]
                    }        
                if touch_action == 'one':
                    dev_states['dev_one'] = 1
                    dev_states['dev_two'] = 0
                elif touch_action == 'two':
                    dev_states['dev_one'] = 0
                    dev_states['dev_two'] = 1
                elif touch_action == 'three':
                    #incase of trip, allow this selection to switch off device, then back on again
                    dev_states['dev_three'] = 0
                    IoHandler.set_devices([dev_states['dev_one'], dev_states['dev_two'], dev_states['dev_three']])
                    utime.sleep(0.25)
                    dev_states['dev_three'] = 1
                elif touch_action == 'four':
                    dev_states['dev_three'] = 0
                    pass
                else:
                    status = 'Error'
                IoHandler.set_devices([dev_states['dev_one'], dev_states['dev_two'], dev_states['dev_three']])
                response_obj = {
                    'status': status,
                    'dev_states': dev_states
                }
                response_builder.set_body_from_dict(response_obj)

            else:
                # unknown action
                response_builder.set_status(404)
        # try to serve static file
        else:
            response_builder.serve_static_file(request.url, "/api_index.html")

        response_builder.build_response()
        writer.write(response_builder.response)
        await writer.drain()
        await writer.wait_closed()

    except OSError as e:
        print('connection error ' + str(e.errno) + " " + str(e))

async def main():
    print('Setting up webserver...')
    server = uasyncio.start_server(handle_request, "0.0.0.0", 80)
    uasyncio.create_task(server)

    # main async loop on first core
    # just pulse the red led
    counter = 0
    while True:
        if counter % 2000 == 0:
            IoHandler.toggle_red_led()
        counter += 1
        await uasyncio.sleep(0)

# check input pin states and update
def show_input_state_leds():
    while True:  
        if IoHandler.get_ant () == 0:
            colour_1 = (128, 0, 0)
            colour_2 = (0, 128, 0)
        else:
            colour_1 = (0, 128, 0)
            colour_2 = (128, 0, 0)       
        
        if IoHandler.get_linear () == 0:
            colour_3 = (0, 128, 0)
            colour_4 = (0, 128, 0)
        else:
            colour_3 = (128, 0, 0)
            colour_4 = (128, 0, 0)
            
        if IoHandler.get_linear_trip () == 0:
            #do nothing
            colour_3 = (64, 64, 64)
    
        IoHandler.set_rgb_pixel(4, colour_1)
        IoHandler.set_rgb_pixel(5, colour_2)
        IoHandler.set_rgb_pixel(6, colour_3)
        IoHandler.set_rgb_pixel(7, colour_4)
        #IoHandler.show_rgb_leds()
        #if needed put in a brief delay.
        #utime.sleep(0.1)

# start neopixel scrolling loop on second processor
second_thread = _thread.start_new_thread(show_input_state_leds, ())

try:
    # start asyncio tasks on first core
    uasyncio.run(main())
finally:
    print("running finally block")
    uasyncio.new_event_loop()

from nicegui import ui, app
import random
from nicegui import ui, events
import time
import math
from collections import deque
import asyncio
from epicallypowerful.actuation.motor_data import *
from epicallypowerful.toolbox.robstride_setup import RobstrideConfigure


MAXLEN = 1000

charts = []
sliders = []
chart_time = deque(maxlen=MAXLEN)
chart_data = [deque(maxlen=MAXLEN) for _ in range(3)]
dropdown_options = ['Select An Actuator ID']
start_time = time.time()

actuator_type = 'RS02'

chart_timescale = {'value': 20}

rs_config_tool = RobstrideConfigure(max_can_id=127)
current_actuator_id = None


def select_actuator(event):
    global current_actuator_id
    if event.value == None or event.value == 'Select An Actuator ID':
        return
    current_actuator_id = int(event.value)
    print(f"Selected Actuator ID: {current_actuator_id}")
    update_act_type(actuator_type)

def update_act_type(value):
    actuator_type = value
    position_limits, velocity_limits, torque_limits, _, kp_limits, kd_limits, _ = get_motor_details(actuator_type)

async def update_dropdown_options():
    # Simulate updating dropdown options
    # Simulate delay
    scan_button.disable()
    dropdown.classes(add='hidden')
    loading_spinner.classes(remove='hidden')
    loading_label.classes(remove='hidden')

    new_options = rs_config_tool.scan()
    #await asyncio.sleep(2)  # Simulate a delay for scanning
    new_options = [str(opt) for opt in new_options]
    #new_options = [f'{random.randint(1, 6)}' for _ in range(5)]  # Simulated options for testing

    loading_spinner.classes(add='hidden')
    loading_label.classes(add='hidden')
    dropdown.classes(remove='hidden')
    dropdown.options = new_options
    dropdown.value = new_options[0]
    dropdown.update()
    scan_button.enable()
    con_button.enable()
    n = ui.notification(timeout=10)
    n.message = "Scan Complete"


def update_id(init_id, target_id):
    rs_config_tool.disable(init_id)
    result = rs_config_tool.change_id(init_id, target_id)
    dropdown.options = ['Select An Actuator ID']
    dropdown.value = dropdown.options[0]
    dropdown.update()
    current_actuator_id = None
    rs_config_tool.available_devices = set()
    n = ui.notification(timeout=20)
    n.message = "ID updated, press`Scan` to confirm"

def enable():
    n = ui.notification(timeout=5)
    n.message = "Motor Enabled"
    rs_config_tool.enable(current_actuator_id)

def disable():
    rs_config_tool.disable(current_actuator_id)
    n = ui.notification(timeout=5)
    n.message = "Motor Disabled"
# Header
ui.label('Robstride Actuator Setup').classes('text-h4 text-center w-full mb-4')

# Main layout
with ui.row().classes('w-full nowrap'):
    
    # Right side
    with ui.column().classes('grow').style('justify-content:center'):
        # Update button and dropdown
        ui.label('Select Actuator').classes('text-h6 text-center gap-1')
        with ui.row().classes('w-full items-center justify-between'):
            scan_button = ui.button('Scan ↺', on_click=update_dropdown_options).classes('w-small')
            dropdown = ui.select(dropdown_options, value=dropdown_options[0], on_change=select_actuator).classes('grow')
            loading_label = ui.label('Scanning for actuators...').classes('text-body1').classes('hidden')
            loading_spinner = ui.spinner(size='24px').classes('text-primary').classes('hidden')
        ui.toggle(['RS00', 'RS01', 'RS02', 'RS03', 'RS04', 'RS05', 'RS06', 'Cybergear'], value='RS02', on_change=lambda e: update_act_type(e.value)).style('text-align: center;')

        with ui.row().classes('w-full items-center justify-between'):
            con_button = ui.button('Enable', color='green', on_click=lambda e:enable() ).classes('basis-1/2')
            dis_button = ui.button('Disable', color='red', on_click=lambda e:disable() ).classes('basis-1/2')
        ui.separator()
        # Update CAN ID button
        with ui.row().classes('w-full items-center'):
            ui.label('Set CAN ID')
            new_id_input = ui.input('New ID', placeholder='Enter new ID', validation={'Not an integer': lambda x: x.isdigit(), 'Must be in range 1-127': lambda x: 1 <= int(x) <= 127})
            update_button = ui.button('Update', on_click=lambda event:update_id(current_actuator_id, int(new_id_input.value))).props('flat')

def main():
    update_act_type(actuator_type)  # Initialize sliders with default actuator type
    app.on_shutdown(lambda: print('Shutting down...'))
    #ui.run(title='Robstride Setup', dark=True, native=True, reload=False, window_size=(1280, 720))
    ui.run(title='Robstride Setup', dark=True, show_welcome_message=True, reload=False)


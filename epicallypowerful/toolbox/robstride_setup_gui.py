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

# rs_config_tool = RobstrideConfigure(max_can_id=127)
current_actuator_id = None


def select_actuator(event):
    current_actuator_id = int(event.value)
    print(f"Selected Actuator ID: {current_actuator_id}")
    update_act_type(actuator_type)

def update_act_type(value):
    actuator_type = value
    position_limits, velocity_limits, torque_limits, _, kp_limits, kd_limits, _ = get_motor_limits(actuator_type)
    sliders[0].props['min'] = torque_limits[0]
    sliders[0].props['max'] = torque_limits[1]
    sliders[1].props['min'] = velocity_limits[0]
    sliders[1].props['max'] = velocity_limits[1]
    sliders[2].props['min'] = position_limits[0]
    sliders[2].props['max'] = position_limits[1]
    sliders[3].props['min'] = kp_limits[0]
    sliders[3].props['max'] = kp_limits[1]
    sliders[4].props['min'] = kd_limits[0]
    sliders[4].props['max'] = kd_limits[1]
    for s in sliders:
        s.value = 0
        s.update()

async def update_dropdown_options():
    # Simulate updating dropdown options
    # Simulate delay
    scan_button.disable()
    dropdown.classes(add='hidden')
    loading_spinner.classes(remove='hidden')
    loading_label.classes(remove='hidden')

    # new_options = rs_config_tool.scan()
    await asyncio.sleep(2)  # Simulate a delay for scanning
    # new_options = [str(opt) for opt in new_options]
    new_options = [f'{random.randint(1, 6)}' for _ in range(5)]  # Simulated options for testing

    loading_spinner.classes(add='hidden')
    loading_label.classes(add='hidden')
    dropdown.classes(remove='hidden')
    dropdown.options = new_options
    dropdown.value = new_options[0]
    dropdown.update()
    scan_button.enable()

def update_charts():
    for i, chart in enumerate(charts):
        chart.push([time.time() - start_time], [[math.sin((time.time() - start_time) * (i + 1)) * 50 + 50]])

def update_echarts():
    for i, chart in enumerate(charts):
        chart_time.append(time.time() - start_time)
        chart_data[i].append((time.time() - start_time, math.sin((time.time() - start_time) * (i + 1)) * 50 + 50))
        chart.options['xAxis']['min'] = time.time() - start_time - chart_timescale['value']  # Show last 20 seconds
        chart.options['xAxis']['max'] = time.time() - start_time
        chart.options['series'][0]['data'] = list(chart_data[i])
        chart.update()

def reset_controls():
    for s in sliders:
        s.value = 0
        s.update()
# Header
ui.label('Robstride Actuator Setup').classes('text-h4 text-center w-full mb-4')

# Main layout
with ui.row().classes('w-full nowrap'):
    # Left - Charts
    with ui.column().classes('basis-1/2 grow-0').style('height: 90vh; overflow: auto;'):
        with ui.row().classes('w-full items-center mb-2 no-wrap'):
            ui.label('Chart Timescale').style('min-width: 150px;')
            ui.slider(min=1, max=60, value=20, step=1).style('width: 60%').bind_value(chart_timescale, 'value')
        ui.label("Torque").classes('text-h6')
        chart1 = ui.echart(options={
            'grid': {'left': 100, 'right': 20, 'top': 30, 'bottom': 30},
            'backgroundColor': 'black',
            'xAxis': {'type': 'value', 'axisLabel': {':formatter': 'value =>  value.toFixed(1) + "s"'}, 'splitLine': {'show':False}},
            'yAxis': {'type': 'value', 'axisLabel': {':formatter': 'value =>  value.toFixed(1) + "Nm"'}, 'splitLine': {'show':False}},
            'series': [{'type': 'line', 'data': [], 'showSymbol': False,'smooth': True, 'lineStyle': {'width': 2, 'color': '#00ff00'}}]
        }).style('width: 100%; height: 24%;')
        ui.label("Velocity").classes('text-h6')
        chart2 = ui.echart(options={
            'grid': {'left': 100, 'right': 20, 'top': 30, 'bottom': 30},
            'backgroundColor': 'black',
            'xAxis': {'type': 'value', 'axisLabel': {':formatter': 'value =>  value.toFixed(1) + "s"'}, 'splitLine': {'show':False}},
            'yAxis': {'type': 'value', 'axisLabel': {':formatter': 'value =>  value.toFixed(1) + "rad/s"'}, 'splitLine': {'show':False}},
            'series': [{'type': 'line', 'data': [], 'showSymbol': False,'smooth': True}]
        }).style('width: 100%; height: 24%;')
        ui.label("Position").classes('text-h6')
        chart3 = ui.echart(options={
            'grid': {'left': 100, 'right': 20, 'top': 30, 'bottom': 30},
            'backgroundColor': 'black',
            'xAxis': {'type': 'value', 'axisLabel': {':formatter': 'value =>  value.toFixed(1) + "s"'}, 'splitLine': {'show':False}},
            'yAxis': {'type': 'value', 'axisLabel': {':formatter': 'value =>  value.toFixed(1) + "rad"'}, 'splitLine': {'show':False}},
            'series': [{'type': 'line', 'data': [], 'showSymbol': False,'smooth': True}]
        }).style('width: 100%; height: 24%;')
        charts = [chart1, chart2, chart3]

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
            con_button = ui.button('Enable', color='grey', on_click=lambda: print(f'Connecting to {dropdown.value}')).classes('basis-1/2')
            ui.chip('Disabled For Motion', color='red').props('outline square')

         
        # Sliders section
        with ui.row().classes('w-full items-center no-wrap'):
            ui.label('Control Parameters').classes('text-h6')
            ui.button('Reset', on_click=reset_controls).classes('text-red-500').props('flat').style('margin-left: auto;')

        with ui.row().classes('w-full items-center no-wrap'):
            ui.label('Torque (Nm)').classes('text-body1 min-w-[150px]')
            s = ui.slider(min=0, max=100, value=0, step=0.1).props('label="Torque"')
            ui.label(0).bind_text(s, 'value').classes('text-body1 min-w-[30px]')
            sliders.append(s)
        with ui.row().classes('w-full items-center no-wrap'):
            ui.label('Velocity (rad/s)').classes('text-body1 min-w-[150px]')
            s = ui.slider(min=0, max=100, value=0, step=0.1).props('label="Velocity"')
            ui.label(0).bind_text(s, 'value').classes('text-body1 min-w-[30px]')
            sliders.append(s)
        with ui.row().classes('w-full items-center no-wrap'):
            ui.label('Position (rad)').classes('text-body1 min-w-[150px]')
            s = ui.slider(min=0, max=100, value=0, step=0.1).props('label="Position"')
            ui.label(0).bind_text(s, 'value').classes('text-body1 min-w-[30px]')
            sliders.append(s)
        with ui.row().classes('w-full items-center no-wrap'):
            ui.label('Kp (Nm/rad)').classes('text-body1 min-w-[150px]')
            s = ui.slider(min=0, max=100, value=0, step=0.1).props('label="Kp"')
            ui.label(0).bind_text(s, 'value').classes('text-body1 min-w-[30px]')
            sliders.append(s)
        with ui.row().classes('w-full items-center no-wrap'):
            ui.label('Kd (Nm/rad/s)').classes('text-body1 min-w-[150px]')
            s = ui.slider(min=0, max=100, value=0, step=0.1).props('label="Kd"')
            ui.label(0).bind_text(s, 'value').classes('text-body1 min-w-[30px]')
            sliders.append(s)

        with ui.row().classes('w-full items-center no-wrap'):
            ui.button('Send Command ⇒', on_click=lambda: print(f'Sending command to {dropdown.value}')).classes('basis-1/3 gap-1')
            ui.button('Set Zero Position', on_click=lambda: print(f'Setting zero position for {dropdown.value}')).classes('basis-1/3 gap-1')

        ui.separator()
        # Update CAN ID button
        with ui.row().classes('w-full items-center'):
            ui.label('Set CAN ID')
            new_id_input = ui.input('New ID', placeholder='Enter new ID', validation={'Not an integer': lambda x: x.isdigit(), 'Must be in range 1-127': lambda x: 1 <= int(x) <= 127})
            update_button = ui.button('Update', on_click=lambda: print(f'Updating CAN ID for {dropdown.value}')).props('flat')

    # Update charts periodically
ui.timer(0.1, update_echarts)

def main():
    update_act_type(actuator_type)  # Initialize sliders with default actuator type
    app.on_shutdown(lambda: print('Shutting down...'))
    ui.run(title='Robstride Setup', dark=True, native=True, reload=False, window_size=(1280, 720))

main()

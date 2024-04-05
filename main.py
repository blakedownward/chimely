import time
from taipy.gui import Gui, notify
from playsound import playsound

# set some constants for now - can make dynamic later
preset_intervals = {
    'hb1': ('1 minute', 60),
    'hb2': ('15 minutes', 900),
    'hb3': ('1 hour', 3600)
}

chime_path = 'assets//chime.mp3'
logo_path = 'assets//Chimely_logo.png'

# initialise state variables
custom_request = False
custom_int_mins = 5
selected_int = None
active = False

start_time = 0

hours = 0
minutes = 0
seconds = 0

display_time = f"{hours:02}:{minutes:02}:{seconds:02}"


def chime():
    playsound(chime_path)


# define local functions
def get_time_string(s) -> str:
    """Transform s seconds into HH:MM:SS format"""
    h = 0
    m = 0

    if s//60 < 1:  # if less than 1 minute
        s = s

    elif s//60 < 60:  # if less than 60 minutes
        m = s//60
        s = s % 60

    elif s//3600 < 100:  # if less than 100 hours (max digits for HH:MM:SS)
        h = s//60//60
        m = s//60 % 60
        s = s % 60
    else:
        s = s-360000  # minus 100 hours and start again from zero
        time_string = get_time_string(s)
        return time_string

    return f"{int(h):02}:{int(m):02}:{int(s):02}"


def start_timer(state, id):
    print("Hot button ID:", id)
    try:
        interval = preset_intervals[id][1]
    except KeyError:
        if id.startswith("custom_input"):
            interval = state.custom_int_mins * 60
            state.custom_request = False
        else:
            print("Key error!\nSetting interval to 5 minutes...")
            interval = 300

    state.active = True
    state.seconds = 0
    state.selected_int = interval
    chime()
    # success notification on start of the timer
    notify(state, 'success',
           f'Timer started and will chime every {int(state.selected_int//60)} minute/s until stopped.',
           duration=5000)

    state.start_time = time.time()
    lag = 0.05

    while state.active:

        time.sleep(1 - lag)
        state.seconds = time.time() - state.start_time
        lag = state.seconds % 1

        # print(f'Rounded state secs: {round(state.seconds)}')
        # print(f'Rounded state int: {state.selected_int}')

        if round(state.seconds) % state.selected_int == 0:
            notify(state, 'I',
                   f'Chimely Reminder: {int(state.selected_int // 60)} minute/s passed.',
                   duration=2500, system_notification=True)
            chime()
            print('interval reached')


def input_custom(state):
    state.custom_request = True


def stop_timer(state):
    notify(state, 'warning',
           f'Timer stopped.',
           duration=2500, system_notification=True)
    state.active = False


def on_change(state, var_name, var_value):
    if var_name == "seconds":
        state.seconds = var_value
        state.display_time = get_time_string(var_value)  # Changed to var_value from state.seconds to see what happens
    if var_name == "selected_int":
        state.selected_int = var_value
    if var_name == "active":
        state.active = var_value
    if var_name == "custom_int":
        state.custom_int = var_value


page_md = """
<|{logo_path}|image|id=header_logo|>

never lose time with chimely

<|part|class_name=ch-segment|
<|TIME ELAPSED|text|class_name=ch-seg-title|>

<|{display_time}|text|id=timer_display|>
|>

<|part|class_name=ch-segment|
<|CONTROLS|text|class_name=ch-seg-title|>

<|part|render={not custom_request and not active}|
<|{preset_intervals['hb1'][0]}|button|id=hb1|on_action=start_timer|>
<|{preset_intervals['hb2'][0]}|button|id=hb2|on_action=start_timer|>
<|{preset_intervals['hb3'][0]}|button|id=hb3|on_action=start_timer|>
<|custom interval|button|id=custom_int_btn|on_action=input_custom|>
|>
<|part|render={custom_request}|
<|{custom_int_mins}|number|id=custom_input|on_action=start_timer|>
<|start timer|button|id=custom_input_btn|on_action=start_timer|>
|>
<|part|render={active}|
<|STOP TIMER|button|id=stop_btn|on_action=stop_timer|>
|>
|>

<|part|class_name=ch-segment|
<|SUPPORT|text|class_name=ch-seg-title|>
  
Like this project?

Give it a &#11088; on GitHub to show your support :)

|>
"""


if __name__ == '__main__':
    gui = Gui(page=page_md)
    gui.run(use_reloader=False,
            dark_mode=False,
            title="Chimely",
            favicon="assets//chimely-favicon.png",
            notification_duration=1500)

# written on August 7, 2022
# python 3.8.10
# PySimpleGUI 4.60.3

# features:
# unix time as a reference, no second drift
# user settings
# local sqlite3 database
# statistics history

#wtf how did it get in here?
#from this import d
import time
from collections import deque
from tkinter.font import BOLD

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
#import sqlite3
#from sqlite3 import Error
from db_scripts import *
import calendar
import datetime
#from dateutil import rrule
import math
from playsound import playsound

matplotlib.use('TkAgg')
#import ptoaster #adds fading notification

#sg.UserSettings(filename='timekeeper_settings.json', path='.')

timekeeper_settings = sg.UserSettings(filename='timekeeper_settings.json', path='.')
#timekeeper_test_data = 'timekeeper_test_data.txt'
db_file = "timekeeper_db_real_data.db"
notification_sound = 'notification.mp3'

#timekeeper_settings.load()
timekeeper_settings_location = timekeeper_settings.get_filename()
#timekeeper_settings_location = sg.UserSettings.get_filename(timekeeper_settings)

#app.FindElementWithFocus()


#sg.theme('LightBlue3')
#sg.theme('DarkGrey2')

#sg.theme('DarkBrown')
#sg.theme('DarkBrown4')



#debug('time implementation:',time.get_clock_info('time').implementation, keep_on_top= False)
#debug('time.localtime(): {:02}:{:02}'.format(time.localtime().tm_hour, time.localtime().tm_min), keep_on_top= False)

#debug('timekeeper_settings location:', timekeeper_settings_location)
#debug('timekeeper_settings: ', timekeeper_settings)

if timekeeper_settings['-location-'] == None:
    #debug('-location- not found, setting to [0,0]')
    timekeeper_settings['-location-'] = [0,0]

if timekeeper_settings['-tasklist-'] == None:
    #debug('-tasklist- not found, setting to []')
    timekeeper_settings['-tasklist-'] = []

#reference to mutable object
task_list = timekeeper_settings['-tasklist-']


focus_time_slider_default_value = 60
default_focus_time = focus_time_slider_default_value
#timekeeper_settings['-default_focus_time-'] = default_focus_time


short_break_slider_default_value = 5
default_short_break = short_break_slider_default_value
#timekeeper_settings['-default_short_break-'] = default_short_break


long_break_slider_default_value = 20
default_long_break = long_break_slider_default_value
#timekeeper_settings['-default_long_break-'] = default_long_break


total_session_rounds_slider_default_value = 3

custom_timeout = 100

default_task = 'No task'
#timekeeper_settings['-default_task-'] = default_task
current_task = default_task

is_timer_running = False
is_timer_paused = False
is_timer_reset = False
is_timer_finished = False

progress_bar_limit = 1000
progress_bar_value = 0

#timekeeper_settings['-total_session_rounds_slider_default_value-'] = total_session_rounds_slider_default_value

current_session_round = 1
total_session_rounds = total_session_rounds_slider_default_value

round_state_order = deque([])
default_round_state = 'Focus time'
current_round_state = default_round_state

#reset_time = 0


if timekeeper_settings['-current_plot-'] == None:
    #debug('-current_plot- not found, setting to "Week"')
    timekeeper_settings['-current_plot-'] = 'Week'

current_plot = timekeeper_settings['-current_plot-']

total_focus_hours_this_week = 0
total_focus_hours_this_month = 0
total_focus_hours_this_year = 0
total_focus_hours_all_time = 0

icon_icon = b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAD90lEQVR4nO2aX2iOURzHz7sZYRK1uaCUC2n+FfmTPy02RWuSldlciKWEO3I5LrULW8m/iJErF3Kh0ZK/F4gNkRRRM2wK4cLm30en92y9O87z/nnec57neef91Gr1Pn1/v/N9n/c85znnK0SePNYBZgI7gWPAdeAV8An4qf7k/13ADeCkunY2UCByFWABcAh4j396lMYSkQsABcB6oAP7PADqIntXAMuAR7jnIbBCRAVgLHAC+JOk6T6gHdgHrAXKgFIgpjTGATOAVcBe4ALwJYURsmZx2IOfBTxL0uRNoN5Po8AooAq4CPzy0H8pJ0s3o0sBUAF89WjsipwEhSWAacA54LehluyhylattFATnbytdd7KW1w4AlgIPDXU/QHUuKo7BKAS6Dc0cQmYIByjfhqHPUyodl18rsdt3xT04wnYZpgbvgFzXBUsBp4bBt/opGB6PdWqlWQir4HxLoqdNgy+xXohf3eCTqvtIuWG53wbUCgiAHDQYMJqW+KFwBNNvBeYJCICMBLo1Hp8auULAjYa3K0VEUNN0PqkuDVb0RjwWBO9NbCEjRrAUcNdEMv2BUfHyouILmpJc7JhjVKRjeBxTazDRqOuDFC6rZr0qWwmv4+a2I4cMEA+sRKRYyjyIzRfE5ILjtIcMEBuynRr8pnvKAG7NZH7tpp0aYDHz2CPH5GzmkhzDhnQoMmf9yNyTxPZkkMGLNLkO/2IfNBEynPIgIma/Gc/It81kelBGqC2w/TJzAVvgDV68RGGC6e6NADYoH0uGwuKLr25IsNFUywb0G14zA6aQMCk8xMos2xAjeHlZdAEAsbUYK92zXKbBqga9V4mpGww+9opDbirXdNguwlVp87DhNANOONyIZSGCYGSzlK4w5UBCRsv/3zzQWFqaJ52jTyVKQlhlzc0AwoMr8O7XBoQpgnpboh0ujZA1Q3/KSABlhrMqhQBEBUDYoZN0du2m/HdoI8FU6b6Qv0mdTY5GHPSgYVpQKHhYKTH5vZYOgMLzYCE7XH9aOyay6OxSBkgUfm9wA5HM27QtT7xMJQpD7TfdnO+GgxCn3goypTearEdkIikARJgpUc+qM3mUtmrQbIklX5aAOuShKRqhr0BEnlImiTM2J5tvjfyBkhU4tMUW0sMSm6WSVAxHA2QAGPUubwpxDhAn4rJN6qMoZxMS1TkbbTccJXpLvVZk4rN22nQA+v6wGKV6HaClVEP7de+PvGXp2rgzn9pgGFHqdnW6U6CrhMd4RLiUfjtwBHgKvBC7Tb1q/OHd2qVeRk4oLbLh48BfsgboOFlTKakMjgyuG4wb4Bjg6036BoRNcgbQHgBiSggYysBpUS6rEXr84jc5y8HbiVaLf9ejwAAAABJRU5ErkJggg=='

start_base64_icon = b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAABFElEQVRoge3XIU4DURQF0EJC8DhI2ABhCRgWgGQLWCRbYA1INMGwBlgCBonAUkcQHATTZFrmM/0I3vzwjpxOk3ub9vbPbJZSSimlhuEO+9E5fs2XV5xjMzpPNcvucRCdqYrv3nGJ7ehsaxkosPCE4+h8o34oAB+4xk50zqKRAgsvOI3OOmgg7FX3yQ+5xV505iWrCbtrR3gslJjW5A4V6K5v4QJvhSLTmNxSgd7rh3golIif3LEC3T0bOMO8UCRuctcp0Lt3FzeFEjGTW1Og954TPBeKVE3uNJYg0r/4Cmn5R6zVGdXyH5mWjxJaP8wVNHWc7mv6gabZR8r4aayxEn4a01ijCz6taaxhitOYUkoppT/yCVXxEV1PYBYkAAAAAElFTkSuQmCC'
pause_base64_icon = b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAAAUUlEQVRoge3PsQqAMBAFwcT//+fYWwSCxQrO1HcPdgwAoDNPH9Zaazs453bz7f/TdXL8RQJqAmoCagJqAmoCagJqAmoCagJqAmoCagIAgD+7AbpgCDi7dLGGAAAAAElFTkSuQmCC'
reset_base64_icon = b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAABhElEQVRoge2YIVLGMBCF38IwGAbNDBcBgcTiwOL474DgHIBCYpAMAvcLOACCCzDDFRgED0E6QEm2aZp0EfvZttn9mr5pEsBxHMcSKX2Q5D6AOwCr9dpJIyLRXlcmDHgP4Ky4o0qoM0ByAYAicpm4LgCuARw16O0XqRlIQnKX5BvJd5J7yn0bJJ/YmLHNb5F8+fH8K8ntUYNMpFiA5BrJZeQlPJJcb9hzv49igQtlJq8a9tzvY7wAyYX6IX5x0rj3rpdxAvwO7RBqqE0E+De0QzQPdbYA06EdommoxwhooR2iWahzBZJ/t/5Do/+EE8mtX7wW+i+4gDUuYI0LWOMC1riANeYCqcVk5L4Y59rAWavBCgKly/kHasv5uQRCrfobqjkFQr0d1tzSzi0Qah5nCOQdKlgIhLraDjEd2shAVgKpUOuhjQxkIhBqTz/a1D/DKjyT3FTqd6FWQ5u9qW/EDYBDEYnWYghs6nhfZYYZ6Did8gasZwAAPgAciMjtTPUcx3Eq8gkSmw1oZCAvqQAAAABJRU5ErkJggg=='
reset_session_base64_icon = b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/wD/AP+gvaeTAAABhElEQVRoge2YIVLGMBCF38IwGAbNDBcBgcTiwOL474DgHIBCYpAMAvcLOACCCzDDFRgED0E6QEm2aZp0EfvZttn9mr5pEsBxHMcSKX2Q5D6AOwCr9dpJIyLRXlcmDHgP4Ky4o0qoM0ByAYAicpm4LgCuARw16O0XqRlIQnKX5BvJd5J7yn0bJJ/YmLHNb5F8+fH8K8ntUYNMpFiA5BrJZeQlPJJcb9hzv49igQtlJq8a9tzvY7wAyYX6IX5x0rj3rpdxAvwO7RBqqE0E+De0QzQPdbYA06EdommoxwhooR2iWahzBZJ/t/5Do/+EE8mtX7wW+i+4gDUuYI0LWOMC1riANeYCqcVk5L4Y59rAWavBCgKly/kHasv5uQRCrfobqjkFQr0d1tzSzi0Qah5nCOQdKlgIhLraDjEd2shAVgKpUOuhjQxkIhBqTz/a1D/DKjyT3FTqd6FWQ5u9qW/EDYBDEYnWYghs6nhfZYYZ6Did8gasZwAAPgAciMjtTPUcx3Eq8gkSmw1oZCAvqQAAAABJRU5ErkJggg=='
#reset_session_base64_icon = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAoklEQVRIie3UMQoCMRCF4UUQryB4ES28ztrucbQRwZtY6EUEryA2n5WyxDXuJltJXjkk82fCvFdVRTlCI0GxhhvUQW0/CgAr3PHAOnHibgDmuLYeccNiFACmOHVMesFsDMAu8p2HbMCgAwmASWqzviqAPwC017xVe2kbHh68phGjnj+MmuoDfaMmx2hY+hWWkcj4pmNwvxbEfS4AmpSJi956Av775GD6kS+fAAAAAElFTkSuQmCC'
graph_base64_icon = b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAA3UlEQVRIie3UzUrDQBSG4Ym7KqIVpf7QRfHe7KZeoSC4EbF1oQtFF6XqhTxuTjWENHVsQAr9VjMnZ973TAJJaZOciLTJ3GoTtt4CHGC4rKnxG6CDzgL4Qxy//JMA27jCDXZL9S7GcfQNZ9kC7ODaT+5j6i4mUXtthC8SYA+38egds1hP8BTrZxw3wusE2MddlGc4Rz+mnecFJ0vhVUHl3U4xKPX18JgFrxEMSxOe1vQe4ujX8Kog9iP0siA5gjayPr+KfxMU5Q0+Ukr9laFF8c2t3uAipfS5qmCTrHwB/TtBja7+dEUAAAAASUVORK5CYII='

timer =  sg.Frame('Timer', [[sg.Text(key = '-localtime-', font=('Helvetica', 12))],
        [sg.Text(text=current_task, key='-current_task-', font=('Helvetica', 20))],
        [sg.Text('', key='-timer-', font=('Helvetica', 48))],

        [sg.Text(key = '-current_state-', font=('Helvetica', 24))],

        [sg.ProgressBar(progress_bar_limit, orientation='h', size=(20,20), key='-progressbar-', border_width=3)],

        [sg.Button(image_data = start_base64_icon, key = '-start/pause-', metadata='start', focus = True),
        #sg.Button(image_data = reset_base64_icon, metadata='reset', key = '-reset_timer-'),
        #sg.Push(),
        sg.Text(text = '{}/{}'.format(current_session_round, total_session_rounds), key = '-round_info-', font=('Helvetica', 24)),
        sg.Button(image_data = reset_session_base64_icon, key='-reset_session-')]], font=('Helvetica', 12), relief='solid', element_justification='c')

task_listbox = sg.Frame('Task list', [[sg.Listbox(values=[l for l in task_list], key='-task_listbox-', enable_events=True, size=(20,10), font=('Helvetica', 12))],
                    [sg.Button('Add', key='-add_task-', font=('Helvetica', 12, 'bold')), sg.Button('Delete', key='-delete_task-', font=('Helvetica', 12, 'bold'))],
                    [sg.Input(size=(22), key='-task_to_add-', font=('Helvetica', 12), enable_events=True)]], font=('Helvetica', 12), relief='solid')

stat_history = ['Week', 'Month', 'Year']

#sg.Button(image_data=graph_base64_icon, key='-py_plot-')
stat_numbers_and_combo = sg.Column([[sg.Text('Plot:', font=('Helvetica', 12)), sg.Push(), sg.Combo(stat_history, enable_events = True, font=('Helvetica'), readonly=True, default_value = current_plot, key='-stat_history_combo-')], 
                
                [sg.Text('Week:', font=('Helvetica', 12)), sg.Push(), sg.Text('0', key='-stat_week-', font=('Helvetica', 12, 'bold'))],
                [sg.Text('Month:', font=('Helvetica', 12)), sg.Push(), sg.Text('0', key='-stat_month-', font=('Helvetica', 12, 'bold'))],
                [sg.Text('Year:', font=('Helvetica', 12)), sg.Push(), sg.Text('0', key='-stat_year-', font=('Helvetica', 12, 'bold'))],
                [sg.Text('Total:', font=('Helvetica', 12)), sg.Push(), sg.Text('0', key='-stat_total-', font=('Helvetica', 12, 'bold'))]])

#stat_history_tabs =  sg.TabGroup([[sg.Tab('Tab1', [[]], key='-tab1-')], [sg.Tab('Tab2', [[]])]])
#[sg.Text('tabs')]
canvas = sg.Column([[sg.Canvas(key='-CANVAS-')]])

stats = sg.Frame('Statistics',[[sg.vtop(stat_numbers_and_combo), canvas]], font=('Helvetica', 12), relief='solid')

settings = sg.Frame('Settings', [[sg.Text('Focus time', font=('Helvetica', 12)), sg.Push(), sg.Text('0', key='-focus_time_settings-',  font=('Helvetica', 12, 'bold')), sg.Text('min', font=('Helvetica', 12))],
            [sg.Slider(key='-focus_time_slider-', range=(5, 120), resolution = 5, default_value = focus_time_slider_default_value, orientation='h', size=(20,15), enable_events=True, disable_number_display=True)],
            
            [sg.Text('Short break', font=('Helvetica', 12)), sg.Push(), sg.Text('0', key='-short_break_settings-', font=('Helvetica', 12, 'bold')), sg.Text('min', font=('Helvetica', 12))],
            [sg.Slider(key='-short_break_slider-', range=(1, 10), default_value = short_break_slider_default_value, orientation='h', size=(20,15), enable_events=True, disable_number_display=True) ],
            [sg.Text('Long break', font=('Helvetica', 12)), sg.Push(), sg.Text('0', key='-long_break_settings-', font=('Helvetica', 12, 'bold')), sg.Text('min', font=('Helvetica', 12))],
            [sg.Slider(key='-long_break_slider-', range=(0, 60), resolution = 5, default_value = long_break_slider_default_value, orientation='h', size=(20,15), enable_events=True, disable_number_display=True)],
            
            [sg.Text('Session rounds', font=('Helvetica', 12)), sg.Push(), sg.Text('0', key='-total_session_rounds_settings-', font=('Helvetica', 12, 'bold')), sg.Text('rounds', font=('Helvetica', 12))],
            [sg.Slider(key='-total_session_rounds_slider-', range=(1, 10), default_value = total_session_rounds_slider_default_value, orientation='h', size=(20,15), enable_events=True, disable_number_display=True)],
            [sg.Button('Default settings', key='-reset_settings-', font=('Helvetica', 12, 'bold'))]], font=('Helvetica', 12), relief='solid', size=(230,250))

timekeeper_layout = [[task_listbox, timer, settings],
                    [stats]]
#sg.Window("hello!", icon='Images/logo.ico')
app = sg.Window(
    'Timekeeper', timekeeper_layout, icon=icon_icon, finalize = True, enable_close_attempted_event=True,
    #location=sg.user_settings_get_entry('-location-', (None, None)),
    location = timekeeper_settings['-location-'],
    right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT,
    element_justification='c')

#from my stackoverflow question https://stackoverflow.com/q/73248474/8186223
app.bring_to_front()

#element = app['-stat_history_combo-']
#element.widget.select_range(0, sg.tk.END)     # After window finalized

# Set colors of foreground and background in entry field of Combo element.
style = sg.ttk.Style()
style_name = app['-stat_history_combo-'].widget.configure()['style'][-1]
style.configure(style_name, selectforeground=sg.theme_input_text_color())
style.configure(style_name, selectbackground=sg.theme_input_background_color())


#listboxfocus = app['-task_listbox-'].widget.configure()['style'][-1]
#style.configure(listboxfocus, focuscolor='#FFFFFF')
#app['-task_listbox-'].Widget.config(focus_color='#000000')

#app['-tab1-']
#style.configure(app['-tab1-'], focuscolor=style.configure(".")["background"])

app['-current_task-'].update(default_task)
app['-current_state-'].update(current_round_state)





#sin function
#fig = matplotlib.figure.Figure(figsize=(10, 3), dpi=50)
#t = np.arange(0, 3, 0.1)
#fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
###########################################################
def PyplotGGPlotSytleSheet(data_range, values, labels):
    #import numpy as np
    #import matplotlib.pyplot as plt
    #from matplotlib.pyplot import figure
    #figure(figsize=(1, 1), dpi=80)
    #plt.ion()
    plt.style.use('ggplot')
    plt.rcParams["figure.figsize"] = (5.48,2)
    #plt.tight_layout()
    #plt.savefig(bbox_inches='tight')
    # Fixing random state for reproducibility
    #np.random.seed(19680801)

    fig, axes = plt.subplots()
    plt.subplots_adjust(left=0.09, right=1, top=0.98, bottom=0.13)

    #ax3 = axes

    # bar graphs
    x = np.arange(data_range)
    #y1 = np.random.randint(1, 25, size=(2, 5))
    y1 = values
    ##debug(type(y1))
    width = 0.5
    #list(plt.rcParams['axes.prop_cycle'])[2]['color']
    axes.yaxis.get_major_locator().set_params(integer=True)
    axes.bar(x + width, y1, width, color='DarkGrey')
    #axes.bar(x + width, y2, width,
    #        color=list(plt.rcParams['axes.prop_cycle'])[2]['color'])
    
    axes.set_xticks(x + width)
    #axes.set_xticklabels(['a', 'b', 'c', 'd', 'e'])
    axes.set_xticklabels(labels)
    #fig = plt.gcf().set_dpi(300)
    fig = plt.gcf()  # get the figure to show
    #fig = plt.figure(dpi=100)

    return fig

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def delete_figure_agg(fig_canvas_agg):
    fig_canvas_agg.get_tk_widget().forget()
    plt.close('all')

def draw_plot():
            #plt.plot([0.1, 0.2, 0.5, 0.7])
            a = plt.show(block=False)
            #plt.close()
            #plt.close('all')
            ##debug(a)

def plot_current_year():
    #debug('----------def plot_current_year START----------')
    sql_month_end_date = datetime.date.today()
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month
    #debug('current month:', current_month)

    sql_month_start_date = datetime.date(current_year, 1, 1)
    
    #debug('sql_month_start_date:', sql_month_start_date)
    #debug('sql_month_end_date:', sql_month_end_date)

    conn = create_connection(db_file)

    test_start = datetime.date.fromisoformat('2023-01-01')
    test_end = datetime.date.fromisoformat('2023-01-05')
    rows = select_date_range(conn, sql_month_start_date, sql_month_end_date)
    #rows = ()
    #type(rows) is tuple
    #debug('sql RAW rows (tuple):')
    #for row in rows:
        #debug(row)

    ##debug('sql rows: e.g. January is 1')
    date_dict={}
    month_number = 0
    total_focus_time = {}

    #date_dict shows total minutes for each month
    # being a key: e.g. January is 1
    for row in rows:
        
        #if have the same month, add focus time
        if datetime.date.fromisoformat(row[1]).month == month_number:
            #row[2] is focus_time in minutes
            total_focus_time[datetime.date.fromisoformat(row[1]).month] += int(row[2])
        else:
            total_focus_time[datetime.date.fromisoformat(row[1]).month] = int(row[2])
        
        #last_date is 12
        month_number = datetime.date.fromisoformat(row[1]).month
        
        ##debug('date_dict[month]:', datetime.date.fromisoformat(row[1]).month)
    
        date_dict[datetime.date.fromisoformat(row[1]).month] = round((total_focus_time[datetime.date.fromisoformat(row[1]).month] / 60), 2)
    
    #debug("total_focus_time:", total_focus_time)
    #global total_focus_hours_this_year
    #total_focus_hours_this_year = total_focus_time / 60

    month_number = 0
    total_focus_time = 0

    
    #debug('date_dict[month] Jan is 1:', date_dict)

    data_range = 12
    #data_values = [0,0,0,0,0,0,0]
    data_values=[]
    data_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    #make list of dict values which has some keys with the rest being zeros
    #fill in empty weekdays
    for i in range(1,data_range+1):
        if i not in date_dict:
            data_values.append(0)
        else:
            data_values.append(date_dict[i])

    #debug('pyplot data_values:', data_values)

    fig = PyplotGGPlotSytleSheet(data_range, data_values, data_labels)
    fig_canvas_agg = draw_figure(app['-CANVAS-'].TKCanvas, fig)

    #debug('----------def plot_current_year FINISH----------')

    return fig_canvas_agg


#plot_current_year()

def plot_current_month():
    #debug('----------def plot_current_month START----------')
    sql_month_end_date = datetime.date.today()
    #sql_month_end_date = datetime.date.fromisoformat('2022-09-30')
    current_month_date = datetime.date.today().day
    current_month = datetime.date.today().month

    if sql_month_end_date == 1:
        sql_month_start_date = sql_month_end_date
    else:
        date_delta = datetime.timedelta(days = (current_month_date - 1))
        sql_month_start_date = sql_month_end_date - date_delta

    #debug('sql_month_start_date:', sql_month_start_date)
    #debug('sql_month_end_date:', sql_month_end_date)

    # for dt in rrule.rrule(rrule.DAILY, dtstart=sql_month_start_date, until=sql_month_end_date):
    #     d_truncated = datetime.date(dt.year, dt.month, dt.day)
    #     #debug(d_truncated)

    conn = create_connection(db_file)

    test_start = datetime.date.fromisoformat('2023-01-01')
    test_end = datetime.date.fromisoformat('2023-01-05')
    rows = select_date_range(conn, sql_month_start_date, sql_month_end_date)
    #rows = ()
    #type(rows) is tuple
    #debug('sql RAW rows (tuple):')
    #for row in rows:
        #debug(row)

    ##debug('sql rows: e.g. 1 is 0')
    date_dict={}
    last_date = ''
    total_focus_time = 0

    #date_dict shows total minutes for each weekday
    # being a key: e.g. Monday is 0
    for row in rows:

        #if have the same date, add focus time
        if row[1] == last_date:
            #row[2] is focus_time in minutes
            total_focus_time += int(row[2])
        else:
            total_focus_time = int(row[2])
        
        #last_date is '2022-12-31'
        last_date = row[1]
        
        ##debug("FOCUS TIMEEEEEE", total_focus_time)
        ##debug('date_dict[day-1]:', datetime.date.fromisoformat(last_date).weekday())
        date_dict[datetime.date.fromisoformat(last_date).day-1] = round((total_focus_time / 60), 2)

    #global total_focus_hours_this_month
    #total_focus_hours_this_month = total_focus_time / 60
    
    last_date = ''
    total_focus_time = 0

    #debug('date_dict [day-1] 1 is 0:', date_dict)
    ##debug('month range:', calendar.monthrange(2022, 2)[1])
    number_of_days_in_month = calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1]
    #debug('month range:', number_of_days_in_month)
    data_range = number_of_days_in_month
    #data_values = [0,0,0,0,0,0,0]
    data_values=[]
    #c = calendar.Calendar()
    #for d in [x for x in c.itermonthdates(datetime.date.today().year,  datetime.date.today().month) if x.month ==  datetime.date.today().month]:
    #    #debug('d:', d)
    data_labels = []
    for a in range(1,number_of_days_in_month+1):
        if a % 2 == 0:
            data_labels.append('')
        else:    
            data_labels.append(a)
    #data_labels = ['Mon','Tue','Wen','Thu','Fri','Sat', 'Sun']
    #data_range = 7
    #make list of dict values which has some keys with the rest being zeros
    #fill in empty weekdays
    for i in range(0,data_range):
        if i not in date_dict:
            data_values.append(0)
        else:
            data_values.append(date_dict[i])

    #debug('pyplot data_values:', data_values)


    fig = PyplotGGPlotSytleSheet(data_range, data_values, data_labels)
    fig_canvas_agg = draw_figure(app['-CANVAS-'].TKCanvas, fig)
    
    #debug('----------def plot_current_month FINISH----------')

    return fig_canvas_agg

#plot_current_month()

def plot_current_week():
    #debug('----------def plot_current_week START----------')

    sql_week_end_date = datetime.date.today()
    #sql_end_date = datetime.date.fromisoformat('2023-01-01')

    today_weekday = datetime.datetime.today().weekday()
    #today_month = datetime.datetime.today().month()
    ##debug('today_month:', today_month)

    if today_weekday == 0:
        sql_week_start_date = sql_week_end_date
    else:
        date_delta = datetime.timedelta(days = today_weekday)
        sql_week_start_date = sql_week_end_date - date_delta

    #<class 'datetime.date'>
    #debug('sql_week_start_date:', sql_week_start_date)
    #debug('sql_week_end_date:', sql_week_end_date)
    
    ##debug('date_start:', type(date_start))
    ##debug(datetime.date.today())
    #for dt in rrule.rrule(rrule.DAILY, dtstart=sql_start_date, until=sql_end_date):
    #    d_truncated = datetime.date(dt.year, dt.month, dt.day)
    #    #debug(d_truncated)

    conn = create_connection(db_file)

    test_start = datetime.date.fromisoformat('2023-01-01')
    test_end = datetime.date.fromisoformat('2023-01-05')
    rows = select_date_range(conn, sql_week_start_date, sql_week_end_date)
    #rows = ()
    #type(rows) is tuple
    #debug('sql RAW rows (tuple):')
    total_focus_time = 0
    for row in rows:
        #debug(row)
        total_focus_time += int(row[2])
        #global total_focus_hours_this_week
        #total_focus_hours_this_week = total_focus_time / 60
    
    ##debug('sql rows: e.g. Monday is 0:')
    date_dict={}
    last_date = ''
    total_focus_time = 0

    #date_dict shows total minutes for each weekday
    # being a key: e.g. Monday is 0
    for row in rows:

        #if have the same date, add focus time
        if row[1] == last_date:
            #row[2] is focus_time in minutes
            total_focus_time += int(row[2])
        else:
            total_focus_time = int(row[2])
        
        #last_date is '2022-12-31'
        last_date = row[1]
        
        #debug('date_dict[weekday]:', datetime.date.fromisoformat(last_date).weekday())
        date_dict[datetime.date.fromisoformat(last_date).weekday()] = round((total_focus_time/60), 2)

    last_date = ''
    total_focus_time = 0

    #debug('date_dict [weekday] Mon is 0:', date_dict)

    data_range = 7
    #data_values = [0,0,0,0,0,0,0]
    data_values=[]
    data_labels = ['Mon','Tue','Wen','Thu','Fri','Sat', 'Sun']

    #make list of dict values which has some keys with the rest being zeros
    #fill in empty weekdays
    for i in range(0,data_range):
        if i not in date_dict:
            data_values.append(0)
        else:
            data_values.append(date_dict[i])

    #debug('pyplot data_values:', data_values)


    fig = PyplotGGPlotSytleSheet(data_range, data_values, data_labels)
    fig_canvas_agg = draw_figure(app['-CANVAS-'].TKCanvas, fig)

    #debug('----------def plot_current_week FINISH----------')

    return fig_canvas_agg

def get_focus_time_year():
    #debug('----------def get_focus_time_year START----------')
    sql_month_end_date = datetime.date.today()
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month
    ##debug('current month:', current_month)

    sql_month_start_date = datetime.date(current_year, 1, 1)
    
    ##debug('sql_month_start_date:', sql_month_start_date)
    ##debug('sql_month_end_date:', sql_month_end_date)

    conn = create_connection(db_file)

    test_start = datetime.date.fromisoformat('2023-01-01')
    test_end = datetime.date.fromisoformat('2023-01-05')
    rows = select_date_range(conn, sql_month_start_date, sql_month_end_date)
    #rows = ()
    #type(rows) is tuple
    ##debug('sql RAW rows (tuple):')
    total = 0
    for row in rows:
        ##debug(int(row[2]))
        total += int(row[2])

    #total = total / 60
    #debug('total:', total)
    #debug('----------def get_focus_time_year FINISH----------')

    return total

def get_focus_time_month():
    #debug('----------def get_focus_time_month START----------')
    sql_month_end_date = datetime.date.today()
    #sql_month_end_date = datetime.date.fromisoformat('2022-09-30')
    current_month_date = datetime.date.today().day
    current_month = datetime.date.today().month

    if sql_month_end_date == 1:
        sql_month_start_date = sql_month_end_date
    else:
        date_delta = datetime.timedelta(days = (current_month_date - 1))
        sql_month_start_date = sql_month_end_date - date_delta

    ##debug('sql_month_start_date:', sql_month_start_date)
    ##debug('sql_month_end_date:', sql_month_end_date)

    # for dt in rrule.rrule(rrule.DAILY, dtstart=sql_month_start_date, until=sql_month_end_date):
    #     d_truncated = datetime.date(dt.year, dt.month, dt.day)
    #     #debug(d_truncated)

    conn = create_connection(db_file)

    test_start = datetime.date.fromisoformat('2023-01-01')
    test_end = datetime.date.fromisoformat('2023-01-05')
    rows = select_date_range(conn, sql_month_start_date, sql_month_end_date)
    #rows = ()
    #type(rows) is tuple
    ##debug('sql RAW rows:')
    total = 0
    for row in rows:
        ##debug(row)
        total += int(row[2])
    #total = total / 60
    #debug('total:', total)
    #debug('----------def get_focus_time_month FINISH----------')
    return total

def get_focus_time_week():
    #debug('----------def get_focus_time_week START----------')
    sql_week_end_date = datetime.date.today()
    #sql_end_date = datetime.date.fromisoformat('2023-01-01')

    today_weekday = datetime.datetime.today().weekday()
    #today_month = datetime.datetime.today().month()
    ##debug('today_month:', today_month)

    if today_weekday == 0:
        sql_week_start_date = sql_week_end_date
    else:
        date_delta = datetime.timedelta(days = today_weekday)
        sql_week_start_date = sql_week_end_date - date_delta

    #<class 'datetime.date'>
    ##debug('sql_week_start_date:', sql_week_start_date)
    ##debug('sql_week_end_date:', sql_week_end_date)
    
    ##debug('date_start:', type(date_start))
    ##debug(datetime.date.today())
    #for dt in rrule.rrule(rrule.DAILY, dtstart=sql_start_date, until=sql_end_date):
    #    d_truncated = datetime.date(dt.year, dt.month, dt.day)
    #    #debug(d_truncated)

    conn = create_connection(db_file)

    test_start = datetime.date.fromisoformat('2023-01-01')
    test_end = datetime.date.fromisoformat('2023-01-05')
    rows = select_date_range(conn, sql_week_start_date, sql_week_end_date)
    #rows = ()
    #type(rows) is tuple
    ##debug('sql RAW rows:')
    total = 0
    for row in rows:
        ##debug(row)
        total += int(row[2])
        #global total_focus_hours_this_week
        #total_focus_hours_this_week = total_focus_time / 60
    #total = total / 60
    #debug('total:', total)
    #debug('----------def get_focus_time_week FINISH----------')
    return total

def get_focus_time_all_time():
    #debug('----------def get_focus_time_all_time START----------')
    conn = create_connection(db_file)
    rows = select_all_for_total(conn)
    total = 0
    for row in rows:
        ##debug(row)
        total += int(row[2])
        #global total_focus_hours_this_week
        #total_focus_hours_this_week = total_focus_time / 60
    
    #total = total / 60
    #debug('total:', total)
    #debug('----------def get_focus_time_all_time FINISH----------')
    return total

def update_plots():
    if current_plot == 'Week':
        fig_canvas_agg = plot_current_week()
        return fig_canvas_agg
    elif current_plot == 'Month':
        fig_canvas_agg = plot_current_month()
        return fig_canvas_agg
    elif current_plot == 'Year':
        fig_canvas_agg = plot_current_year()
        return fig_canvas_agg

def min_to_hr_min(total):
    h = math.trunc(total / 60)
    m = total - (h * 60)
    total_str = '{} hr {} min'.format(h,m)
    return total_str

def update_totals():
    total_focus_min_this_week = get_focus_time_week()
    total_focus_min_this_month = get_focus_time_month()
    total_focus_min_this_year = get_focus_time_year()
    total_focus_min_all_time = get_focus_time_all_time()

    t_w = min_to_hr_min(total_focus_min_this_week)
    t_m = min_to_hr_min(total_focus_min_this_month)
    t_y = min_to_hr_min(total_focus_min_this_year)
    t_a = min_to_hr_min(total_focus_min_all_time)

    
    app['-stat_week-'].update(t_w)
    app['-stat_month-'].update(t_m)
    app['-stat_year-'].update(t_y)
    app['-stat_total-'].update(t_a)

conn = create_connection(db_file)
create_table_tasks(conn)

fig_canvas_agg = update_plots()
update_totals()

#delete_figure_agg(fig_canvas_agg)

#fig = matplotlib.figure.Figure(figsize=(5, 2), dpi=50)
#t = np.arange(0, 4, 1)
#fig.add_subplot(111).plot(t, 5*t)

#def draw_plot():
    #plt.plot([0.1, 0.2, 0.5, 0.7])
    #plt.show(block=False)
#draw_plot()

def convert_seconds_to_hms(input_seconds):
    
    s = int(input_seconds % 60)

    remained_total_minutes = int((input_seconds - s) / 60)
    ##debug(remained_total_minutes)
    m = int(remained_total_minutes % 60)
    h = int((remained_total_minutes - m) / 60)

    return[h, m, s]


if timekeeper_settings['-focus_time-'] == None:
    #debug('-focus_time- not found, setting to:', focus_time_slider_default_value)
    timekeeper_settings['-focus_time-'] = focus_time_slider_default_value

def update_focus_time_slider_settings_and_timer(time):

    app['-focus_time_slider-'].update(time)
    event, values = app.read(timeout = 0)
    #get values only after read, or you'll get previous slider value
    
    focus_time_in_minutes = int(values['-focus_time_slider-'])
    focus_time_in_seconds = focus_time_in_minutes * 60

    ##debug('updatefuckslider', focus_time_in_minutes)

    app['-focus_time_settings-'].update(focus_time_in_minutes)

    hms = convert_seconds_to_hms(focus_time_in_seconds)
    app['-timer-'].update('{:02}:{:02}:{:02}'.format(hms[0], hms[1], hms[2]))
    return focus_time_in_seconds

focus_time_in_seconds = update_focus_time_slider_settings_and_timer(int(timekeeper_settings['-focus_time-']))


if timekeeper_settings['-short_break-'] == None:
    #debug('-short_break- not found, setting to:', short_break_slider_default_value)
    timekeeper_settings['-short_break-'] = short_break_slider_default_value

def update_short_break_slider_settings(time):

    app['-short_break_slider-'].update(time)
    event, values = app.read(timeout = 0)

    short_break_in_minutes = int(values['-short_break_slider-'])
    short_break_in_seconds = short_break_in_minutes * 60

    app['-short_break_settings-'].update(short_break_in_minutes)

    return short_break_in_seconds

short_break_in_seconds = update_short_break_slider_settings(int(timekeeper_settings['-short_break-']))


if timekeeper_settings['-long_break-'] == None:
    #debug('-long_break- not found, setting to:', long_break_slider_default_value)
    timekeeper_settings['-long_break-'] = long_break_slider_default_value

def update_long_break_slider_settings(time):

    app['-long_break_slider-'].update(time)
    event, values = app.read(timeout = 0)

    long_break_in_minutes = int(values['-long_break_slider-'])
    long_break_in_seconds = long_break_in_minutes * 60

    app['-long_break_settings-'].update(long_break_in_minutes)

    return long_break_in_seconds

long_break_in_seconds = update_long_break_slider_settings(int(timekeeper_settings['-long_break-']))



if timekeeper_settings['-total_rounds-'] == None:
    #debug('-total_rounds- not found, setting to:', total_session_rounds_slider_default_value)
    timekeeper_settings['-total_rounds-'] = total_session_rounds_slider_default_value

def update_total_rounds(rounds):
    #global total_session_rounds
    #total_session_rounds = usersettings_rounds

    app['-total_session_rounds_slider-'].update(rounds)
    event, values = app.read(timeout = 0)

    total_session_rounds = int(values['-total_session_rounds_slider-'])
    
    app['-total_session_rounds_settings-'].update(total_session_rounds)
    app['-round_info-'].update('{}/{}'.format(current_session_round, total_session_rounds))

    return total_session_rounds

total_session_rounds = update_total_rounds(timekeeper_settings['-total_rounds-'])


#focus_time_in_seconds = default_focus_time * 60
#hms = convert_seconds_to_hms(focus_time_in_seconds)
#app['-timer-'].update('{:02}:{:02}:{:02}'.format(hms[0], hms[1], hms[2]))



#app['-focus_time_settings-'].update(focus_time_slider_default_value)
#app['-short_break_settings-'].update(short_break_slider_default_value)
#app['-long_break_settings-'].update(long_break_slider_default_value)
#app['-total_session_rounds_settings-'].update(total_session_rounds_slider_default_value)

#start time is time.time() at the moment of start, start_seconds is the Focus time (min) * 60
#return list of [h,m,s (int), is_finished(bool)]





def run_countdown_timer(start_time, start_seconds):
    system_time = time.time()
    delta = system_time - start_time
    ##debug(delta)
    
    #original delta_sec = int(delta / 1)
    #delta_sec = int(delta / 1)
    delta_sec_trunc = math.trunc(delta)
    
    ##debug('delta_sec:', delta_sec, 'delta_sec_trunc:', delta_sec_trunc)

    remained_seconds = start_seconds - delta_sec_trunc
    #print('remained seconds', remained_seconds)
    show_time = convert_seconds_to_hms(remained_seconds)

    show_hours = show_time[0]
    show_minutes = show_time[1]
    show_seconds = show_time[2]

    if show_hours == 0 and show_minutes == 0 and show_seconds == 0:  
            is_timer_finished = True
    else: 
        is_timer_finished = False

    return [show_hours, show_minutes, show_seconds, is_timer_finished]

def update_timer(sec):
    hms = convert_seconds_to_hms(sec)
    app['-timer-'].update('{:02}:{:02}:{:02}'.format(hms[0], hms[1], hms[2]))

#update progress bar as precise as read(timeout) allows (less timeout, more refresh rate)
def update_progress_bar(start_time, focus_time_in_seconds, progress_bar_limit):
    delta = time.time() - start_time
    
    if focus_time_in_seconds != 0:
        percent = delta / focus_time_in_seconds
    else:
        percent = 0
    app['-progressbar-'].update(progress_bar_limit * percent)
    #print('updated progress bar')

def run_round_state_timer(state_lenght):
    global current_session_round
    #global current_round_state
    ##debug('current round state:', current_round_state)
    ##debug('START TIME:', start_time)
    ct = run_countdown_timer(start_time, state_lenght)
    
    hours = ct[0]
    minutes = ct[1]
    seconds = ct[2]
    is_timer_finished = ct[3]

    update_progress_bar(start_time, state_lenght, progress_bar_limit)

    app['-timer-'].update('{:02}:{:02}:{:02}' .format(hours, minutes, seconds))

    
    
    #mydict = {'a':1, 'b':2}

    if is_timer_finished:
        
        #if current_round_state == 'Focus time' and current_session_round <= total_session_rounds_in_progress:
            
            #current_session_round += 1
            #print('current_session_round:', current_session_round)
            #app['-round_info-'].update('{}/{}'.format(current_session_round, total_session_rounds_in_progress))

        finished_state = round_state_order.popleft()
        #debug('finished state:', finished_state)

        #add sound notification
        #if finished_state != 'Long break':
        
        playsound(notification_sound, block = False)

        if round_state_order != deque([]):
            next_round_state = round_state_order[0]
            #debug('next round state:', next_round_state)

            sg.popup('Done: ' + finished_state, 'Next: ' + next_round_state, font=('Helvetica', 24),
            auto_close=True, auto_close_duration=3, non_blocking=True, no_titlebar=True,
            keep_on_top=True, location=(1050,550))

            app['-current_state-'].update(next_round_state)

            if next_round_state == 'Focus time':
                current_session_round += 1
                #print('current_session_round:', current_session_round)
                app['-round_info-'].update('{}/{}'.format(current_session_round, total_session_rounds))


        next_round_state_start_time = time.time()
            
        return {'is_timer_finished': False, 'next_round_state_start_time': next_round_state_start_time}
        
    else:
        
        #is_timer_finished = False
        next_round_state_start_time = start_time
        #print({'is_timer_finished': False , 'next_round_state_start_time': next_round_state_start_time})
        return {'is_timer_finished': False , 'next_round_state_start_time': next_round_state_start_time}


def launch_pomodoro_schedule(focus_time_sec, short_break_sec, long_break_sec):
    ##debug('pomodoro')
    #for cur_round in range(1, total_session_rounds+1):
    #    #debug('current round', cur_round)
    global current_round_state
    if round_state_order != deque([]):

        current_round_state = round_state_order[0]
        ##debug('CURRENT ROUND STATE:', current_round_state)
    else:
        #debug('AAAAAAAAAAAAAA the deque is empty')
        is_timer_finished = True
        current_round_state = 'Finish'
        return {'is_timer_finished': True, 'next_round_state_start_time': 0}
    
    ##debug('left states:', round_state_order)
    
    if  current_round_state == 'Focus time':
        
        focus_time_result = run_round_state_timer(focus_time_sec)
        return focus_time_result
    if current_round_state == 'Short break':
        
        short_break_result = run_round_state_timer(short_break_sec)
        return short_break_result
        ct = run_countdown_timer(start_time, short_break_sec)
    
        hours = ct[0]
        minutes = ct[1]
        seconds = ct[2]
        is_timer_finished = ct[3]

        update_progress_bar(start_time, short_break_sec, progress_bar_limit)

        app['-timer-'].update('{:02}:{:02}:{:02}' .format(
        hours, minutes, seconds))

        #current_session_round += 1
        #app['-round_info-'].update('{}/{}'.format(current_session_round, total_session_rounds))

        #mydict = {'a':1, 'b':2}

        if is_timer_finished:

            finished_state = round_state_order.popleft()
            next_round_state = round_state_order[0]

            #debug('finished state:', finished_state)
            #debug('next round state:', next_round_state)
            
            next_round_state_start_time = time.time()
            
            return {'is_timer_finished': True, 'next_round_state_start_time': next_round_state_start_time}

        else:
            
            is_timer_finished = False
            next_round_state_start_time = start_time
            #print({'is_timer_finished': False , 'next_round_state_start_time': next_round_state_start_time})
            return {'is_timer_finished': False , 'next_round_state_start_time': next_round_state_start_time}

    if current_round_state == 'Long break':
        long_break_result = run_round_state_timer(long_break_sec)
        return long_break_result

        current_round_state_start_time = time.time()
        start_time = current_round_state_start_time

    #is_timer_finished = True
    #return {'is_timer_finished': False , 'current_session_round': current_session_round}
            
            #return next_round_state
            #is_timer_finished = False
            #return is_timer_finished
            #sg.popup('Countdown is finished. Resetting timer...', non_blocking = False, keep_on_top= True)
            #return is_timer_finished
    
        ##debug('working...', seconds)
        #is_timer_finished = False
        #event=''
        #return [deque([]), is_timer_finished]

def reset_timer():
    #debug('------------------------------------------------------')
    #debug('resetting timer...')

    focus_time_in_minutes = int(values['-focus_time_slider-'])
    focus_time_in_seconds = focus_time_in_minutes * 60

    hms = convert_seconds_to_hms(focus_time_in_seconds)
    app['-timer-'].update('{:02}:{:02}:{:02}'.format(hms[0], hms[1], hms[2]))
        
    app['-progressbar-'].update(0)
    
    app['-start/pause-'].update(image_data=start_base64_icon)
    app['-start/pause-'].metadata = 'start'

    global is_timer_running
    global is_timer_paused
    global is_timer_finished

    is_timer_running = False
    
    #why keep it paused?
    #is_timer_paused = True
    
    is_timer_finished = False

    #round_state_order = deque([])

    #debug('reset current task now:', current_task)
        
    #debug('reset current round state now:', current_round_state)
    #debug('current/total round now: {}/{}'.format(str(current_session_round), str(total_session_rounds)))
        
    #debug('reset Focus time now:', focus_time_in_seconds)
    #debug('reset Short break now:', short_break_in_seconds)
    #debug('reset Long break now:', long_break_in_seconds)
    #debug('reset round state order now:', round_state_order)
    
    #debug('------------------------------------------------------')
    return focus_time_in_seconds

def reset_after_finish(focus_time_in_seconds_in_process, values):
    #debug('reset_after_finish...')

    hms = convert_seconds_to_hms(focus_time_in_seconds_in_process)
    app['-timer-'].update('{:02}:{:02}:{:02}'.format(hms[0], hms[1], hms[2]))

            #current_task_in_progress = current_task

            #current_session_round_in_progress = int(current_session_round)
            #total_session_rounds_in_progress = int(total_session_rounds)

            #focus_time_in_seconds_in_process = int(focus_time_in_seconds)
            #short_break_in_progress = int(app['-short_break_settings-'].get())
            #long_break_in_progress = int(app['-long_break_settings-'].get())

    ##debug('focus_time_in_seconds_in_process:', focus_time_in_seconds_in_process)
    ##debug('slider value before reset:', values['-focus_time_slider-'])
            
            #probably a bug ???
            #values['-focus_time_slider-'] doesn't change, slider graphics is updated but not slider's value
            #value of the slider can be changed only by user input, using the actual slider
            #update: possible fix is to add app.read() before getting slider value,
            #value['slider'] is updated only after app.read(),
            #if you update app['slider'].update() withing the same app.read(), value['slider'] won't change
    
    ##debug(values)
    app['-focus_time_slider-'].update(float(focus_time_in_seconds_in_process/60))
    event, values = app.read(timeout = 0)
    app['-focus_time_settings-'].update(int(values['-focus_time_slider-']))

    #when next fresh start will be timer will take previous Focus time as its current Focus time
    focus_time_in_seconds = focus_time_in_seconds_in_process
    ##debug('slider value after reset:', values['-focus_time_slider-'])

    return focus_time_in_seconds

def reset_session():

    #debug('------------------------------------------------------')
    #debug('resetting session...')
    global current_round_state
    current_round_state = default_round_state
    app['-current_state-'].update(current_round_state)
    #debug('reset current state to default:', current_round_state)
    round_state_order.clear()
    #debug('reset round_state_order:', round_state_order)
    global current_session_round
    current_session_round = 1
    app['-round_info-'].update('{}/{}'.format(current_session_round, total_session_rounds))
    
    #
    if (values['-task_listbox-'] != []):
        current_task = values['-task_listbox-'][0]
    else:
        #debug('reset: listbox: no task chosen, choosing default task...')
        current_task = default_task
    app['-current_task-'].update(current_task)

    #app['-reset_timer-'].update(disabled = False)

    app['-reset_session-'].update(disabled = False)
    #enable settings
    app['-focus_time_slider-'].update(disabled = False)
    app['-short_break_slider-'].update(disabled = False)
    app['-long_break_slider-'].update(disabled = False)
    app['-total_session_rounds_slider-'].update(disabled = False)
    app['-reset_settings-'].update(disabled = False)
    
    #debug('session reset complete')
    #debug('------------------------------------------------------')

def make_round_state_order(disable_long_break):

    global round_state_order
    
    for a in range(0, total_session_rounds):

        round_state_order.append('Focus time')
    
        if total_session_rounds > 1:
            if a != total_session_rounds-1:
                round_state_order.append('Short break')
            elif disable_long_break == False:
                round_state_order.append('Long break')

        #debug('+1 round')

    #debug('make round state order:', round_state_order)

def make_stat_data(condition):

    cur_year = time.localtime().tm_year
    cur_month = time.localtime().tm_mon
    cur_day = time.localtime().tm_mday
    

    if condition == 'Week':
        cur_weekday = time.localtime().tm_wday
        #if cur_weekday == 0:
        date_start = '{}-{:02}-{:02}'.format(cur_year, cur_month,cur_day)
        #debug('date_start:', date_start)
    

    ##debug('current date: {:02}-{:02}'.format(cur_weekday,cur_day))

    #with open(timekeeper_test_data, 'r', encoding='UTF-8') as f:
            ##debug(f.read())
            #pass

#make_stat_data('Week')



while True:
    app['-localtime-'].update('{:02}:{:02} {}'.format(time.localtime().tm_hour, time.localtime().tm_min, datetime.date.today()))

    event, values = app.read(timeout = custom_timeout)
    
    if event !='__TIMEOUT__':
        pass
        ##debug(values)
        ##debug('Event:', event)
        ##debug('is running:', is_timer_running)
        ##debug('is paused:', is_timer_paused)
        ##debug('is reset:', is_timer_reset)
        ##debug('main loop Focus time:', focus_time_in_seconds)  
        ##debug('main loop slider value:', values['-focus_time_slider-'])
        ##debug(focus_time_in_seconds)
    ##debug(event)
    if app.FindElementWithFocus() == app['-task_to_add-']:

        if event == '-task_to_add-':
            ##debug()
            if len(values['-task_to_add-']) > 32:
                app['-task_to_add-'].update(values['-task_to_add-'][:32])
                sg.popup_ok('Reached max character limit: 32', title='Please, stop')
    if event == '-add_task-' and values['-task_to_add-'] != '':
        
        task_to_add = values['-task_to_add-']
        
        if task_to_add not in task_list:
            task_list.append(task_to_add)
            #debug('appended task:', task_to_add)
            app['-task_listbox-'].update(task_list)
            app['-task_to_add-'].update('')
            task_to_add = ''
            
            timekeeper_settings["-tasklist-"] = task_list.copy()

            ##debug('timekeeper_settings["-tasklist-"] before save:', timekeeper_settings["-tasklist-"])
            timekeeper_settings.save(filename='timekeeper_settings.json', path='.')            
            #debug('timekeeper_settings["-tasklist-"] after save:', timekeeper_settings["-tasklist-"])
            
            #debug('tasklist:', task_list)

        #if task_to_add not in timekeeper_settings["-tasklist-"]:

            #timekeeper_settings["-tasklist-"] = task_list
            ##debug('added task to settings')
            #

    if event == '-stat_history-':
        #doesn't highlight the text in combo element
        #app['-stat_history-'].widget.select_clear()
        pass

    if event == '-delete_task-' and values['-task_listbox-'] != []:

        #debug('new task_list:', task_list)
        
        if values['-task_listbox-'][0] in task_list:
        
            timekeeper_settings["-tasklist-"] = task_list
            task_list.remove(values['-task_listbox-'][0])
            app['-task_listbox-'].update(task_list)

            app['-current_task-'].update(default_task)

            timekeeper_settings.save(filename='timekeeper_settings.json', path='.')
            #debug('tasklist:', task_list)
            #debug('timekeeper_settings["-tasklist-"]:', timekeeper_settings["-tasklist-"])

    ##debug('timekeeper_settings["-tasklist-"]:', timekeeper_settings["-tasklist-"])
    ##debug(values['-task_listbox-'])
    if event == '-task_listbox-' and is_timer_running == False and is_timer_paused == False:
        
        if values['-task_listbox-'] != []:
            current_task = values['-task_listbox-'][0]
        else:
            current_task = default_task
        
        ##debug('listbox: current task now:',current_task)
        app['-current_task-'].update(current_task)
    
    if event == '-focus_time_slider-':
        ##debug(values['-focus_time_slider-'])
        app['-focus_time_settings-'].update(int(values['-focus_time_slider-']))
        
        focus_time_in_minutes = int(app['-focus_time_settings-'].get())
        focus_time_in_seconds = focus_time_in_minutes * 60

        hms = convert_seconds_to_hms(focus_time_in_seconds)
        app['-timer-'].update('{:02}:{:02}:{:02}' .format(hms[0], hms[1], hms[2]))

        timekeeper_settings['-focus_time-'] = focus_time_in_minutes
        #timekeeper_settings.save(filename='timekeeper_settings.json', path='.')

    if event == '-short_break_slider-':
        app['-short_break_settings-'].update(int(values['-short_break_slider-']))
        short_break_in_minutes = int(app['-short_break_settings-'].get())
        short_break_in_seconds = short_break_in_minutes * 60

        timekeeper_settings['-short_break-'] = short_break_in_minutes

    if event == '-long_break_slider-':
        app['-long_break_settings-'].update(int(values['-long_break_slider-']))
        long_break_in_minutes = int(app['-long_break_settings-'].get())
        long_break_in_seconds = long_break_in_minutes * 60

        timekeeper_settings['-long_break-'] = long_break_in_minutes

    if event == '-total_session_rounds_slider-':
        app['-total_session_rounds_settings-'].update(int(values['-total_session_rounds_slider-']))

        total_session_rounds = int(app['-total_session_rounds_settings-'].get())

        app['-round_info-'].update('{}/{}'.format(current_session_round, total_session_rounds))

        disable_long_break = False
        if long_break_in_seconds == 0:
            disable_long_break = True
        
        round_state_order.clear()
        make_round_state_order(disable_long_break)

        timekeeper_settings['-total_rounds-'] = total_session_rounds

        
    ############################################################################################################
    ############################################################################################################
    ############################################################################################################
    if event == '-start/pause-' and focus_time_in_seconds != 0:
        
        event = app['-start/pause-'].metadata
        ##debug('start/pause event:', event)
        #flip start/pause icon to pause ||
        if event == 'start':
            app['-start/pause-'].update(image_data=pause_base64_icon)
            app['-start/pause-'].metadata = 'pause'
            
        #flip start/pause icon to pause start |>
        if event == 'pause':
            app['-start/pause-'].update(image_data=start_base64_icon)
            app['-start/pause-'].metadata = 'start'

    #fresh timer start or after the session reset
    if event  == 'start' and is_timer_running == False and is_timer_paused == False:
        #debug('FRESH START OR AFTER SESSION RESET')
        if (values['-task_listbox-'] != []):
            current_task = values['-task_listbox-'][0]
        else:
            ##debug('start: listbox: no task chosen, choosing default task...')
            app_location = app.current_location()
            ##debug(app_location)
            answer = sg.popup_yes_no('You haven\'t selected a task.\nContinue?', title='No task')
            
            if answer == 'Yes':
                current_task = default_task
            else:
                app['-start/pause-'].update(image_data=start_base64_icon)
                app['-start/pause-'].metadata = 'start'
                continue

        app['-current_task-'].update(current_task)
        ##debug('current task:', current_task)
        ##debug('round/total:{}/{}'.format(current_session_round, total_session_rounds))
        ##debug('Focus time:', app['-focus_time_settings-'].get())
        ##debug('Short break:', app['-short_break_settings-'].get())
        ##debug('Long break:', app['-long_break_settings-'].get())
        
        #copy seconds so that the Focus time slider doesn't change the timer while it's running
        #current_task_in_progress = current_task

        #current_session_round_in_progress = current_session_round
        #total_session_rounds_in_progress = total_session_rounds

        #focus_time_in_seconds_in_process = focus_time_in_seconds
        #short_break_in_seconds__progress = short_break_in_seconds
        #long_break_in_seconds_in_progress = long_break_in_seconds
        #debug('------------------------------------------------------')
        

        #debug('current task:', current_task)
        #debug('current round state:', current_round_state)
        ##debug('current round:', )
        ##debug('total rounds:', total_session_rounds)
        #debug('current/total round: {}/{}'.format(str(current_session_round), str(total_session_rounds)))
        
        #focus_time_in_seconds = focus_time_in_seconds / 10
        #short_break_in_seconds = short_break_in_seconds / 10
        #long_break_in_seconds = long_break_in_seconds / 10
        
        disable_long_break = False
        if long_break_in_seconds == 0:
            disable_long_break = True

        #debug('Focus time:', focus_time_in_seconds)
        #debug('Short break:', short_break_in_seconds)
        #debug('Long break:', long_break_in_seconds)

        #state order for pomodoro to work with
        # 'locked' total_session_rounds_in_progress (isn't affected by slider while pomodoro is working)
        
        #if round_state_order != deque([]):
            #print('state order is empty')
            ##debug('STATE ORDER IS NOT EMPTY:', round_state_order)
            ##debug('clearing order...')
            #round_state_order.clear()
            ##debug('cleared order:', round_state_order)
        if round_state_order == deque([]):
            make_round_state_order(disable_long_break)
        #debug('round state order:', round_state_order)
        
        progress_bar_value = int(0)
        
        start_time = time.time()
        start_date = time.localtime()

        start_date_str = 'start date: {:04}-{:02}-{:02}'.format(start_date.tm_year, start_date.tm_mon, start_date.tm_mday)
        start_date_time_str = 'start date time: {:02}:{:02}'.format(start_date.tm_hour, start_date.tm_min)
        start_date_iso = start_date_str = '{:04}-{:02}-{:02}'.format(start_date.tm_year, start_date.tm_mon, start_date.tm_mday) 


        start_date_minute_sum = (start_date.tm_hour * 60) + start_date.tm_min
        focus_time_to_minutes = int(focus_time_in_seconds / 60)
        minutes_before_day_change = 1440 - start_date_minute_sum

        #if start_date_minute_sum + focus_time_to_minutes > 1440:

            #debug('focus time will end next day!', start_date_minute_sum + focus_time_to_minutes)

        #debug(start_date_str)
        #debug(start_date_time_str)
        
        #debug('minutes before changing date:', minutes_before_day_change)
        #debug('total focus minutes:', focus_time_to_minutes)
        #debug('------------------------------------------------------')



        is_timer_running = True
        #is_timer_finished = False
        #app['-reset_timer-'].update(disabled = True)

        app['-reset_session-'].update(disabled = True)

        app['-focus_time_slider-'].update(disabled = True)
        app['-short_break_slider-'].update(disabled = True)
        app['-long_break_slider-'].update(disabled = True)
        app['-total_session_rounds_slider-'].update(disabled = True)

        app['-reset_settings-'].update(disabled = True)
        

    #pause the timer
    if event == 'pause' and is_timer_running and is_timer_paused == False:
        ##debug('paused: ', event)
        pause_time = time.time()
        
        delta = pause_time - start_time
        #debug('pause delta', delta)

        #app['-reset_timer-'].update(disabled = False)
        app['-reset_session-'].update(disabled = False)

        is_timer_paused = True
        is_timer_running = False

    #resume timer after pause
    #adding and is_timer_reset == True doesn't allow resume from just pause
    if event  == 'start' and is_timer_paused == True:
        #debug('RESUMING...')
        is_timer_paused = False
        is_timer_running = True
        
        ##debug("start_time", start_time)
        ##debug("reset_time", reset_time)
        
        #if is_timer_reset:
            #is_timer_reset = False
            #('if reset')
            #start_time = reset_time
            ##debug('IF RESET')
            #start_time = time.time()
        #else:
        start_time = time.time() - delta
        
        
        
        

        # if is_timer_reset == True:
        #     #debug('TIMER IS RESET!!!')
        #     app['-reset_timer-'].update(disabled = True)

        #     app['-reset_session-'].update(disabled = True)

        #     app['-focus_time_slider-'].update(disabled = True)
        #     app['-short_break_slider-'].update(disabled = True)
        #     app['-long_break_slider-'].update(disabled = True)
        #     app['-total_session_rounds_slider-'].update(disabled = True)

        #     app['-reset_settings-'].update(disabled = True)

        

        #app['-reset_timer-'].update(disabled = True)
        app['-reset_session-'].update(disabled = True)

        # #debug('------------------------------------------------------')
        # #debug('current task:', current_task)
        # #debug('current round state:', current_round_state)
        # #debug('current/total round: {}/{}'.format(str(current_session_round), str(total_session_rounds)))
        # ##debug('total rounds:', total_session_rounds)

        # #debug('Focus time:', focus_time_in_seconds)
        # #debug('Short break:', short_break_in_seconds)
        # #debug('Long break:', long_break_in_seconds)
        # #debug('round state order:', round_state_order)
        # #debug('------------------------------------------------------')

    #print('is_timer_running:', is_timer_running)
    ##debug(event)
    
    ##debug('event:', event)
    
    #reset current round state, keep the session round 
    if event == '-reset_timer-' and is_timer_paused == True:
        #focus_time_in_seconds = reset_timer()
        reset_timer()
        #is_timer_paused = False
        is_timer_reset = True
        #reset_time = time.time()
        
    #reset session rounds
    if event == '-reset_session-' and is_timer_paused == True:
        #app['-current_task-'].update(default_task)
        ##debug('REEEEEEE current task = default task', current_task)
        reset_session()
        reset_timer()

        is_timer_paused = False
        is_timer_reset = True
        
    if event == '-reset_settings-':

        # in PySimpleGUI Call Reference Mike, the author says that some methods are shown but they're in fact internal,
        # He says that the PSG code is inconsistent

        # "Some functions / methods may be internal only yet exposed in this documentation"
        # "As a result, sometimes internal only functions or methods that you are not supposed to be calling
        # are accidentally shown in this documentation. Hopefully these accidents don't happen often."
        
        #probably a bug ???  
        #values['-focus_time_slider-'] doesn't change, slider graphics is updated but not slider's value
        #value of the slider can be changed only by user input, using the actual slider
        #update: possible fix is to add app.read() before getting slider value,
        #value['slider'] is updated only after app.read(),
        #if you update app['slider'].update() withing the same app.read(), value['slider'] won't change

        timekeeper_settings['-focus_time-'] = focus_time_slider_default_value
        focus_time_in_seconds = update_focus_time_slider_settings_and_timer(focus_time_slider_default_value)
        
        #app['-focus_time_slider-'].update(focus_time_slider_default_value)
        #event, values = app.read(timeout = 0)
        #get values only after read, or you'll get previous slider value
        #focus_time_in_minutes = int(values['-focus_time_slider-'])
        #focus_time_in_seconds = focus_time_in_minutes * 60

        #app['-focus_time_settings-'].update(focus_time_in_minutes)

        #hms = convert_seconds_to_hms(focus_time_in_seconds)
        #app['-timer-'].update('{:02}:{:02}:{:02}'.format(hms[0], hms[1], hms[2]))
        
        ##debug('Focus time in seconds after slider value update:', focus_time_in_seconds)

        timekeeper_settings['-short_break-'] = short_break_slider_default_value
        short_break_in_seconds = update_short_break_slider_settings(short_break_slider_default_value)


        timekeeper_settings['-long_break-'] = long_break_slider_default_value
        long_break_in_seconds = update_long_break_slider_settings(long_break_slider_default_value)


        timekeeper_settings['-total_rounds-'] = total_session_rounds_slider_default_value
        total_session_rounds = update_total_rounds(total_session_rounds_slider_default_value)
    
    #print(values['-stat_history_combo-'])
    ##debug(values)
    if event == '-stat_history_combo-':
        
        if fig_canvas_agg:
            delete_figure_agg(fig_canvas_agg)

        if values['-stat_history_combo-'] == 'Week':
            fig_canvas_agg = plot_current_week()
            current_plot = 'Week'
            timekeeper_settings['-current_plot-'] = current_plot
            
        elif values['-stat_history_combo-'] == 'Month':
            fig_canvas_agg = plot_current_month()
            current_plot = 'Month'
            timekeeper_settings['-current_plot-'] = current_plot

        elif values['-stat_history_combo-'] == 'Year':
            fig_canvas_agg = plot_current_year()
            current_plot = 'Year'
            timekeeper_settings['-current_plot-'] = current_plot


        # if values['-stat_history_combo-'] == 'Week':
            
        #     taskdata = {'2022-08-01':240, '2022-08-02':180, '2022-08-03':60, '2022-08-04':180}

        #     data_range = 7
        #     data_values = [1,2,3,4,5,6,7]
        #     data_labels = ['Mon','Tue','Wen','Thu','Fri','Sat','Sun']
        #     fig = PyplotGGPlotSytleSheet(data_range, data_values, data_labels)
        #     fig_canvas_agg = draw_figure(app['-CANVAS-'].TKCanvas, fig)

        # if values['-stat_history_combo-'] == 'Month':
        #     taskdata = {'2022-08-01':240, '2022-08-02':180, '2022-08-03':60, '2022-08-04':180}
        #     data_range = 30
        #     data_values = [i for i in range(0,30)]
        #     data_labels = [i for i in range(0,30)]
        #     fig = PyplotGGPlotSytleSheet(data_range, data_values, data_labels)
        #     fig_canvas_agg = draw_figure(app['-CANVAS-'].TKCanvas, fig)

        # if values['-stat_history_combo-'] == 'Year':
        #     taskdata = {'2022-08-01':240, '2022-08-02':180, '2022-08-03':60, '2022-08-04':180}
        #     data_range = 12
        #     data_values = [1,2,3,4,5,6,7,8,9,10,11,12]
        #     data_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        #     fig = PyplotGGPlotSytleSheet(data_range, data_values, data_labels)
        #     fig_canvas_agg = draw_figure(app['-CANVAS-'].TKCanvas, fig)

    if event == '-py_plot-':
        draw_plot()

    if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT) and sg.popup_yes_no('Do you really want to exit?', title='Exit') == 'Yes':
        #sg.user_settings_set_entry('-location-', app.current_location())
        timekeeper_settings['-location-'] = app.current_location()
        break

    if event == 'Edit Me':
        sg.execute_editor(__file__)
    if event == 'Version':
        sg.popup_scrolled(sg.get_versions())
  
    if is_timer_running == True:
        
        ##debug('Focus time in progress:', focus_time_in_seconds_in_process)
        ##debug('Focus time:', focus_time_in_seconds)
        
        #focus_time_in_seconds
        #short_break_in_seconds
        #long_break_in_seconds

        schedule_state = launch_pomodoro_schedule(focus_time_in_seconds, short_break_in_seconds, long_break_in_seconds)
        
        #print(schedule_state)
        next_round_state_start_time = schedule_state['next_round_state_start_time']
        is_timer_finished = schedule_state['is_timer_finished']

        if is_timer_finished == False and next_round_state_start_time != 0:
            start_time = next_round_state_start_time
        
        #current_session_round_in_progress = schedule_state[1]
        #focus_time_in_seconds_in_process
        #short_break_in_seconds__progress
        #long_break_in_seconds_in_progress
        #next_round_state = next_round_state_and_finish_state[0]
        #is_timer_finished = next_round_state_and_finish_state[1]
        if is_timer_finished == True:
            reset_session()
            reset_timer()

            finish_focus_time = int(focus_time_in_seconds / 60)
            finish_short_break = int(short_break_in_seconds / 60)
            finish_long_break = int(long_break_in_seconds / 60)

            total_focus_time_in_min = 0
            total_break_time_in_min = 0

            for a in range(0, total_session_rounds):
                total_focus_time_in_min += finish_focus_time
                total_break_time_in_min += finish_short_break

            total_break_time_in_min = total_break_time_in_min - finish_short_break + finish_long_break

            #start_date_str = 'start date: {:04}-{:02}-{:02}'.format(start_date.tm_year, start_date.tm_mon, start_date.tm_mday)

            #debug('------------------------------------------------------')
            #debug('Finish current task:', current_task)
            #debug('Finish Focus time:', finish_focus_time)
            #debug('Finish Short break:', finish_short_break)
            #debug('Finish Long break:', finish_long_break)
            #debug('Finish Total rounds:', total_session_rounds)
            #debug('Finish date:', start_date_str)
            #debug('total focus time in minutes:', total_focus_time_in_min)
            #debug('total break time in minutes:', total_break_time_in_min)
            #debug('------------------------------------------------------')

            ##debug('------------------------------------------------------')
            ##debug('exporting data  to txt...')
            
            #with open(timekeeper_test_data, 'a', encoding='UTF-8') as f:
            #    f.write('date: {}, '.format('{:04}-{:02}-{:02}'.format(start_date.tm_year, start_date.tm_mon, start_date.tm_mday)))
            #    f.write('focus time: {:03}, '.format(total_focus_time_in_min))
            #    f.write('break time: {:02}, '.format(total_break_time_in_min))
            #    f.write('task: {}\n'.format(current_task))
            
            ##debug('exporting data  to txt Done')
            ##debug('------------------------------------------------------')

            conn = create_connection(db_file)
            today_date = datetime.date.today()
            #start_date_iso
            insert_data(conn, (today_date, total_focus_time_in_min, total_break_time_in_min, current_task))
            
            if fig_canvas_agg:
                delete_figure_agg(fig_canvas_agg)
            fig_canvas_agg = update_plots()
            
            #if current_plot == 'Week':
            #    fig_canvas_agg = plot_current_week()
            #elif current_plot == 'Month':
            #    fig_canvas_agg = plot_current_month()
            #elif current_plot == 'Year':
            #    fig_canvas_agg = plot_current_year()

            update_totals()

            sg.popup('Session complete', font=('Helvetica', 24), auto_close=True, auto_close_duration=3, non_blocking=True, no_titlebar=True, keep_on_top=True, location=(1050,550))
        
        
app.close()

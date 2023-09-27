from __future__ import print_function

import tkinter as tk
from datetime import datetime
import os
from tkinter import *
from tkinter.ttk import *

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

#timer adapted from this tutorial: https://www.youtube.com/watch?v=mdfuJPGLhPM


running = False
session = False
hours, minutes, seconds = 0, 0, 0

start_time = ''
end_time = ''


def start():
    now=datetime.now()
    global start_time

    #record start time for session
    global session
    if not session:
        start_time = datetime(now.year,now.month,now.day,now.hour,now.minute).isoformat()
        session = True

    #ensures that the start time is not overwriten when the timer is paused
    global running
    if not running:
        update()
        running = True


def stop():
    global running
    if running:
        # cancel updating of time using after_cancel()
        stopwatch_label.after_cancel(update_time)
        running = False


#logs timer session to google calendar
def log():

    #gets the time at the end of the session when the user presses 'log'
    now=datetime.now()
    global end_time
    end_time = datetime(now.year,now.month,now.day,now.hour,now.minute).isoformat()

    global running
    if running:
        #stops timer
        stopwatch_label.after_cancel(update_time)
        running = False

    # set variables back to zero
    global hours, minutes, seconds
    hours, minutes, seconds = 0, 0, 0
    # set label back to zero
    stopwatch_label.config(text='00:00:00')


    #creates window to add a note to your sesson
    newWindow = Toplevel(root)
    newWindow.title("Add Notes")
    newWindow.geometry("400x200")
    notes_lable = Label(newWindow,text="Add a note for your study session:",font=('System', 10))
    notes_textbox = Text(newWindow, height=5, width=60)

    INPUT = ''
    def get_text():
        #gets input in textbox
        INPUT = notes_textbox.get("1.0", "end-1c")
        create_event(start_time, end_time, INPUT)
        newWindow.quit()

    #calls get_text when user presses to submit button to record note and call create_event
    notes_submit = tk.Button(newWindow,text="Submit",height=5,width=10,font=('System', 30),command=lambda:get_text())

    notes_lable.pack()
    notes_textbox.pack()
    notes_submit.pack()
    


def update():
    
    global hours, minutes, seconds
    seconds += 1
    if seconds == 60:
        minutes += 1
        seconds = 0
    if minutes == 60:
        hours += 1
        minutes = 0        
    # format time to include leading zeros
    hours_string = f'{hours}' if hours > 9 else f'0{hours}'
    minutes_string = f'{minutes}' if minutes > 9 else f'0{minutes}'
    seconds_string = f'{seconds}' if seconds > 9 else f'0{seconds}'
    # update timer label after 1000 ms (1 second)
    stopwatch_label.config(text=hours_string + ':' + minutes_string + ':' + seconds_string)
    # after each second (1000 milliseconds), call update function
    # use update_time variable to cancel or pause the time using after_cancel
    global update_time
    update_time = stopwatch_label.after(1000, update)



#creates the event to the calendar using a start and end time, and notes value
def create_event(start, end, notes):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # builds the event for the calendar
        event = {
            'summary': 'Coding Practice',
            'description': notes,
            'colorId':"9",
            'start': {'dateTime': start,
                      'timeZone': 'America/New_York',
            },
            'end': {'dateTime': end,
                    'timeZone': 'America/New_York',
            },

        }

        #insert event into user calendar
        event = service.events().insert(calendarId='primary', body=event).execute()

        #prints link to event
        print (event.get('htmlLink'))


    except HttpError as error:
        print('An error occurred: %s' % error)



# create main window
root = tk.Tk()
root.geometry('490x210')
root.title('Coding Productivity Tracker')

# label to display time
stopwatch_label = tk.Label(text='00:00:00', font=('Terminal', 80))
stopwatch_label.pack()

# start, pause, reset, quit buttons
start_button = tk.Button(text='start', height=5, width=7, font=('System', 20), command=start)
start_button.pack(side=tk.LEFT)
pause_button = tk.Button(text='stop', height=5, width=7, font=('System', 20), command=stop)
pause_button.pack(side=tk.LEFT)
log_button = tk.Button(text='log', height=5, width=7, font=('System', 20), command=log)
log_button.pack(side=tk.LEFT)
quit_button = tk.Button(text='quit', height=5, width=7, font=('System', 20), command=root.quit)
quit_button.pack(side=tk.LEFT)

# run app
root.mainloop() 
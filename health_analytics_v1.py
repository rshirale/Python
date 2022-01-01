import csv
import requests
import io
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

plt.style.use('Solarize_Light2')

workout = []
date = []
gpx = []


# Base class to create inheritance
class HealthAnalytics:
    def __init__(self, activity_id):
        self.activity_id = activity_id


# Class to hold workout summary data
class WorkoutSummary(HealthAnalytics):
    def __init__(self, activity_id, activity_type, distance, duration, average_pace, average_speed, cals_burned, climb):
        super().__init__(activity_id)
        self.activity_type = activity_type  # Running, Walking etc
        self.distance = float(distance)  # Distance in miles
        self.duration = duration  # Duration in mins and hours
        try:
            average_pace.replace(':', '.')
            if float(average_pace.replace(':', '.')) > 50:
                self.average_pace = float(0)  # Average Pace replacing 11:21 to 11.21
            else:
                self.average_pace = float(average_pace.replace(':', '.'))
        except ValueError:
            self.average_pace = float(0)  # If string is empty, replace with 0
        try:
            self.average_speed = float(average_speed)  # Speed in mph
        except ValueError:
            self.average_speed = float(0)  # If string is empty, replace with 0

        self.calories_burned = int(cals_burned.replace('.', ''))

        self.climb = int(climb)  # Climb in feet

    def __str__(self):
        return f'Activity ID: {self.activity_id}\t, Type: {self.activity_type}\t, Pace: {self.average_pace}\t, Speed: {self.average_speed}\t' \
               f'Calories: {self.calories_burned}\t, Climb: {self.climb}\t, Distance: {self.distance}'


# Class to hold workout date information
class Date(HealthAnalytics):
    def __init__(self, activity_id, date, time, day, month, year, hour, am_pm):
        super().__init__(activity_id)
        # self.activity_id = activity_id
        self.date = date  # Extract only date
        self.time = time  # Extract only time
        self.day = day  # Extract the day
        self.month = month  # Extract month
        self.year = year  # Extract year
        self.hour = hour  # Extract hour
        self.am_pm = am_pm

    # Creating @classmethod to apply different kinds of transformations to date information.
    @classmethod
    def date_from_string(cls, activity_id, date):
        activity_id = activity_id
        _date, _time = date.split(' ')
        # print(_date)
        day = datetime.strptime(_date, "%Y-%m-%d").strftime("%A")
        month = datetime.strptime(_date, "%Y-%m-%d").strftime("%B")
        year = datetime.strptime(_date, "%Y-%m-%d").strftime("%Y")
        time = datetime.strptime(_time, "%H:%M:%S").strftime("%I:%M %p")
        hour = datetime.strptime(_time, "%H:%M:%S").strftime("%I")
        am_pm = datetime.strptime(_time, "%H:%M:%S").strftime("%p")
        return cls(activity_id, _date, time, day, month, year, hour, am_pm)

    def __str__(self):
        return f'Activity ID: {self.activity_id}\t, Date: {self.date}\t, Time: {self.time}\t' \
               f'Day: {self.day}\t, Month: {self.month}\t, Year: {self.year}\t, Hour: {self.hour}, AM/PM: {self.am_pm}'


# Class to hold GPX information
class GPXInfo(HealthAnalytics):
    def __init__(self, activity_id, gpx_file_name):
        super().__init__(activity_id)
        self.gpx_file_name = gpx_file_name  # File contains spatial information

    def __str__(self):
        return f'Activity ID: {self.activity_id} and gpxfilename: {self.gpx_file_name}'


def get_workout_data(filename):
    # Read CSV workout data from file exported from workout app
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        for row in reader:
            # print(row)
            workout.append(WorkoutSummary(row[0], row[2], row[4], row[5], row[6], row[7], row[8], row[9]))
            date.append(Date.date_from_string(row[0], row[1]))
            gpx.append(GPXInfo(row[0], row[13]))


def print_head():
    for count, value in enumerate(date):
        if count != 5:
            print(value)
        else:
            break


def date2yday(x):
    """Convert matplotlib datenum to days since 2020-07-19."""
    y = x - mdates.date2num(datetime(2020, 7, 19))
    return y


def yday2date(x):
    """Return a matplotlib datenum for *x* days after 2020-07-19."""
    y = x + mdates.date2num(datetime(2020, 7, 19))
    return y


def plot_data():
    distance = np.array([row.distance for row in workout])
    date_np = np.array([row.date for row in date], dtype='datetime64')


    # Plotting distance time-series data
    df = pd.DataFrame(list(zip(date_np, distance)), columns=['Date', 'Distance']).set_index('Date')
    fig, ax = plt.subplots(figsize=(8.8, 4), layout='constrained', facecolor=(.18, .31, .31))
    ax.set_facecolor('#eafff5')
    ax.plot(df.index, df.Distance, 'xkcd:crimson', label='raw data')
    ax.plot(df.Distance.rolling(window=12).mean(), label='rolling mean')

    ax.legend()
    secax_x = ax.secondary_xaxis('top', functions=(date2yday, yday2date))
    secax_x.set_xlabel('Number of days')
    ax.set_title('Daily distance vs. time chart', color='0.7')
    ax.set_xlabel('time (date)', color='c')
    ax.set_ylabel('distance (miles)', color='peachpuff')

    ax.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='both', width=2)
    ax.tick_params(which='major', length=7)
    ax.tick_params(which='minor', length=4, color='r')
    ax.tick_params(labelcolor='tab:orange')

    plt.show()


def plot_scatter():
    distance = np.array([row.distance for row in workout])
    average_speed = np.array([row.average_speed for row in workout])
    calories = np.array([row.calories_burned for row in workout])
    climb = np.array([row.climb for row in workout])
    pace = np.array([row.average_pace for row in workout])
    date_np = np.array([row.date for row in date], dtype='datetime64')

    # Plotting distance time-series data
    df = pd.DataFrame(list(zip(date_np, distance, average_speed, calories, climb, pace)),
                      columns=['Date', 'Distance', 'Speed', 'Calories', 'Climb', 'pace']).set_index('Date')
    fig, ax = plt.subplots(figsize=(8.8, 4), layout='constrained', facecolor=(.18, .31, .31))
    ax.set_facecolor('#eafff5')
    ax.plot(df.index, df.Distance, 'xkcd:crimson', label='Distance raw data')
    ax.plot(df.Distance.rolling(window=12).mean(), label='Distance rolling mean')
    ax.plot(df.pace.rolling(window=12).mean(), label='Pace rolling mean miles/hr')
    ax.legend()
    ax.set_title('Daily distance vs. time chart', color='0.7')
    ax.set_xlabel('time (date)', color='c')
    ax.set_ylabel('distance (miles)', color='peachpuff')
    ax.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='both', width=2)
    ax.tick_params(which='major', length=7)
    ax.tick_params(which='minor', length=4, color='r')
    ax.tick_params(labelcolor='tab:orange')

    plt.show()


def plot_boxplot():
    distance = np.array([row.distance for row in workout])
    average_speed = np.array([row.average_speed for row in workout])
    calories = np.array([row.calories_burned for row in workout])
    climb = np.array([row.climb for row in workout])
    pace = np.array([row.average_pace for row in workout])
    date_np = np.array([row.date for row in date], dtype='datetime64')

    fig, ax = plt.subplots(1, 2, figsize=(9, 4), layout='constrained')
    green_diamond = dict(markerfacecolor='g', marker='D')
    labels = ['samples']
    ax[0].boxplot(distance, flierprops=green_diamond, labels=labels)
    ax[0].set_title('Distance distribution')
    ax[0].set_ylabel('Observed values')

    ax[1].boxplot(pace, flierprops=green_diamond, labels=labels)
    ax[1].set_title('Pace distribution')
    ax[1].set_ylabel('Observed values')

    fig, ax = plt.subplots(figsize=(4, 4), layout='constrained')
    green_diamond = dict(markerfacecolor='g', marker='D')
    labels = ['samples']

    ax.boxplot(climb, flierprops=green_diamond, labels=labels, notch=True)
    ax.set_title('climb distribution')
    ax.set_ylabel('Observed values')

    plt.show()


if __name__ == '__main__':
    file = r'C:\Users\rahul\PycharmProjects\pythonProject\health_analytics\01-runkeeper-data-export-2021-12-29-232343\cardioActivities.csv'
    # outfile = 'earthquakes.png'
    get_workout_data(file)
    plot_data()
    plot_scatter()
    print_head()
    plot_boxplot()

    # create_png(url, outfile)

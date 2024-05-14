import csv
from math import atan
import math
import threading
import time
from djitellopy import Tello
from time import sleep
    

# Initialize Tello object
drone = Tello()


def calculate_angle(x, y):
    # Calculate the angle in radians
    angle_rad = math.atan2(y, x)
    
    # Convert radians to degrees
    angle_deg = math.degrees(angle_rad)
    
    # Ensure angle is between 0 and 360 degrees
    if angle_deg < 0:
        angle_deg += 360
    
    return angle_deg


def clamp_angle(angle):
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle

def fly_path(path):
    # Take off
    current_angle = 0
    for i in range(len(path)-1):
        x1,y1 = path[i]
        x2,y2 = path[i+1]
        dx = x2 - x1
        dy = y2 - y1
        distance = round((dx ** 2 + dy ** 2) ** 0.5)
        target_angle = round(calculate_angle(dy,-dx))
        move_angle = clamp_angle(current_angle-target_angle)
        current_angle = target_angle
        clockwise = True
        if move_angle >= 180:
            clockwise = False
            move_angle = 360 - move_angle
        if clockwise:
            drone.rotate_clockwise(move_angle)
        else:
            drone.rotate_counter_clockwise(move_angle)
        drone.move_forward(distance)


def connect():
    drone.connect()
    drone.send_rc_control
    print(drone.get_battery())
   

def launch():

    drone.takeoff()
    drone.move_up(50)

def land():
    drone.land()
    drone.end()

def round_to_nearest_ten(number):
    return round(number / 10) * 10

def read_csv(file_path):
    data = []
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header row
        for row in csvreader:
            x, y, _ = map(float, row)
            xcm = round_to_nearest_ten(-x * 400)
            ycm = round_to_nearest_ten(y *400)
            data.append((ycm, xcm))
    return data

def main():
    connect()
    launch()
    path = read_csv("path_pos_20s.csv")
    fly_path(path)
    land()
 

if __name__ == "__main__":
    main()

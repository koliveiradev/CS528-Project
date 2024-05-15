import time
import math
import board
import busio
import adafruit_mpu6050

from record import countdown, post_file


SCL_1 = board.IO1
SDA_1 = board.IO0
i2c_1 = busio.I2C(SCL_1, SDA_1) 
mpu_1 = adafruit_mpu6050.MPU6050(i2c_1)

SCL_2 = board.IO3
SDA_2 = board.IO2
i2c_2 = busio.I2C(SCL_2, SDA_2) 
mpu_2 = adafruit_mpu6050.MPU6050(i2c_2)

orientation = [0, 0, 0]

# Return average of acceleration data from both MPUs
def get_avg_acc():
    return [(a_1+a_2)/2 for a_1, a_2 in zip(mpu_1.acceleration, mpu_2.acceleration)]

# Given both mpu objects and a duration in seconds
# Records gyroscope and acceleration readings for duration and averages them to get gyro bias and initial gravity vector
# Sensor must be held still during calibration for this to work 
def calibrate(mpu_1,mpu_2, duration):
    global grav_mag
    start_time = time.monotonic()
    gyro_bias_1 = [0.0, 0.0, 0.0]
    gyro_bias_2 = [0.0, 0.0, 0.0]
    gravity = [0.0, 0.0, 0.0]
    readings_1 = []
    readings_2 = []
    readings_acc = []

    while time.monotonic() - start_time < duration:
        gyro_1 = mpu_1.gyro
        gyro_2 = mpu_2.gyro
        acc = get_avg_acc()
        # print(gyro_1, gyro_2, acc)
        readings_1.append(gyro_1)
        readings_2.append(gyro_2)
        readings_acc.append(acc)
    
    for reading_1, reading_2, reading_acc in zip(readings_1, readings_2, readings_acc):
        gyro_bias_1 = [bias + reading_1[i] for i, bias in enumerate(gyro_bias_1)]
        gyro_bias_2 = [bias + reading_2[i] for i, bias in enumerate(gyro_bias_2)]
        gravity = [axis + reading_acc[i] for i, axis in enumerate(gravity)]

    gyro_bias_1 = [bias / len(readings_1) for bias in gyro_bias_1]
    gyro_bias_2 = [bias / len(readings_2) for bias in gyro_bias_2]
    gravity = [axis / len(readings_acc) for axis in gravity]
    grav_mag = gravity[0]**2 + gravity[1]**2 + gravity[2]**2
    grav_mag = math.sqrt(grav_mag)
    gravity = [gravity[0]/grav_mag, gravity[1]/grav_mag, gravity[2]/grav_mag]
    return gyro_bias_1, gyro_bias_2, gravity


gyro_bias_1, gyro_bias_2, gravity = calibrate(mpu_1, mpu_2, duration=10)


# Return average readings between both MPUs accounting for bias in each
def get_gyro():
    gyro_1 = [g - b for g,b in zip(mpu_1.gyro,gyro_bias_1)]
    gyro_2 = [g - b for g,b in zip(mpu_2.gyro,gyro_bias_2)]
    return [(g_1+g_2)/2 for g_1, g_2 in zip(gyro_1, gyro_2)]

# function to update Euler angle orientation estimation based on gyroscope data
def update_orientation(dt):
    global orientation
    gyro = get_gyro()
    orientation = [axis + g*dt for axis, g in zip(orientation, gyro)]
    orientation_deg = [(axis*180/math.pi)%360 for axis in orientation]
    return orientation_deg
grav_mag = 0

# Function to update gravity vector using Euler angle transformations
# DEPRECATED: Part of a solution that did not work
def update_gravity_vector():
    global orientation
    cos_x, cos_y, cos_z = [math.cos(angle) for angle in orientation]
    sin_x, sin_y, sin_z = [math.sin(angle) for angle in orientation]
    global gravity
    grav_x, grav_y, grav_z = gravity

    # apply x axis rotation transformation
    new_grav_x = grav_x
    new_grav_y = cos_x*grav_y - sin_x*grav_z
    new_grav_z = sin_x*grav_y + cos_x*grav_z

    grav_x, grav_y, grav_z = [new_grav_x, new_grav_y, new_grav_z]

    # apply y axis rotation transformation
    new_grav_x = cos_y*grav_x + sin_y*grav_z
    new_grav_y = grav_y
    new_grav_z = -sin_y*grav_x + cos_y*grav_z

    grav_x, grav_y, grav_z = [new_grav_x, new_grav_y, new_grav_z]

    # apply z axis rotation transformation
    new_grav_x = cos_z*grav_x - sin_z*grav_y
    new_grav_y = sin_z*grav_x + cos_z*grav_y
    new_grav_z = grav_z


    gravity = [new_grav_x, new_grav_y, new_grav_z]


last_time = time.monotonic()

def record(duration):
    data = []
    print("start recording path")
    start_time = time.time()
    global last_time
    while time.time() - start_time <= duration:

        current_time = time.monotonic()
        
        update_orientation(current_time - last_time)
        # update_gravity_vector()
        last_time = current_time

        accel = get_avg_acc()
        gyro = get_gyro()
        data.append((accel, gyro, orientation))
        print(time.time() - start_time, end='\r')
        time.sleep(0.01)

    print("stop recording path")
    return data

countdown(5)
data = record(20)
post_file(data)

# while(True):
#     current_time = time.monotonic()
#     orientation_deg = update_orientation(current_time - last_time)
#     # update_gravity_vector()
#     last_time = current_time
#     print(orientation, get_avg_acc())
#     time.sleep(0.1)
    
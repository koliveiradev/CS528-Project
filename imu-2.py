from time import sleep
import numpy as np
from madgwick import MadgwickFilter
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class IMU:

    def __init__(self, filter_alpha):
        self.MadgwickFilter = MadgwickFilter(1, 20/732)
        #self.mpu = MPU6050(i2c)
        self.position = np.array([0, 0, 0])
        self.filter_alpha = filter_alpha
        self.prev_accel = np.array([0, 0, 0])

    def update(self,acceleration, gyroscope):
        accel = np.array(acceleration)
        gyro = gyroscope
        q = self.MadgwickFilter.update(accel, gyro)

        # Convert quaternion to rotation matrix
        rotation_matrix = self.quat_to_rotm(q)

        # Rotate accelerometer readings into earth frame
        accel_earth = np.dot(rotation_matrix, accel)

        # Apply high-pass filter in earth frame
        filtered_accel = self.filter_alpha * (accel_earth - self.prev_accel)
        self.prev_accel = accel_earth
        return q, accel_earth # filtered_accel
    def quat_to_rotm(self, q):
        # Normalize quaternion
        q = q / np.linalg.norm(q)

        # Extract components
        w, x, y, z = q[0], q[1], q[2], q[3]

        # Create rotation matrix
        rotm = np.array([
            [1 - 2*y**2 - 2*z**2, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
            [2*x*y + 2*z*w, 1 - 2*x**2 - 2*z**2, 2*y*z - 2*x*w],
            [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x**2 - 2*y**2]
        ])

        return rotm

imu = IMU(1)
x, y, z = [], [], []
x_c, y_c, z_c =  [], [], []
x.append(0)
y.append(0)
z.append(0)

duration = 20
samples = 732
dt = duration/samples

with open('path_rows_chair_20s.csv') as file:
    i_x, i_y, i_z = 0, 0, 0
    reader = csv.reader(file)
    first_row = next(reader)
    for row in reader:
        # print(row[-4:-1])
        i_x = float(row[1])
        i_y = float(row[2])
        i_z = float(row[3])

        gyro = list(map(float, row[4:7]))
        acceleration = [i_x, i_y, i_z]

        q, filtered_accel = imu.update(acceleration,gyro)
        rotm = imu.quat_to_rotm(q)
        rotated_accel = np.dot(rotm,acceleration)

        i_x , i_y, i_z = rotated_accel
        i_x = i_x * dt
        i_x = i_x * dt
        x.append(x[-1]+i_x if x else i_x)
        i_y = i_y * dt
        i_y = i_y * dt
        y.append(y[-1]+i_y if y else i_y)

        i_z = i_z * dt
        i_z = i_z * dt
        z.append(z[-1]+i_z if z else i_z)
"""
        row = [float(i) for i in row]
        #print(filtered_accel)
        i_x = filtered_accel[0] * .01
        sleep(.01)
"""

interpolated_time_step = 2.5

n = duration/interpolated_time_step

step_size = len(x) // (n - 1)

selected_x = [val for i, val in enumerate(x) if i % step_size == 0]
selected_y = [val for i, val in enumerate(y) if i % step_size == 0]
selected_z = [val for i, val in enumerate(z) if i % step_size == 0]

# 3D scatter plot
fig1 = plt.figure()
ax = fig1.add_subplot(111, projection='3d')
ax.scatter(x, y, z)
fig1.suptitle('3D Scatter Plot')

# XY projection
fig2 = plt.figure()
ax1 = fig2.add_subplot(111)
ax1.scatter(x, y)
ax1.set_title('XY Projection')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')

# XY projection Interpolated
fig2 = plt.figure()
ax1 = fig2.add_subplot(111)
ax1.scatter(selected_x, selected_y)
ax1.set_title('XY Projection Interpolated')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')

# YZ projection
fig3 = plt.figure()
ax2 = fig3.add_subplot(111)
ax2.scatter(y, z)
ax2.set_title('YZ Projection')
ax2.set_xlabel('Y')
ax2.set_ylabel('Z')

# Zip the arrays together to form rows
rows = zip(x, y, z)



selected_rows = [row for i, row in enumerate(rows) if i % step_size == 0]


# Write the data to a CSV file
with open('path_pos_20s.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['x', 'y', 'z'])  # Write header
    writer.writerows(selected_rows)  # Write rows

plt.show()
### Introduction

### What is the project about
The project is about utilizing a gyroscope and accelerometer to track real time position and to direct a UAV quadcopter to follow the device containing the gyroscope and accelerometer in a lock step fashion.

### How are we doing this project
	Utilizing a DJI Tello and an ESP-32 and MPU6050, we are having the esp32 and MPU-6050 be a “remote sensing module” and the DJI Tello as the remote drone. We are utilizing the remote sensing module to control the DJI Tello 

### Why is the project useful
Some applications of this project include camera drones that will want to stay in some sort of lock step with an operator but use their camera to film some other object. Traditionally automatic camera tracking drones utilize their camera to keep themselves oriented and positioned relative to the subject. However this does not allow for the drone to track more than one object or to be positioned relative to one subject and to film another subject. Using a system that uses non camera data to position itself relative to some subject would allow this.

### Running
drone.py contains code for running the drone and can be run by simply connecting the the drone's wifi connection then calling python3 drone.py. As for making recordings code.py and the included config in the repo is supposed to be dragged into circuit python on the esp32 to record acceleration data.

import numpy as np

class MadgwickFilter:
    def __init__(self, beta, dt):
        self.beta = beta
        self.dt = dt
        self.q = np.array([1, 0, 0, 0])  # quaternion

    def update(self, accelerometer_measurements, gyro_measurements):
        # Normalize accelerometer measurement
        accelerometer_measurements = accelerometer_measurements / np.linalg.norm(accelerometer_measurements)

        # Gradient descent algorithm corrective step
        error_function = np.array([
            2*(self.q[1]*self.q[3] - self.q[0]*self.q[2]) - accelerometer_measurements[0],
            2*(self.q[0]*self.q[2] + self.q[1]*self.q[3]) - accelerometer_measurements[1],
            2*(0.5 - self.q[1]**2 - self.q[2]**2) - accelerometer_measurements[2]
        ])
        jacobian_matrix = np.array([
            [-2*self.q[2],  2*self.q[3], -2*self.q[0], 2*self.q[1]],
            [ 2*self.q[1],  2*self.q[0],  2*self.q[3], 2*self.q[2]],
            [     0, -4*self.q[1], -4*self.q[2], 0]
        ])
        step = np.dot(jacobian_matrix.T, error_function)
        step = step / np.linalg.norm(step)  # normalize step magnitude

        # Compute rate of change of quaternion
        q_dot = 0.5 * np.array([
            -self.q[1]*gyro_measurements[0] - self.q[2]*gyro_measurements[1] - self.q[3]*gyro_measurements[2],
            self.q[0]*gyro_measurements[0] + self.q[2]*gyro_measurements[2] - self.q[3]*gyro_measurements[1],
            self.q[0]*gyro_measurements[1] - self.q[1]*gyro_measurements[2] + self.q[3]*gyro_measurements[0],
            self.q[0]*gyro_measurements[2] + self.q[1]*gyro_measurements[1] - self.q[2]*gyro_measurements[0]
        ]) - self.beta * step.T

        # Integrate to yield quaternion
        self.q = self.q + q_dot * self.dt
        self.q = self.q / np.linalg.norm(self.q)  # normalize quaternion

        return self.q
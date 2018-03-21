import numpy as np

__author__ = "Olve Drageset, Andre Gramlich"

''' mew_t_minus_1 is the pose at the previous frame
 sigma_t_minus_1 is the covariance matrix from the previous frame
 u_t is the change in position [delta_x, delta_y, delta_theta] since t-1 according to our knowledge of our wheels
 z_t is the position as predicted by the sensor data '''


def kalman_filter(mew_t_minus_1, sigma_t_minus_1, u_t, z_t):
    # A_t is the Identity matrix because we have 0 inertia
    # B_t is the Identity matrix because our input u_t is already the delta in position due to control
    # C_t is th Identity matrix because we want to make it simple
    A_t = B_t = C_t = np.array([[1, 0, 0],
                                [0, 1, 0],
                                [0, 0, 1]])

    C_t_transpose = np.transpose(C_t)

    # Q_t is the error in the correction, R_t is the error in the prediction
    Q_t = R_t = np.array([[.04, 0, 0],
                          [0, .04, 0],
                          [0, 0, .04]])

    # PREDICTION
    # Set our predicted position according to our old position, velocity, and estimated change due to control
    mew_bar_t = np.matmul(A_t, mew_t_minus_1) + np.matmul(B_t, u_t)
    # Set our new covariance matrix based on our estimated error in u_t
    sigma_bar_t = np.matmul(np.matmul(A_t, sigma_t_minus_1), np.transpose(A_t)) + R_t

    # CORRECTION
    K_t = np.matmul(
        np.matmul(sigma_bar_t, C_t_transpose),
        np.linalg.inv(np.matmul(np.matmul(C_t, sigma_bar_t), C_t_transpose) + Q_t))
    # Correct our predicted position due to our sensor observation
    mew_t = mew_bar_t + np.matmul(K_t, z_t - np.matmul(C_t, mew_bar_t))
    # Correct our covariance matrix due to the difference between our prediction and correction due to sensor data
    sigma_t = np.matmul(np.identity(3) - np.matmul(K_t, C_t), sigma_bar_t)

    return mew_t, sigma_t  # Prediction of pose at time t, covariance at time t


mew_t_minus_1 = np.array([0, 0, 0])  # Starting position at t_0
# At the beginning we are very certain of our position, so no covariance
sigma_t_minus_1 = np.array([[0, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]])
u_t = np.array([0, 0, 0])  # Movement due to control from t_0 to t_1
z_t = np.array([10, 10, 0])  # Observed position at t_1

mew_t, sigma_t = kalman_filter(mew_t_minus_1, sigma_t_minus_1, u_t, z_t)

print(f"mew_t: {mew_t}")
print(f"sigma_t: \n{sigma_t}")

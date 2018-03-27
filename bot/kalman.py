""" Kalman Filter """
import numpy as np

__author__ = "Olve Drageset, Andre Gramlich"


def kalman_filter(mu_t_minus_1, sigma_t_minus_1, u_t, z_t):
    """
        Given as input a previous believed pose, previous covariance matrix, control input, and sensor correction on pose,
        determine a new believed pose and covariance.

        mu_t_minus_1 is the believed pose at the previous frame
        sigma_t_minus_1 is the covariance matrix from the previous frame
        u_t is the change in position [delta_x, delta_y, delta_theta] since t-1 according to our knowledge of our wheels
        z_t is the position as predicted by the sensor data
    """

    # A_t is the Identity matrix because we have 0 change in position depending on our previous position
    # B_t is the Identity matrix because our input u_t is already the delta in position due to control
    # C_t is the Identity matrix because we want to make it simple
    A_t = B_t = C_t = np.array([[1, 0, 0],
                                [0, 1, 0],
                                [0, 0, 1]])

    C_t_transpose = np.transpose(C_t)

    # Q_t is the covariance for the sensor error, R_t is for the odometry error
    Q_t = np.array([[.01, 0, 0],
                    [0, .01, 0],
                    [0, 0, .01]])
    R_t = np.array([[.05, 0, 0],
                    [0, .05, 0],
                    [0, 0, .05]])

    # PREDICTION
    # Set our predicted position according to our old position, velocity, and estimated change due to control
    mu_bar_t = np.matmul(A_t, mu_t_minus_1) + np.matmul(B_t, u_t)
    mu_bar_t[2] = mu_bar_t[2] % 360
    # Increase our covariance based on our estimated error in u_t
    sigma_bar_t = np.matmul(np.matmul(A_t, sigma_t_minus_1), np.transpose(A_t)) + R_t

    # CORRECTION
    K_t = np.matmul(
        np.matmul(sigma_bar_t, C_t_transpose),
        np.linalg.inv(np.matmul(np.matmul(C_t, sigma_bar_t), C_t_transpose) + Q_t))
    # Correct our predicted position due to our sensor observation
    mu_t = mu_bar_t + np.matmul(K_t, z_t - np.matmul(C_t, mu_bar_t))
    mu_t[2] = mu_t[2] % 360
    # Correct our covariance matrix (decrease covariance) due to the sensor data
    sigma_t = np.matmul(np.identity(3) - np.matmul(K_t, C_t), sigma_bar_t)

    return mu_t, sigma_t  # Prediction of pose at time t, covariance at time t

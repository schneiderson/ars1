import numpy as np


def kalman_filter(mew_t_minus_1, sigma_t_minus_1, u_t, z_t):
    A_t = B_t = C_t = np.array([[1, 0, 0],
                                [0, 1, 0],
                                [0, 0, 1]])
    C_t_transpose = np.transpose(C_t)

    Q_t = R_t = np.array([[.04, 0, 0],
                          [0, .04, 0],
                          [0, 0, .04]])

    # PREDICTION
    mew_bar_t = np.matmul(A_t, mew_t_minus_1) + np.matmul(B_t, u_t)
    sigma_bar_t = np.matmul(np.matmul(A_t, sigma_t_minus_1), np.transpose(A_t))

    # CORRECTION
    K_t = np.matmul(
        np.matmul(sigma_bar_t, C_t_transpose),
        np.linalg.inv(np.matmul(np.matmul(C_t, sigma_bar_t), C_t_transpose) + Q_t))
    mew_t = mew_bar_t + np.matmul(K_t, z_t - np.matmul(C_t, mew_bar_t))
    sigma_t = np.matmul(np.identity(3) - np.matmul(K_t, C_t), sigma_bar_t)

    return mew_t, sigma_t


mew_t_minus_1 = np.array([1, 1, 1])
sigma_t_minus_1 = np.array([[2, 0, 0],
                            [0, 2, 0],
                            [0, 0, 2]])
u_t = np.array([1, 1, 1])
z_t = np.array([1, 1, 1])

mew_t, sigma_t = kalman_filter(mew_t_minus_1, sigma_t_minus_1, u_t, z_t)

print(f"mew_t: {mew_t}")
print(f"sigma_t: \n{sigma_t}")

import math

''' KINEMATICS '''

'''
calculate total velocity 
 - given left and right velocity
'''
def total_velocity( vel_l , vel_r ):
    return (vel_l + vel_r) / 2


''' 
calculate rotation rate (degree/second) 
 - given left and right velocity and wheel distance (l)
'''
def rotation_rate_by_velocities( vel_l, vel_r, wheel_dist = 1 ):
    # fail if wheel distance is zero
    assert wheel_dist != 0, 'Wheel distance cannot be 0!'
    
    rotationRate = (vel_r - vel_l) / wheel_dist
    return rotationRate


''' 
calculate distance to ICC (degree/second)
'''
def ICC_dist( vel_l, vel_r, wheel_dist = 1 ):
    # fail if wheel distance is zero
    assert wheel_dist != 0, 'Wheel distance cannot be 0!'

    # avoid division by zero (return infinity)
    if( vel_l == vel_r ):
        return math.inf
    else:
        R = ( wheel_dist / 2 ) * (vel_r + vel_l) / (vel_r - vel_l)
        return R


''' 
calculate ICC coordinates (x, y)
'''
def ICC_coordinates( pos_x, pos_y, angle, vel_l, vel_r, wheel_dist = 1 ):
    icc_dist = ICC_dist( vel_l, vel_r, wheel_dist )

    # if icc_dist isn't infinity, calculate ICC position
    if( icc_dist != math.inf ):
        rad = math.radians(angle)
        x = pos_x - icc_dist * math.sin(rad)
        y = pos_y + icc_dist * math.cos(rad)
        return x, y
    else:
        return None, None



''' 
calculate new bot coordinates (x, y)
'''
def bot_calc_coordinate( pos_x, pos_y, angle, vel_l, vel_r, delta_t = 1, wheel_dist = 1 ):
    x_icc, y_icc = ICC_coordinates( pos_x, pos_y, angle, vel_l, vel_r, wheel_dist )

    # velocities are equal (angle doesn't change)
    if( x_icc is None or y_icc is None ):
        # get total velocity and scale it by delta_t
        t_vel = total_velocity( vel_l, vel_r ) * delta_t
        
        # rotate unit vector, multiply by velocity and add current position
        rad = math.radians(angle)
        x_new = math.cos(rad) * t_vel + pos_x
        y_new = math.sin(rad) * t_vel + pos_y

        return x_new, y_new, angle

   # velocities are different (angle will change)
    else:
        # scale rotation by delta_t
        rr = rotation_rate_by_velocities( vel_l, vel_r, wheel_dist ) * 2 * math.pi * delta_t

        # calc new position
        x_tmp = pos_x - x_icc
        y_tmp = pos_y - y_icc
        x_new = ( x_tmp * math.cos(rr) ) + ( y_tmp * -math.sin(rr) ) + x_icc
        y_new = ( x_tmp * math.sin(rr) ) + ( y_tmp * math.cos(rr) ) + y_icc

        # calc new angle
        angle_new = ( angle + math.degrees(rr) ) % 360

        return x_new, y_new, angle_new 

''' ROBOT MODULE '''
import math
from bot import kinematics as kin
from bot import trigonometry as tri
from bot import beacon as bc

__author__ = 'Camiel Kerkhofs'

COLLISION_TOLERANCE = 0.001
BEACON_COLLISION_TOLERANCE = 5

class Robot:
    def __init__(self):
        
        # Robot position
        self.radius = 30
        self.initial_posx = self.posx = 400.0
        self.initial_posy = self.posy = 175.0
        self.initial_angle = self.angle = 0
        
        # Velocity
        self.vel_left = 0
        self.vel_right = 0

        """
         Infrared sensors
         For each sensor we have (A, B, C) where:
            - A is the linear distance measure between 0 and sensor_max
            - B is the transformed distance measure given by (sensor_max - A) ^ dist_transformation_factor
            - C is the position (x,y) of the intersection
        """
        self.sensor_max = 500
        self.dist_transformation_factor = 2
        self.sensors = [(0, 0, (self.posx, self.posy))] * 12
        self.connected_beacons = []
        self.num_collisions = 0
        self.max_activation = self.sensor_max ** self.dist_transformation_factor

    def reset(self):
        self.posx = self.initial_posx
        self.posy = self.initial_posy
        self.angle = self.initial_angle

        self.vel_left = 0
        self.vel_right = 0

        self.sensors = [(0, 0, (self.posx, self.posy))] * 12
        self.connected_beacons = []
        self.num_collisions = 0

    def set_robot_initial_position(self, x, y, angle):
        self.initial_posx = x
        self.initial_posy = y
        self.initial_angle = angle

    def set_robot_position(self, x, y, angle):
        self.posx = x
        self.posy = y
        self.angle = angle

    def set_velocity(self, left, right):
        self.vel_left = left
        self.vel_right = right

    def move_robot(self, delta_time):
        """
            move the robot using the given delta time
            vel_right and vel_left are switched on purpose to compensate for the pygame coordinate system (y-axis is flipped, with 0,0 point being top left)
        """

        if delta_time >= self.radius*10:
            # Delta_t exceeds robot radius; wall detection becomes unreliable at this point
            raise ValueError('movement delta_time of ' + str(delta_time) + 'ms exceeds robot radius. This might be caused by a high time_dilation or a screen drag. (Do not drag the screen!)')
        
        left_velocity = float(format(self.vel_right, '.5f'))
        right_velocity = float(format(self.vel_left, '.5f'))
        pos = kin.bot_calc_coordinate(self.posx, self.posy, self.angle, left_velocity, right_velocity,
                                      delta_time / 10, self.radius * 2)
        self.set_robot_position(pos[0], pos[1], pos[2])

    def update_beacons(self, beacons, walls, display=None):
        """
            Update all beacon connections given a set of beacons and a set of walls
        """

        # Find beacons that are connected to the robot by a direct line of sight
        connected_beacons = []  # [beacon_x, beacon_y, distance, bearing]
        for beacon in beacons:
            # Check collision points for each wall
            connected = True
            for wall in walls:
                intersect = tri.line_intersect(wall[0], wall[1], (self.posx, self.posy), (beacon.x, beacon.y), COLLISION_TOLERANCE)
                if intersect:
                    # Determine beacon distance to intersect
                    distance = tri.line_distance((beacon.x, beacon.y), (intersect[0], intersect[1]))
                    if distance > BEACON_COLLISION_TOLERANCE:
                        #print('Beacon ' + str(beacon) + ' intersects with wall ' + str(wall) + ' at point ' + str(intersect) + '. distance: ' + str(distance))
                        connected = False
            if connected:
                # Determine distance+bearing from robot to beacon
                distance = tri.line_distance((beacon.x, beacon.y), (self.posx, self.posy))
                bearing = tri.line_angle((beacon.x, beacon.y), (self.posx, self.posy))

                # Make bearing relative to robots angle
                # Subtract robots actual angle from the bearing because the sensor can not know the real beacon angle
                bearing = (bearing - self.angle) % 360

                # Append the beacon to the list of connected beacons for future reference
                connected_beacons.append(bc.Beacon(beacon.x, beacon.y, distance, bearing))
        self.connected_beacons = connected_beacons

        X = tri.triangulate_beacons(connected_beacons, display, self)
        return X

    def update_sensors(self, walls):
        """
            Update all infrared sensor values given a set of bounding lines (walls)
        """

        closest_transformed = 0
        for index, sensor in enumerate(self.sensors):
            # Determine current sensor endpoint
            closest_collision = self.sensor_max
            sensor_angle = ((360 / len(self.sensors)) * index)
            angle = (self.angle + sensor_angle) % 360
            sensor_end = tri.line_endpoint((self.posx, self.posy), angle, closest_collision)
            intersect_wall = 0
        
            # Check collision points for each wall
            for wall in walls:
                intersect = tri.line_intersect(wall[0], wall[1], (self.posx, self.posy), sensor_end, COLLISION_TOLERANCE)
            
                if intersect:
                    # Determine distance to intersect
                    distance = tri.line_distance((self.posx, self.posy), (intersect[0], intersect[1]))
                    if distance < closest_collision:
                        closest_collision = distance
                        sensor_end = intersect
                        intersect_wall = wall
        
            # Transform linear distance measure and update sensor value
            transformed_distance = (self.sensor_max - closest_collision) ** self.dist_transformation_factor
            self.sensors[index] = [closest_collision, transformed_distance, sensor_end]
            if transformed_distance > closest_transformed:
                closest_transformed = transformed_distance
        
            # Handle wall collisions, apply motion only parallel to wall, rest motion perpendicular to wall
            if closest_collision < self.radius - COLLISION_TOLERANCE:
                self.num_collisions += 1

                # The robot is moved back along the angle of the current (infringing) sensor using the illegal distance
                illegal_distance = (self.radius - closest_collision) + self.radius
                corrected_position = tri.line_endpoint((sensor_end[0], sensor_end[1]), angle, illegal_distance)
                self.set_robot_position(corrected_position[0], corrected_position[1], self.angle)

                # Restart sensor update to find potential sensors that might conflict with the new position
                self.update_sensors(walls)

        return closest_transformed

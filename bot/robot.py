''' ROBOT MODULE '''
import math
from bot import kinematics as kin
from bot import trilateration as tri
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
                intersect = self.find_line_intersect(wall[0], wall[1], (self.posx, self.posy), (beacon.x, beacon.y))
                if intersect:
                    # Determine beacon distance to intersect
                    distance = math.sqrt((intersect[0] - beacon.x) ** 2 + (intersect[1] - beacon.y) ** 2)
                    if distance > BEACON_COLLISION_TOLERANCE:
                        #print('Beacon ' + str(beacon) + ' intersects with wall ' + str(wall) + ' at point ' + str(intersect) + '. distance: ' + str(distance))
                        connected = False
            if connected:
                # Determine distance+bearing to beacon and save beacon as connected
                distance = math.sqrt((self.posx - beacon.x) ** 2 + (self.posy - beacon.y) ** 2)
                bearing = math.atan2((beacon.y-self.posy), (beacon.x-self.posx))*180.0/math.pi
                bearing = (bearing + 360) % 360

                # Make bearing relative to robots angle
                # Subtract robots actual angle from the bearing because the sensor can not know the actual beacon angle
                bearing = (bearing - self.angle) % 360

                # The beacons X and Y position are saved only for rendering purposes.
                # The algorithm only uses the distance and bearing for triangulation
                connected_beacons.append(bc.Beacon(beacon.x, beacon.y, distance, bearing))
        self.connected_beacons = connected_beacons

        x = tri.triangulate(connected_beacons, display)

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
            theta_rad = math.radians(angle)
            sensor_end = \
                self.posx + closest_collision * math.cos(theta_rad), \
                self.posy + closest_collision * math.sin(theta_rad)
            intersect_wall = 0
        
            # Check collision points for each wall
            for wall in walls:
                intersect = self.find_line_intersect(wall[0], wall[1], (self.posx, self.posy), sensor_end)
            
                if intersect:
                    # Determine distance to intersect
                    distance = math.sqrt((intersect[0] - self.posx) ** 2 + (intersect[1] - self.posy) ** 2)
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
                corrected_position = sensor_end[0] - illegal_distance * math.cos(theta_rad), \
                                     sensor_end[1] - illegal_distance * math.sin(theta_rad)
                self.set_robot_position(corrected_position[0], corrected_position[1], self.angle)

                # Restart sensor update to find potential sensors that might conflict with the new position
                self.update_sensors(walls)
            
                # TODO: motion parallel from wall continues normally, but should be slown down by a weight to discourage 'pushing' the wall
                # xDiff = intersect_wall[1][0] - intersect_wall[0][0]
                # yDiff = intersect_wall[1][1] - intersect_wall[0][1]
                # wall_angle = math.degrees(math.atan2(yDiff, xDiff))
        return closest_transformed
                
    def find_line_intersect(self, a_p1, a_p2, b_p1, b_p2):
        """
            Finds the intersection between two lines a and b defined by their respective endpoints p1 and p2
        """
    
        # Check if lines intersect
        if a_p1[0] > b_p1[0] and a_p1[0] > b_p2[0] and a_p2[0] > b_p1[0] and a_p2[0] > b_p2[0]: return False
        if a_p1[0] < b_p1[0] and a_p1[0] < b_p2[0] and a_p2[0] < b_p1[0] and a_p2[0] < b_p2[0]: return False
        if a_p1[1] > b_p1[1] and a_p1[1] > b_p2[1] and a_p2[1] > b_p1[1] and a_p2[1] > b_p2[1]: return False
        if a_p1[1] < b_p1[1] and a_p1[1] < b_p2[1] and a_p2[1] < b_p1[1] and a_p2[1] < b_p2[1]: return False
    
        # Get diffs along each axis
        x_diff = (a_p1[0] - a_p2[0], b_p1[0] - b_p2[0])
        y_diff = (a_p1[1] - a_p2[1], b_p1[1] - b_p2[1])
    
        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]
    
        # Find the intersection
        div = det(x_diff, y_diff)
        if div == 0: return False
        d = (det(*(a_p1, a_p2)), det(*(b_p1, b_p2)))
        x = det(d, x_diff) / div
        y = det(d, y_diff) / div
    
        # Check if intersection exceeds the segments
        if x < min(a_p1[0], a_p2[0]) - COLLISION_TOLERANCE: return False
        if x > max(a_p1[0], a_p2[0]) + COLLISION_TOLERANCE: return False
        if y < min(a_p1[1], a_p2[1]) - COLLISION_TOLERANCE: return False
        if y > max(a_p1[1], a_p2[1]) + COLLISION_TOLERANCE: return False
        if x < min(b_p1[0], b_p2[0]) - COLLISION_TOLERANCE: return False
        if x > max(b_p1[0], b_p2[0]) + COLLISION_TOLERANCE: return False
        if y < min(b_p1[1], b_p2[1]) - COLLISION_TOLERANCE: return False
        if y > max(b_p1[1], b_p2[1]) + COLLISION_TOLERANCE: return False
    
        return x, y
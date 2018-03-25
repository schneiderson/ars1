''' TRIGONOMETRY MODULE '''
import math

__author__ = 'Camiel Kerkhofs'


def triangulate_beacons(beacons):
    """
        Given a set of beacons and the distance to each beacon, finds the point where they all intersect.

        We assume the real position of each beacon is known from an internal map.
        All other information is relative to the robot and is noisy (distance and bearing to each beacon).
            input: [(beacon_1.x, beacon_1.y, bearing, distance), ..., (beacon_n.x, beacon_n.y, bearing, distance)]

        By triangulating the beacons using their known location and the robots orientation towards them
        we can find a noisy estimate of the real x, y and theta values of the robot.
            returns tuple (x, y, theta)
    """

    if len(beacons) < 3:
        return False

    # Triangulate connected beacons
    inner_points = []
    for index, beacon in enumerate(beacons):
        # Triangulate the beacon with all other beacons
        for index_2, beacon_2 in enumerate(beacons):
            if index_2 > index:
                # Distance between beacon 1 and robot
                d1 = beacon.distance

                # Distance between beacon 2 and robot
                d2 = beacon_2.distance

                # Angle between d1 and d2 relative to the robot
                angle = abs(beacon_2.bearing - beacon.bearing)
                if angle > 180:
                    angle = 360-angle

                # Distance between the 2 beacons
                a = law_of_cosines(d1, d2, angle)

                # Robot position relative to the 2 beacons
                x = (a**2 + d1**2 - d2**2) / (2*a)
                y = math.sqrt(d1**2 - x**2)

                # We assume the position of the beacons is derived from an internal map.
                # We use the position of beacon 1 and beacon 2 to get the angle between these beacons
                # Real angle of the 2 beacons
                beacon_angle = line_angle((beacon_2.x, beacon_2.y), (beacon.x, beacon.y))

                # Get the 2 possible robot positions from x, y, beacon1 and the angle between the 2 beacons
                x_endpoint = line_endpoint((beacon.x, beacon.y), beacon_angle, x)
                xy_endpoint_pos = line_endpoint(x_endpoint, beacon_angle+90, y)
                xy_endpoint_neg = line_endpoint(x_endpoint, beacon_angle-90, y)

                # Append the possible endpoints to the list
                inner_points.append([(round(xy_endpoint_pos[0]), round(xy_endpoint_pos[1])), (round(xy_endpoint_neg[0]), round(xy_endpoint_neg[1]))])

    # Filter all possible inner points.
    # Determine whether X or X' is valid given all other beacon observations (this is why we need at least 3 beacons)
    believe_point = None
    believe_points = []
    for i in range(len(inner_points)):

        # First loop execution: find initial believe point using the first 2 beacon pairs
        if len(believe_points) == 0 and i+1 < len(inner_points):
            p1 = inner_points[i]
            p2 = inner_points[i+1]

            # The 2 points that are closest to each other in the 2x2 matrix are the correct X/X' point
            dist_diffs = [
                line_distance(p1[0], p2[0]),
                line_distance(p1[0], p2[1]),
                line_distance(p1[1], p2[0]),
                line_distance(p1[1], p2[1])
            ]
            temp = dist_diffs.index(min(dist_diffs))
            if temp < 2:
                believe_point = p1[0]
                believe_points.append(p1[0])
                if temp == 0:
                    believe_points.append(p2[0])
                elif temp == 1:
                    believe_points.append(p2[1])
            elif temp < 4:
                believe_point = p1[1]
                believe_points.append(p1[1])
                if temp == 2:
                    believe_points.append(p2[0])
                elif temp == 3:
                    believe_points.append(p2[1])

        # Compare other beacon observations to the believe point
        else:
            if line_distance(inner_points[i][0], believe_point) < line_distance(inner_points[i][1], believe_point):
                believe_points.append(inner_points[i][0])
            else:
                believe_points.append(inner_points[i][1])

    # Average the believe points
    # Due to noisy distance measures, our position estimates can vary.
    # We take the middle of this area; more beacons = higher accuracy
    center = get_polygon_center(believe_points)

    # Get the robots real angle using the known beacons and the calculated robot position
    theta_real = line_angle((beacons[0].x, beacons[0].y), (center[0], center[1]))  # angle between beacon 1 and robot
    theta = (theta_real - beacons[0].bearing) % 360  # Actual robot pose given its relative angle to beacon 1

    return (center[0], center[1], theta)


def line_intersect(a_p1, a_p2, b_p1, b_p2, tolerance = 0.001):
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
    if x < min(a_p1[0], a_p2[0]) - tolerance: return False
    if x > max(a_p1[0], a_p2[0]) + tolerance: return False
    if y < min(a_p1[1], a_p2[1]) - tolerance: return False
    if y > max(a_p1[1], a_p2[1]) + tolerance: return False
    if x < min(b_p1[0], b_p2[0]) - tolerance: return False
    if x > max(b_p1[0], b_p2[0]) + tolerance: return False
    if y < min(b_p1[1], b_p2[1]) - tolerance: return False
    if y > max(b_p1[1], b_p2[1]) + tolerance: return False

    return x, y


def line_endpoint(start, angle, distance):
    """
        Return the endpoint of a line that goes from point 'start' at angle 'angle' for distance 'distance'
    """
    x = start[0] + distance * math.cos(math.radians(angle))
    y = start[1] + distance * math.sin(math.radians(angle))
    return  x, y


def law_of_sines(a, b, c):
    """
        Return the angle of the corner opposite to side c in a triangle given by its 3 sides a, b and c (Law of sines)
    """
    return math.degrees(math.acos((c**2 - b**2 - a**2)/(-2.0 * a * b)))


def law_of_cosines(a, b, angle):
    """
        Return the side of a triangle given its sides a, b and the angle between them (Law of cosines)
    """
    return math.sqrt(
                    a**2 +
                    b**2 -
                    2*a*b*math.cos(math.radians(angle))
                )


def line_distance(p1, p2):
    """
        Return the distance between 2 points p1 and p2
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def line_angle(p1, p2):
    """
        Return the angle of the line that goes from p1 to p2
            Clockwise in pygame window
            Counter clockwise in xy-space
    """
    angle = math.atan2((p1[1]-p2[1]), (p1[0]-p2[0])) * 180.0/math.pi
    return (angle + 360) % 360


def get_polygon_center(points):
    """
        Returns the center of a set of points
    """
    center = [0, 0]
    num = len(points)
    for i in range(num):
        center[0] += points[i][0]
        center[1] += points[i][1]
    center[0] /= num
    center[1] /= num
    return center

''' TRIGONOMETRY MODULE '''
import math
import pygame

__author__ = 'Camiel Kerkhofs'

TRILATERATION_TOLLERANCE = 0.00001

def triangulate_beacons(beacons, display):
    """
        Given a set of beacons amd the distance to each beacon, finds the point where they all intersect
    """

    # Temp: only use 3 beacons
    beacons = beacons[:3]

    # Triangulate connected beacons
    inner_points = []
    for index, beacon in enumerate(beacons):
        # triangulate with all other beacons
        for index_2, beacon_2 in enumerate(beacons):
            if index_2 > index:
                # distance between beacon 1 and robot
                d1 = beacon.distance

                # distance between beaacon 2 and robot
                d2 = beacon_2.distance

                # distance between 2 beacons (uses the bearing and distance of each beacon; law of cosines)
                angle = abs(beacon_2.bearing - beacon.bearing)
                if angle>180:
                    angle = 360-angle
                a = law_of_cosines(d1, d2, angle)

                x = (a**2 + d1**2 - d2**2) / (2*a)
                y = math.sqrt(d1**2 - x**2)

                # TODO: Normalize point to 0 degrees bearing using the known position of beacon 1 and beacon 2
                theta = 0

                # Angle between the 2 beacons
                beacon_angle = line_angle((beacon.x, beacon.y), (beacon_2.x, beacon_2.y)) % 90

                # Angle from beacon 1 to robot relative to the 2 beacons
                beacon_robot_angle = law_of_sines(d1, x, y)

                # We assume the position of the beacons is derived from an internal map.
                # We use the position of beacon 1 and beacon 2 to get the angle between these beacons
                # Using the law of cosines, solve for angle gamma and subtract this from the angle between the beacons to get the angle to the x axis

                #Temp:
                # if display is not None and index==0 and index_2==1:
                #     print('drawing temp line for beacon0 at ' + str((beacon.x, beacon.y, beacon.bearing)) + ' and beacon1 at ' + str((beacon_2.x, beacon_2.y, beacon_2.bearing)))
                #     endpoint = line_endpoint((beacon.x, beacon.y), 0, x)
                #     pygame.draw.line(display, (255,0,0), (beacon.x,beacon.y), endpoint, 1)
                #     # pygame.draw.line(display, (255,0,0), (beacon.x,beacon.y), (10,10), y)

                #TODO: inner points are relative to beacon 1, how do we combine these beacons


                inner_points.append([x, y, theta])

    #TODO: avarage the inner points..


    return inner_points

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
        Return the side of a triangle given its sides a, b and its angle (Law of cosines)
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

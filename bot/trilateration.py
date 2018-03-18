''' TRILATERATION MODULE '''
import math
import numpy

__author__ = 'Camiel Kerkhofs'

TRILATERATION_TOLLERANCE = 0.00001

def triangulate(beacons):
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
                a = math.sqrt(
                    d1**2 +
                    d2**2 -
                    2*d1*d2*math.cos(math.radians(angle))
                )


                x = (a**2 + d1**2 - d2**2) / (2*a)
                y = math.sqrt(d1**2 - x**2)

                # TODO: Normalize point to 0 degrees bearing
                #TODO: inner points are relative to beacon 1, how do we combine these beacons


                inner_points.append([x, y])

    #TODO: combine these inner points..

    return inner_points

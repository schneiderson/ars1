''' BEACON MODULE '''

__author__ = 'Camiel Kerkhofs'

class Beacon(object):

    def __init__(self, x, y, dist=None, bearing=None):
        self.x = x
        self.y = y
        self.distance = dist
        self.bearing = bearing
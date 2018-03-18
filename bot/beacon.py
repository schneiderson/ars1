''' BEACON MODULE '''

__author__ = 'Camiel Kerkhofs'

class Beacon(object):

    def __init__(self, x, y, dist=None, bearing=None):
        self.x = x  # Only used for renderering purposes
        self.y = y  # Only used for rendering purposes
        self.distance = dist
        self.bearing = bearing
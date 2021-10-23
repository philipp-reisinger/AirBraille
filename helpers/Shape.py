import math


class Point2D(object):

    def __init__(self, x: float, y: float):
        """
        Inits a 2d point.
        :param x: the x coordinate of the point
        :param y: the y coordinate of the point
        """
        self.x = x
        self.y = y

    def distance_to(self, other) -> float:
        """
        Calculates the distance between this point and the other
        :param other: the other point to which the distance should be calculated
        :return: The distance between this point and the other.
        """
        return math.dist((self.x, self.y), (other.x, other.y))

    def __str__(self):
        return 'Point: ' + '(x: ' + self.x.__str__() + ', y: ' + self.y.__str__() + ')'


def middle_point(point_a: Point2D, point_b: Point2D) -> Point2D:
    """
    Finds the middle point between two 2d points.
    :param point_a: The point a.
    :param point_b: The point b.
    :return: The point in the middle of the points a and b.
    """
    x = (point_a.x + point_b.x) / 2
    y = (point_a.y + point_b.y) / 2
    return Point2D(x, y)


class Circle(object):

    def __init__(self, point: Point2D, radius: float):
        """
        Inits a circle object.
        :param point: The middle point of the circle.
        :param radius: The circle's radius.
        """
        self.x = point.x
        self.y = point.y
        self.point = point
        self.r = radius
        self.d = 2 * self.r

    # based upon: https://stackoverflow.com/a/481153
    def contains(self, point: Point2D) -> bool:
        """
        Determines whether a point is inside the circle.
        :param point: The point to be checked whether to be inside the circle
        :return: True, if inside, False otherwise
        """
        return point.distance_to(self.point) <= self.r

    def area(self) -> float:
        """
        Calculates the area of the circle.
        :return: the circle's area.
        """
        return (self.r ** 2) * math.pi

    def circumference(self) -> float:
        """
        Calculates the circumference of the circle.
        :return: The circle's circumference.
        """
        return self.d * math.pi

    def __str__(self):
        return f"""Circle: x = {self.x} + y = {self.y} - radius = {self.r}"""

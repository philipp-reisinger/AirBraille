class HandCoordinateType:
    # this class holds the coordinate values used in the MediaPipe framework

    WRIST = 0

    # thumb
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4

    # index finger
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8

    # middle finger
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12

    # ring finger
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16

    # pinky finger
    PINKY_FINGER_MCP = 17
    PINKY_FINGER_PIP = 18
    PINKY_FINGER_DIP = 19
    PINKY_FINGER_TIP = 20

    # indices for access
    CMC = 0
    MCP = 0
    IP = 1
    PIP = 1
    DIP = 2
    TIP = 3

    # keys are the number
    def get_as_dictionary(self) -> dict:
        """
        maps all coordinates to its values

        :return: the coordinates in a dictionary, where the index is the key
        """
        return {
            0: self.WRIST,
            1: self.THUMB_CMC,
            2: self.THUMB_MCP,
            3: self.THUMB_IP,
            4: self.THUMB_TIP,
            5: self.INDEX_FINGER_MCP,
            6: self.INDEX_FINGER_PIP,
            7: self.INDEX_FINGER_DIP,
            8: self.INDEX_FINGER_TIP,
            9: self.MIDDLE_FINGER_MCP,
            10: self.MIDDLE_FINGER_PIP,
            11: self.MIDDLE_FINGER_DIP,
            12: self.MIDDLE_FINGER_TIP,
            13: self.RING_FINGER_MCP,
            14: self.RING_FINGER_PIP,
            15: self.RING_FINGER_DIP,
            16: self.RING_FINGER_TIP,
            17: self.PINKY_FINGER_MCP,
            18: self.PINKY_FINGER_PIP,
            19: self.PINKY_FINGER_DIP,
            20: self.PINKY_FINGER_TIP
        }


class HandCoordinate(object):

    def __init__(self, x: float, y: float, z: float, coord_type: HandCoordinateType):
        """
        constructor of a hand coordinate object, that holds the coordinates x, y, z
        as well as the type of the coordinate

        :param x: the x coordinate of the hand's coordinate
        :param y: the y coordinate of the hand's coordinate
        :param z: the z coordinate of the hand's coordinate
        :param coord_type: the type of the coordinate
        """
        self.x = x
        self.y = y
        self.z = z
        self.type = coord_type

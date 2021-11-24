class Settings(object):

    # debugging options
    DEBUG: bool = True
    PRINT_HANDS: bool = False
    PRINT_EVAL: bool = False
    PRINT_FINGER: bool = False
    PRINT_ANGLE: bool = False

    # modes:
    CONFIRM_INPUT: bool = True
    INVERT: bool = False

    THRESHOLD: int = 10  # number of images, that are collected in one take
    ANGLE: int = 120  # the angle, at which the finger is stretched or not

    # finger is braille point:
    #################
    #               #
    #   1       4   #
    #   2       5   #
    #   3       6   #
    #   7       8   #
    #               #
    #################

    # left hand's finger indices
    LEFT_THUMB: int = 0
    LEFT_INDEX: int = 1
    LEFT_MIDDLE: int = 2
    LEFT_RING: int = 3
    LEFT_KINKY: int = 7

    # right hand's finger indices
    RIGHT_THUMB: int = 9
    RIGHT_INDEX: int = 4
    RIGHT_MIDDLE: int = 5
    RIGHT_RING: int = 6
    RIGHT_KINKY: int = 8

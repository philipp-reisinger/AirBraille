from protobuf_to_dict import protobuf_to_dict
from typing import Tuple, List
import numpy as np

from helpers.Shape import *
from hand.Coordinate import *
from settings.Settings import *


class HandPair(object):

    NOT_TWO_HANDS: str = "Keine zwei Hände im Bild!"
    TWO_SAME_HANDS: str = "Zwei gleiche Hände!"

    def __init__(self):
        """
        constructor for a hand pair, holds a left and right hand
        """
        self.left_hand = None
        self.right_hand = None

    def is_valid(self, result_multi_handedness: list) -> Tuple[bool, str]:
        """
        Checks if the detection results are a valid handpair
        A handpair is valid,
            iff there are exactly two hands
            and one hand is a left hand
            and the other hand is a right hand
        :param result_multi_handedness: the detection results
        :return: Tuple[true, '']: iff the detection results represent a valid handpair
                 Tuple[false, error message]: iff the result is an invalid pair of hands,
                                              the error message tells, whether two identical
                                              hands are visible, or not two hands were detected.
        """

        if len(result_multi_handedness) != 2:
            return False, self.NOT_TWO_HANDS

        # convert from protobuf message to python's dictionary
        # https://github.com/google/mediapipe/issues/1374

        dict_hand_a = protobuf_to_dict(result_multi_handedness[0])
        dict_hand_b = protobuf_to_dict(result_multi_handedness[1])

        # get each hand's label
        label_hand_a = dict_hand_a['classification'][0]['label']
        label_hand_b = dict_hand_b['classification'][0]['label']

        if label_hand_a == label_hand_b:
            return False, self.TWO_SAME_HANDS

        return True, ''

    def define_hands(self, result):
        """
        Inits left and right hand of the hand pair.
        :param result: The detection results
        :return:
        """
        dict_hand_a = protobuf_to_dict(result.multi_handedness[0])
        landmarks_a = protobuf_to_dict(result.multi_hand_landmarks[0])['landmark']

        if len(result.multi_handedness) == 2:
            dict_hand_b = protobuf_to_dict(result.multi_handedness[1])
            landmarks_b = protobuf_to_dict(result.multi_hand_landmarks[1])['landmark']
        else:
            dict_hand_b = None

        # dictionary = dict['classification'] # -> is a list
        # len(dictionary) # is always 1, so -> dictionary[0]
        # dictionary[0] -> is a dict
        # dictionary[0] keys are: index score label

        label_a = dict_hand_a['classification'][0]['label']
        index_a = dict_hand_a['classification'][0]['index']
        score_a = dict_hand_a['classification'][0]['score']

        if dict_hand_b is not None:
            label_b = dict_hand_b['classification'][0]['label']
            index_b = dict_hand_b['classification'][0]['index']
            score_b = dict_hand_b['classification'][0]['score']

        if label_a == 'Right':
            self.right_hand = Hand(index_a, score_a, label_a, landmarks_a)
            if dict_hand_b is not None:
                self.left_hand = Hand(index_b, score_b, label_b, landmarks_b)
            else:
                self.left_hand = None
        else:
            self.left_hand = Hand(index_a, score_a, label_a, landmarks_a)
            if dict_hand_b is not None:
                self.right_hand = Hand(index_b, score_b, label_b, landmarks_b)
            else:
                self.right_hand = None

    def evaluate(self) -> str:
        """
        evaluates the current handpair and maps it to the corresponding braille points
        :return: a string, that contains all braille points (order ascending), that the handpair represents
        """
        
        result = dict()
        # init dict to default: all fingers not stretched
        for i in range(0, 9):
            result[i] = False

        if self.left_hand is not None:
            left_hand_eval = self.left_hand.evaluate()
            for finger_type in left_hand_eval:
                if finger_type is _FingerType.THUMB:
                    result[Settings.LEFT_THUMB] = left_hand_eval[finger_type]
                elif finger_type is _FingerType.INDEX_FINGER:
                    result[Settings.LEFT_INDEX] = left_hand_eval[finger_type]
                elif finger_type is _FingerType.MIDDLE_FINGER:
                    result[Settings.LEFT_MIDDLE] = left_hand_eval[finger_type]
                elif finger_type is _FingerType.RING_FINGER:
                    result[Settings.LEFT_RING] = left_hand_eval[finger_type]
                else:
                    result[Settings.LEFT_KINKY] = left_hand_eval[finger_type]

        if self.right_hand is not None:
            right_hand_eval = self.right_hand.evaluate()
            for finger_type in right_hand_eval:
                if finger_type is _FingerType.THUMB:
                    result[Settings.RIGHT_THUMB] = right_hand_eval[finger_type]
                elif finger_type is _FingerType.INDEX_FINGER:
                    result[Settings.RIGHT_INDEX] = right_hand_eval[finger_type]
                elif finger_type is _FingerType.MIDDLE_FINGER:
                    result[Settings.RIGHT_MIDDLE] = right_hand_eval[finger_type]
                elif finger_type is _FingerType.RING_FINGER:
                    result[Settings.RIGHT_RING] = right_hand_eval[finger_type]
                else:
                    result[Settings.RIGHT_KINKY] = right_hand_eval[finger_type]

        return self._map_to_string(result)

    def _map_to_string(self, r_dict: dict) -> str:
        """
        maps the dictionary to a string, that represents the braille dots.
        The Settings.INVERT variable determines, if stretched fingers correspond
        to active braille dots and vice versa.
        :param r_dict: the dictionary, that holds at key k the boolean value,
                       that tells whether this finger is stretched (true) or not
        :return: the string of all braille cells
        """
        
        if Settings.INVERT:
            result = '0123456789'
            for key_index in r_dict:
                if r_dict[key_index]:
                    result = result.replace(str(key_index), "")
            return result
        else:
            result = ''
            for key_index in r_dict:
                if r_dict[key_index]:
                    result += str(key_index)
            return result


class Finger(object):

    # last two parameters are needed to say if the thumb is stretched or not
    def __init__(self, finger_type: int, landmarks: list, wrist, index_finger=None, kinky_finger=None):
        """

        :param finger_type: the type of the finger
        :param landmarks: the landmarks / coordinates of the finger
        :param wrist: the wrist of the hand
        :param index_finger: optional, only needed if the finger is a thumb, the index finger of the same hand
        :param kinky_finger: optional, only needed if the finger is a thumb, the kinky finger of the same hand
        """
        self.type = finger_type
        self.landmarks = landmarks
        self.is_thumb = self._is_thumb()
        self.wrist = wrist

        # per default set to None, except it is a thumb
        self.index_finger = index_finger
        self.kinky_finger = kinky_finger

    def _is_thumb(self) -> bool:
        """
        Tells, if the current finger is a humb
        :return: whether the finger is a thumb (true) or not (false)
        """
        if self.type == _FingerType.THUMB:
            return True
        else:
            return False

    def _coordinates(self, coord_index: int) -> dict:
        """
        Provides access to the index of the landmark
        :param coord_index: The index of the landmark that wants to be returned
        :return: the
        """
        return self.landmarks[coord_index]

    def is_stretched(self) -> bool:
        """
        Determines whether a finger is stretched or not. Depends on the finger type:
            thumb: For determining, whether the thumb is stretched or not, there will be checked,
            if the thumb's tip (only x and y coordinate of interest) are inside a 'circle' that is
            described by the middle point of the kinky and index finger and as a radius the distance of both
            other fingers mcp acts, whereas the distance is divided by 1.5 before, in order to let the circle
            be similar placed like the hand's palm.
            other: the cosine angle of two vectors will be evaluated. The two vectors are:
                mcp->tip: the vector from the finger's mcp point to the finger's tip point
                mcp->wrist: the vector from the finger's mcp point to the wrist's point
        :return: whether a finger a stretched (true) or not (false)
        """

        x_coord_tip = self._coordinates(HandCoordinateType.TIP)['x'] * 100
        y_coord_tip = self._coordinates(HandCoordinateType.TIP)['y'] * 100
        if self._is_thumb():
            # kinky finger's mcp point
            x_coord_kinky_mcp = self.kinky_finger._coordinates(HandCoordinateType.MCP)['x'] * 100
            y_coord_kinky_mcp = self.kinky_finger._coordinates(HandCoordinateType.MCP)['y'] * 100
            kinky_point = Point2D(x_coord_kinky_mcp, y_coord_kinky_mcp)

            # index finger's mcp point
            x_coord_index_mcp = self.index_finger._coordinates(HandCoordinateType.MCP)['x'] * 100
            y_coord_index_mcp = self.index_finger._coordinates(HandCoordinateType.MCP)['y'] * 100
            index_point = Point2D(x_coord_index_mcp, y_coord_index_mcp)

            # the circle similar to the hand's palm
            circle = Circle(middle_point(kinky_point, index_point), kinky_point.distance_to(index_point) / 1.5)

            # the thumb's tip point
            thumb_point = Point2D(self._coordinates(HandCoordinateType.TIP)['x'] * 100,
                                  self._coordinates(HandCoordinateType.TIP)['y'] * 100)

            if circle.contains(thumb_point):
                return False
            else:
                return True

        else:
            # https://stackoverflow.com/questions/35176451/python-code-to-calculate-angle-between-three-point-using-their-3d-coordinates

            # define the wrist, mcp and tip as np arrays
            wrist = np.array([self.wrist['x'] * 100, self.wrist['y'] * 100, self.wrist['z'] * 100])
            mcp = np.array(
                [self._coordinates(HandCoordinateType.MCP)['x'] * 100,
                 self._coordinates(HandCoordinateType.MCP)['y'] * 100,
                 self._coordinates(HandCoordinateType.MCP)['z'] * 100]
            )
            tip = np.array([x_coord_tip, y_coord_tip, self._coordinates(HandCoordinateType.TIP)['z'] * 100])

            # calculate the vectors
            mcp_wrist = wrist - mcp
            mcp_tip = tip - mcp

            # calculate the cosine angle, using dot product
            cos_angle = np.dot(mcp_wrist, mcp_tip) / (np.linalg.norm(mcp_wrist) * np.linalg.norm(mcp_tip))
            angle = np.degrees(np.arccos(cos_angle))

            # debug printing
            if Settings.PRINT_ANGLE:
                print(f'angle {self.type}: {angle}')

            if angle < Settings.ANGLE:
                return False
            else:
                return True

    def __str__(self):
        return f""" {_FingerType().dict()[self.type]} : {self.is_stretched()}"""


class Hand(object):

    def __init__(self, index: int, score: float, label: str, landmarks: list):
        """
        Inits a hand object.

        :param index: the hand's index of the detection
        :param score: the score of the detection
        :param label: the label (right or left) of the hand
        :param landmarks: a list of all hand landmarks
        """

        self.index = index
        self.score = score
        self.label = label
        self.landmarks = landmarks
        self._determine_hand()
        self.fingers = self._determine_fingers()
        # self._is_finger_stretched(0)

    def evaluate(self):
        """
        Evaluates the hand.
        :return: a dictionary, where the key is the finger type and the value tells if the finger is
                 is stretched or not.
        """

        result = dict()
        for finger in self._determine_fingers():
            result[finger.type] = finger.is_stretched()

        return result

    def _determine_fingers(self) -> List[Finger]:
        """
        Creates all fingers as objects and collects them into a list
        :return: a list of all fingers as objects
        """

        wrist = self.landmarks[HandCoordinateType.WRIST]
        index_finger = Finger(
            _FingerType.INDEX_FINGER,
            self.landmarks[HandCoordinateType.INDEX_FINGER_MCP:HandCoordinateType.INDEX_FINGER_TIP + 1],
            wrist
        )
        middle_finger = Finger(
            _FingerType.MIDDLE_FINGER,
            self.landmarks[HandCoordinateType.MIDDLE_FINGER_MCP:HandCoordinateType.MIDDLE_FINGER_TIP + 1],
            wrist
        )
        ring_finger = Finger(
            _FingerType.RING_FINGER,
            self.landmarks[HandCoordinateType.RING_FINGER_MCP:HandCoordinateType.RING_FINGER_TIP + 1],
            wrist
        )
        pinky_finger = Finger(
            _FingerType.PINKY_FINGER,
            self.landmarks[HandCoordinateType.PINKY_FINGER_MCP:],
            wrist
        )
        thumb = Finger(
            _FingerType.THUMB,
            self.landmarks[HandCoordinateType.THUMB_CMC:HandCoordinateType.THUMB_TIP + 1],
            wrist,
            index_finger,
            pinky_finger
        )

        return [thumb, index_finger, middle_finger, ring_finger, pinky_finger]

    def _determine_hand(self) -> type(None):
        """
        Determines if a hand is a left hand or a right hand.
        :return: void
        """
        if self.label == 'Right':
            self.is_right = True
        else:
            self.is_right = False
        return type(None)

    def _is_finger_stretched(self, finger_type: int) -> bool:
        """
        Looks up in the list of fingers, if a specific finger is stretched.
        :param finger_type: The finger of which the position wants to be known.
        :return: True, if stretched, false otherwise
        """
        return self.fingers[finger_type].is_stretched()

    def __str__(self):
        return f"""Hand: \n {self.label} : {self.landmarks}
                      {self.fingers[_FingerType.THUMB]}
                      {self.fingers[_FingerType.INDEX_FINGER]}
                      {self.fingers[_FingerType.MIDDLE_FINGER]}
                      {self.fingers[_FingerType.RING_FINGER]}
                      {self.fingers[_FingerType.PINKY_FINGER]}"""


class _FingerType:

    THUMB = 0
    INDEX_FINGER = 1
    MIDDLE_FINGER = 2
    RING_FINGER = 3
    PINKY_FINGER = 4

    def dict(self) -> dict:
        """
        Maps indices to strings.
        :return: a dictionary that maps the fingers index to a string representation
        """
        return {
            0: 'thumb',
            1: 'index finger',
            2: 'middle finger',
            3: 'ring finger',
            4: 'kinky finger'
        }

from statistics import mode

import cv2
import mediapipe as mp
import pyttsx3

from WriteHandler import *
from hand.Hand import *
from settings.Settings import *


# based upon https://google.github.io/mediapipe/solutions/hands.html#python-solution-api
class AirBraille(object):
    # text
    TITLE: str = 'AirBraille'
    ERROR_MSG: str = 'Zeichen nicht bekannt!'
    START_MSG: str = 'Starting detection ...'
    HANDS_VISIBLE: str = 'OK'
    HANDS_N_VISIBLE: str = 'NO'

    # are hands visible
    IS_POS_OK: bool = False

    THUMB_LEFT: str = str(Settings.LEFT_THUMB)
    THUMB_RIGHT: str = str(Settings.RIGHT_THUMB)

    EMPTY_STR: str = ''

    num_of_changes: int = 0

    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands  # hands

    def __init__(self, write_handler: AbstractWriteHandler, show_gui: bool = False):
        """
        Inits AirBraille.
        :param write_handler: The write handler that AirBraille uses.
        :param show_gui: Show graphical output.
        """
        self.show_gui = show_gui
        self.cap = cv2.VideoCapture(0)  # init webcam input
        self.images_count = 0  # setup image count
        self.writer = write_handler  # setup write-handler
        self.frame_results = []  # the frame result buffer
        self.previous_res = self.EMPTY_STR
        self.__clear_hand_pairs()
        self.tts = pyttsx3.init()  # init text to speech

    def _speak(self, msg: str):
        """
        Provides the message as audio feedback using pyttsx3.
        :param msg: The message that is provided as audio feedback.
        :return: void.
        """
        self.tts.say(msg)
        self.tts.runAndWait()

    def __clear_hand_pairs(self):
        """
        Clears the hand pair results. Resets image count.
        :return: void.
        """
        self.hand_pairs_res = dict()
        self.images_count = 0

    def __drop_oldest_frame(self):
        """
        Removes the oldest frame from the 'buffer'
        :return: void.
        """
        self.frame_results.pop(0)
        self.images_count = self.images_count - 1

    def _set_hands_state(self, val: bool):
        """
        Set's the hand's state (visible or not). Notifies on changes.
        :param val: The current visibility of the hand(s).
        :return: void.
        """
        if self.IS_POS_OK != val:
            self.num_of_changes += 1
            if self.num_of_changes >= 5:
                self.IS_POS_OK = val
                self.num_of_changes = 0
                self._notify_hands_state()
        else:
            self.num_of_changes = 0

    def _notify_hands_state(self):
        """
        Triggers audio output on change of hand(s) visibility.
        :return: void.
        """
        if self.IS_POS_OK:
            self._speak(self.HANDS_VISIBLE)
        else:
            self._speak(self.HANDS_N_VISIBLE)

    def _inc_count(self, result: str):
        """
        Increases the count of occurrences of the passed Braille pattern.
        Triggers that the result is returned, if enough frames analyzed.
        :param result: The braille pattern the hand(s) show(s).
        :return: void.
        """
        self.images_count += 1

        if Settings.CONFIRM_INPUT:
            if result in self.hand_pairs_res:
                self.hand_pairs_res[result] += 1
            else:
                self.hand_pairs_res[result] = 1
        else:
            self.frame_results.append(result)

        if self.images_count > Settings.THRESHOLD:
            self.type()

        return

    def _input_confirm(self, most_likely_key: str):
        """
        Mode: Input confirmation. In this case, AirBraille only returns the result (and starts analyzing)
        when the user confirmed the input.
        :param most_likely_key: The most often occurred braille pattern.
        :return: void.
        """
        if self.THUMB_LEFT in most_likely_key and self.THUMB_RIGHT in most_likely_key:
            self._write_and_speak(most_likely_key)
        elif not (self.THUMB_LEFT in most_likely_key) and not (self.THUMB_RIGHT in most_likely_key):
            # user waits, we drop the frame
            pass
        else:
            self._hotkey(most_likely_key)

        return

    def _continuous_input(self, frame_results):
        """
        Mode: Continuous input. All ten frames are evaluated.
        In case of a change to the previous printed result, the new result will
        be returned.
        :param frame_results: A list of all frame' results.
        :return: void.
        """
        # TODO: handle user settings access

        # get the key, that occurs the most
        most_likely_key = mode(frame_results)

        if most_likely_key != self.previous_res:
            self.previous_res = most_likely_key
            self._write_and_speak(most_likely_key)

        # remove the oldest frame's result
        self.__drop_oldest_frame()

    def _hotkey(self, most_likely_key: str):
        # TODO: user wants to access a hotkey
        """
        User accesses settings or hotkeys of AirBraille. This method handles this.
        :param most_likely_key: The most often occurred braille pattern.
        :return: void.
        """
        pass

    def _write_and_speak(self, most_likely_key: str):
        """
        Calls the WriteHandler to process the input. Removes left and right thumb from the pattern,
        that is passed to the WriteHandler, as this is preserved by AirBraille for hotkeys/settings.
        :param most_likely_key: The most often occurred braille pattern.
        :return:
        """
        # we will not pass '0' and '9' as they are preserved by AirBraille
        # WriteHandler's may only use '1'-'8' inclusive
        text = self.writer.write(most_likely_key
                                 .replace(self.THUMB_LEFT, self.EMPTY_STR)
                                 .replace(self.THUMB_RIGHT, self.EMPTY_STR))
        if Settings.DEBUG:
            print(text)
        if text != self.EMPTY_STR and text.isalnum():
            self._speak(text)
        else:
            self._speak(self.ERROR_MSG)
        return

    def type(self):
        """
        User typed. Finds most often occurred Braille pattern, and passes result to corresponding mode.
        Clears the hand pairs at the end.
        :return: void.
        """
        most_likely_key = ''
        most_likely_key_count = 0
        for candidate in self.hand_pairs_res:
            if self.hand_pairs_res[candidate] > most_likely_key_count:
                most_likely_key_count = self.hand_pairs_res[candidate]
                most_likely_key = candidate

        if Settings.CONFIRM_INPUT:
            self._input_confirm(most_likely_key)
            self.__clear_hand_pairs()
        else:
            self._continuous_input(self.frame_results)

        return

    def start_detection(self):
        """
        Starts the detection of AirBraille.
        :return: void.
        """
        self.__evaluate()

    def __evaluate(self):
        with self.mp_hands.Hands(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                max_num_hands=2) as hands:
            self._speak(self.START_MSG)
            while self.cap.isOpened():
                success, image = self.cap.read()
                if not success:
                    # print('empty camera frame ...')
                    continue

                # Flip the image horizontally for a later selfie-view display, and convert
                # the BGR image to RGB.
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                results = hands.process(image)
                if results.multi_handedness is not None:
                    hand_pair = HandPair()
                    valid, err_msg = hand_pair.is_valid(results.multi_handedness)
                    if not valid:
                        # print(err_msg)
                        self._set_hands_state(False)

                        if Settings.DEBUG:
                            hand_pair_debug = HandPair()
                            hand_pair_debug.define_hands(results)
                            hand_pair_debug.evaluate()
                            self.__draw_results(image, results)
                            if cv2.waitKey(5) & 0xFF == 27:
                                break
                        continue

                    self._set_hands_state(True)

                    hand_pair.define_hands(results)
                    self._inc_count(hand_pair.evaluate())
                else:
                    self._set_hands_state(False)

                self.__draw_results(image, results)
                if cv2.waitKey(5) & 0xFF == 27:
                    break

    def __draw_results(self, image, results):
        """
        Draws the results on the image.
        :param image: The image on where to draw on.
        :param results: The results of the detection.
        :return: void.
        """
        if self.show_gui or Settings.DEBUG:
            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            cv2.imshow(AirBraille.TITLE, image)

    def stop_detection(self):
        """
        Stops the detection of AirBraille.
        :return: void.
        """
        if self.cap is not None:
            self.cap.release()
        else:
            print('Cannot stop, detection has not even started yet!')

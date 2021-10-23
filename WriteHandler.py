import keyboard
import json
from abc import ABC, abstractmethod


class AbstractWriteHandler(ABC):
    """Base class for WriteHandler's."""

    @abstractmethod
    def write(self, fingers_txt: str) -> str:
        """
        Defines what text according to the input braille pattern text should be produced.
        :param fingers_txt: The braille cells that are, depending on the mode, hold as finger's position of
        the user.
        :return The string sequence according to the braille pattern that should be printed.
        """
        pass


class WriteHandler8Dot(AbstractWriteHandler):
    """8-dot Braille WriteHandler."""

    def __init__(self, file_path: str):
        """
        Inits a 8-dot WriteHandler.
        :param file_path: The path to the file that contains the 8-dot braille input texts.
        """
        self.text = ''
        self.keys = dict()
        self.file_path = file_path
        self.__setup()

    def __setup(self):
        """Private setup method"""
        # here we init the replacement json-file
        with open(self.file_path) as keys_file:
            data = json.load(keys_file)
            for entry in data:
                self.keys[entry['fingers']] = entry['c']

    def write(self, fingers_txt: str) -> str:
        """
        Declares what text sequence or char should be produced according to the input.
        :param fingers_txt: The input braille dot sequence.
        :return: The text that is provided as audio-feedback.
        """
        if fingers_txt in self.keys:
            self.text = self.keys[fingers_txt]
        else:
            self.text = ''

        self._send_keystroke()
        ret_val: str = self.text
        self.text = ''
        return ret_val

    def _send_keystroke(self):
        # TODO: implement keyboard stroke
        """This method sends a keystroke."""
        print('printing ' + self.text)
        pass
        # keyboard.write(self.text)


class WriteHandler6Dot(AbstractWriteHandler):
    """This class is the handler for writing 6 dot German-Braille."""

    def __init__(self, file_path: str):
        """
        Inits a 6-dot Braille WriteHandler.
        :param file_path: The path to the file that contains the 6-dot braille input texts.
        """
        self.previous = ''
        self.text = ''
        self.file_path = file_path
        self.keys = dict()
        self.__setup()

    def __setup(self):
        """Private setup method"""
        # here we init the replacement json-file
        with open(self.file_path) as keys_file:
            data = json.load(keys_file)
            for entry in data:
                self.keys[entry['fingers']] = entry['c']

    def __map(self, fingers_txt: str) -> str:
        """
        Private method that maps the finger-text we got from AirBraille
        so that it matches the one's inside the corresponding .json-file.
        :param fingers_txt: The input braille dot sequence.
        :return: The mapped text.
        """

        # as we do not need '7' & '8' we drop them
        fingers_txt = fingers_txt.replace('7', '').replace('8', '')
        if fingers_txt in self.keys:
            return self.keys[fingers_txt]
        else:
            return ''

    def write(self, fingers_text: str) -> str:
        """
        Overridden method from super-class. This one handles the \"actual\"
        writing. As it determines whether special case (e.g. capital-letters) or default
        cases is come to mention.
        :param fingers_text: The input braille dot sequence.
        :return: The text that is provided as audio-feedback.
        """
        self.text = self.__map(fingers_text)
        return self.text

    def _send_keystroke(self):
        # TODO: add keyboard strokes.
        """This method lets us send a keystroke."""
        print('printing ' + self.text)
        pass

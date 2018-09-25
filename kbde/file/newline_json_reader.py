from .file_reader import FileReader
import json


class NewlineJsonReader(FileReader):
    def get_line(self):
        line = FileReader.get_line(self)
        if line is None:
            return None
        return json.loads(line)

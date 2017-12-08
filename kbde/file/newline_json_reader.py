from .file_reader import FileReader
import json


class NewlineJsonReader(FileReader):
    def getLine(self):
        line = FileReader.getLine(self)
        if line is None:
            return None
        return json.loads(line)

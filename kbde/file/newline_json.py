import json
from .file_reader import FileReader
from .file_writer import FileWriter


class NewlineJson:
    def __init__(self,file_path):
        self.file_path = file_path
        self.file_writer = FileWriter(file_path)
        self.file_reader = FileReader(file_path)
        
    def get(self):
        line = self.file_reader.getLine()
        if line is None:
            return None
        line_dict = json.loads(line)
        return line_dict

    def put(self,line_dict):
        line = json.dumps(line_dict)
        self.file_writer.putLine(line)

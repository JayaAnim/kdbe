from .file_writer import FileWriter
import json


class NewlineJsonWriter(FileWriter):
    def putLine(self,data):
        json_data = json.dumps(data)
        FileWriter.putLine(self,json_data)

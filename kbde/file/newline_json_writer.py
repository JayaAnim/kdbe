from .file_writer import FileWriter
import json


class NewlineJsonWriter(FileWriter):
    def put_line(self,data):
        json_data = json.dumps(data)
        FileWriter.put_line(self,json_data)

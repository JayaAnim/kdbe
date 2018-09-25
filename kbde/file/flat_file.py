from .file_reader import FileReader
from .file_writer import FileWriter


class FlatFile:
    """
    Reads and writes flat files with a header
    Interfaces to caller with dictionaries
    """

    def __init__(self,file_path,delimiter):
        self.file_writer = FileWriter(file_path)
        self.file_reader = FileReader(file_path)
        self.delimiter = delimiter
        self.header_list = self.get_header_list()

    def get_header_list(self):
        """
        In the case where we are reading a file, derive the header_list from the first line of the file, where the header information is kept
        """
        if self.file_reader.get_line_count > 0:
            raise Exception("file not at first line")

        header_line = self.file_reader.get_line()
        if not header_line:
            return None

        header_list = self.make_list(header_line)

        return header_list

    def get(self):
        if self.header_list is None:
            raise self.FileException("no header line found")

        line = self.file_reader.get_line()
        if line is None:
            return None
        line_list = self.make_list(line)

        line_dict = {}
        index = 0
        for column_name in self.header_list:
            line_dict[column_name] = line_list[index]
            index += 1

        return line_dict

    def put(self,line_dict):
        if self.header_list is None:
            #Assign the first line to the header_list
            self.header_list = sorted(line_dict.keys())
            #Write the header line
            header_line = self.make_line(self.header_list)
            self.file_writer.put_line(header_line)

        line_list = []
        for column_name in self.header_list:
            value = line_dict.get(column_name)
            line_list.append(str(value))

        line = self.make_line(line_list)
        self.file_writer.put_line(line)

    def make_list(self,line):
        line_list = line.split(self.delimiter)
        return line_list

    def make_line(self,line_list):
        line = self.delimiter.join(line_list)
        return line

    class FileException(Exception):
        pass

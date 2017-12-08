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
        self.header_list = self.getHeaderList()

    def getHeaderList(self):
        """
        In the case where we are reading a file, derive the header_list from the first line of the file, where the header information is kept
        """
        if self.file_reader.get_line_count > 0:
            raise Exception("file not at first line")

        header_line = self.file_reader.getLine()
        if not header_line:
            return None

        header_list = self.makeList(header_line)

        return header_list

    def get(self):
        if self.header_list is None:
            raise self.FileException("no header line found")

        line = self.file_reader.getLine()
        if line is None:
            return None
        line_list = self.makeList(line)

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
            header_line = self.makeLine(self.header_list)
            self.file_writer.putLine(header_line)

        line_list = []
        for column_name in self.header_list:
            value = line_dict.get(column_name)
            line_list.append(str(value))

        line = self.makeLine(line_list)
        self.file_writer.putLine(line)

    def makeList(self,line):
        line_list = line.split(self.delimiter)
        return line_list

    def makeLine(self,line_list):
        line = self.delimiter.join(line_list)
        return line

    class FileException(Exception):
        pass

import csv
from io import StringIO
from .flat_file import FlatFile


class CsvFile(FlatFile):
    """
    Reads and writes csv files with a header
    Interfaces to caller with dictionaries
    """
    def __init__(self,file_path):
        FlatFile.__init__(self,file_path,",")

    def makeLine(self,line_list):
        string = StringIO.StringIO()
        writer = csv.writer(string)
        writer.writerow(line_list)
        line = string.getvalue()
        return line

    def makeList(self,line):
        string = StringIO.StringIO(line)
        reader = csv.reader(string)
        line_list = reader.next()
        return line_list

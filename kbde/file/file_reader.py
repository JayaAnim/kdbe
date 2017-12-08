class FileReader:
    """
    Reads a file line by line without loading it into memory
    """

    def __init__(self,file_path):
        self.file_path = file_path
        self.open_file = open(self.file_path,"r")
        self.get_line_count = 0

    def getLine(self):
        line = self.open_file.readline()
        if not line:
            return None
        line = line.strip()
        self.get_line_count += 1
        return line

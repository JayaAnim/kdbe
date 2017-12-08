class FileWriter:
    def __init__(self,file_path):
        self.file_path = file_path
        self.open_file = open(self.file_path,"a")
        self.write_line_count = 0

    def putLine(self,line):
        line = line + "\n"
        self.open_file.write(line)
        self.write_line_count += 1

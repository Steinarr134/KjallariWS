

class HintLoaderClass(object):
    def __init__(self, filename):
        self.Hints = {}
        self.FileName = filename
        self.load()

    def load(self):
        with file(self.FileName, 'r') as f:
            lines = f.readlines()
        print lines
        hints = []
        Qname = ""
        for line in lines:
            print line
            if not line.strip():
                continue
            if not (line[0] == "\t"):
                print "\t new Qname: " + line.strip()
                if Qname:
                    self.Hints[Qname] = hints
                Qname = line.strip()
                hints = []
            else:
                hints.append(line.strip().replace("\\", "\n"))

        if Qname:
            self.Hints[Qname] = hints




if __name__ == '__main__':
    HintLoader = HintLoaderClass("hints.txt")
    print HintLoader.Hints
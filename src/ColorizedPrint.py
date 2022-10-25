# usage ColorizedPrint("text", "INFO_WS")
class ColorizedPrint:
    def __init__(self, text, type):
        self.TITLE = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.INFO = '\033[93m'
        self.OKRED = '\033[91m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.BGRED = '\033[41m'
        self.UNDERLINE = '\033[4m'
        self.FGWHITE = '\033[37m'
        self.FAIL = '\033[95m'
        self.color = {
            "INFO_WS": self.INFO+self.BOLD+text+self.ENDC,
            "PLAIN_WS": self.INFO+text+self.ENDC,
            "ERROR": self.BGRED+self.FGWHITE+self.BOLD+text+self.ENDC,
            "MESSAGE_WS": self.TITLE+self.BOLD+text+self.ENDC,
            "MESSAGE": self.TITLE+self.BOLD+text+self.ENDC+"\n",
            "INSECURE": self.OKRED+self.BOLD+text+self.ENDC+"\n",
            "INSECURE_WS": self.OKRED+self.BOLD+text+self.ENDC,
            "OUTPUT": self.OKBLUE+self.BOLD+text+self.ENDC+"\n",
            "OUTPUT_WS": self.OKGREEN+self.BOLD+text+self.ENDC,
            "SECURE": self.OKGREEN+self.BOLD+text+self.ENDC+"\n"
        }
        print(self.color[type])
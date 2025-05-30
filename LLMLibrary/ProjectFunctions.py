import re
import datetime

def ReadFile(FileName: str):
    with open(FileName, "r", encoding="utf-8") as FileReader:
        return FileReader.read()

def DeleteThinking(Text: str):
    return re.sub("<think>.*<\/think>", "", Text, flags=re.DOTALL)

def TimedPrint(message, **kwargs):
    current_time = datetime.datetime.now().strftime("(%H:%M:%S)")
    print(f"# {current_time} {message}", **kwargs)
import re

def DeleteThinking(Text: str):
    return re.sub("<think>.*<\/think>", "", Text, flags=re.DOTALL)
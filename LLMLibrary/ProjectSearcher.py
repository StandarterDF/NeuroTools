import requests
from duckduckgo_search import DDGS

class ProjectSearcher:
    def Search(self, Text):
        return DDGS().text(Text, max_results=5)
    def Scrap(self, URL):
        return requests.get(url=URL)
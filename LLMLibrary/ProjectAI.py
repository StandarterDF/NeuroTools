import json
import requests

class ProjectAI_Tools:
    def get_models(self, base_api_url):
        return json.loads(requests.get(f"{base_api_url}/models").text)
    def models2list(self, models):
        result = []
        for model in models["data"]:
            result.append(model["id"])
        return result
    
if __name__ == "__main__":
    PAI = ProjectAI_Tools()
    Models = PAI.get_models("http://192.168.0.124:1234/v1")
    ModelsList = PAI.models2list(Models)
    print(ModelsList)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from markupsafe import Markup
import uvicorn
import Config
from LLMLibrary.ProjectAI import ProjectAI_Tools

AutocreatorUI = FastAPI()
AutocreatorUI.mount("/icons", StaticFiles(directory="icons"), name="icons")
AutocreatorUI.mount("/javascript", StaticFiles(directory="javascript"), name="javascript")

# Указываем путь к папке с шаблонами
templates = Jinja2Templates(directory="templates")

ProjectName = "AutocreatorUI"
RemoteFreeFilter = True

@AutocreatorUI.get("/autocreator", response_class=HTMLResponse)
async def main(request: Request):
    PAI = ProjectAI_Tools()
    
    Models = {}
    for provider in Config.OpenAI_API_Providers.keys():
        Models[provider] = PAI.models2list(
            PAI.get_models(
                Config.OpenAI_API_Providers[provider]["base_url"]
            )
        )
    
    if RemoteFreeFilter:
        for provider, models in Models.items():
            Models[provider] = [
                model for model in models
                if Config.OpenAI_API_Providers[provider]["type"] == "local" or model.endswith(":free")
            ]
    
    return templates.TemplateResponse("autocreator.html", {
        "request": request,
        "title": f"Project: {ProjectName}",
        "provider_models": Config.OpenAI_API_Providers,
        "models": Models 
    })
    
if __name__ == "__main__":
    uvicorn.run(AutocreatorUI, host="127.0.0.1", port=8000)
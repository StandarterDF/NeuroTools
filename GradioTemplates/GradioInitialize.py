import gradio as gr

import os
import Config
import LLMLibrary.ProjectFunctions as LLMFunc

from LLMLibrary.ProjectAI import ProjectAI_Tools

PAI = ProjectAI_Tools()

Models = {}
for provider in Config.OpenAI_API_Providers.keys():
    Models[provider] = PAI.models2list(
        PAI.get_models(Config.OpenAI_API_Providers[provider]["base_url"])
    )
    
# Directory Init
Modules = [
    "Autocreator",
    "Autoanswer"
]
os.makedirs("Docs/", exist_ok=True)
for Module in Modules:
    os.makedirs(f"Docs/{Module}", exist_ok=True)
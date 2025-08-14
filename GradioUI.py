import gradio as gr
import os
import Config
import LLMLibrary.ProjectFunctions as LLMFunc
from LLMLibrary.ProjectAI import ProjectAI_Tools

# Directory Init
Modules = [
    "Autocreator",
    "Autoanswer"
]
#

with gr.Blocks() as GradioUI:
    with gr.Tabs():
        with gr.TabItem("Project Creator"):
            import GradioAutocreator
        with gr.TabItem("Project Answer"):
            import GradioAutoanswer
    
if __name__ == "__main__":
    GradioUI.launch()
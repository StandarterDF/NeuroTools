import LLMLibrary.ProjectFunctions as LLMFunc
from LLMLibrary.ProjectAI import ProjectAI_Tools
from markdown_pdf import Section
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import ProjectAutocreatorT
import markdown_pdf
import datetime
import pprint
import re
import os
import uvicorn
import Config
import threading
import time
import copy

AutocreatorUI = FastAPI()
AutocreatorUI.mount("/icons", StaticFiles(directory="icons"), name="icons")
AutocreatorUI.mount("/javascript", StaticFiles(directory="javascript"), name="javascript")
AutocreatorUI.mount("/Docs", StaticFiles(directory="Docs"), name="Docs")

# Указываем путь к папке с шаблонами
templates = Jinja2Templates(directory="templates")

ProjectName = "AutocreatorUI"
RemoteFreeFilter = True

global LogsText
global PauseGeneration
global SubGeneration
global GenerationState
global LastCommand
global CurrentGeneration
global FinalFile

LogsText = "---------LOG STARTED--------\n"
PauseGeneration = False
SubGeneration = False
GenerationState = "None"
LastCommand = ["0", 0]
CurrentGeneration = False


class SiteCMD(BaseModel):
    CMD: str
    
class NNParameters(BaseModel):
    Topic: str
    TopicCount: str
    SubTopicGen: bool 
    ThinkMode: bool 
    GenPDF: bool
    ModelInfo: str
    ModelFunc:str
    ModelInfoProvider:str
    ModelFuncProvider:str

def logprint(Text):
    global LogsText
    current_time = datetime.datetime.now().strftime("(%H:%M:%S)")
    print(f"{current_time}" + str(Text), end="")
    LogsText += str(f"{current_time}" + str(Text))
def logprintln(Text):
    global LogsText
    current_time = datetime.datetime.now().strftime("(%H:%M:%S)")
    print(f"{current_time}" + str(Text))
    LogsText += str(f"{current_time}" + str(Text)) + "\n"
def logclear():
    global LogsText
    LogsText = ""
def wait_unpause(Text: str):
    global PauseGeneration
    PauseGeneration = True
    if Text != "": logprintln(Text)
    while not PauseGeneration:
        time.sleep(0.1)
    return True
def wait_cmd(Text: str, State: str = "WaitForCommand"):
    global LastCommand
    global GenerationState
    GenerationState = State
    LastID = copy.copy(LastCommand[1])
    while True:
        if LastCommand[1] != LastID:
            if Text != "": logprintln(Text)
            break
        time.sleep(0.1)
    return LastCommand
    
def GenerateProject(Topic: str, TopicCount: str, SubTopicGen: bool, ThinkMode: bool, GenPDF: bool, ModelInfo: str, ModelFunc:str, ModelInfoProvider:str, ModelFuncProvider:str):
    # ----- PROGRAM START -----
    logprintln("#-------------------------------------------------#")
    logprintln("# -> PROJECT: Auto Creator")
    logprintln("#-------------------------------------------------#")
    Providers = list(Config.OpenAI_API_Providers.keys())
    
    Model = ModelInfo
    Config.OpenAI_API_Providers[ModelInfoProvider]["model"] = Model
    AI_Basic = ChatOpenAI(**Config.OpenAI_API_Providers[ModelInfoProvider])
    Model = ModelFunc
    Config.OpenAI_API_Providers[ModelFuncProvider]["model"] = Model
    AI_Function = ChatOpenAI(**Config.OpenAI_API_Providers[ModelFuncProvider])
    
    AI_Topic_G1 = AI_Function.with_structured_output(ProjectAutocreatorT.TopicGenerator)
    AI_Topic_G2 = AI_Function.with_structured_output(ProjectAutocreatorT.TopicGeneratorA1)
    
    Structure = []
    FullStructure = []
    ResultText = ""
    
    #########################################################
    # Generate basic structure
    #########################################################
    i = 0
    while True:
        i += 1
        logprintln(f"# -> Генерирование структуры (Попытка {i})")
        ExpTest = True
        Structure = AI_Topic_G1.invoke(
            ProjectAutocreatorT.Template_1.invoke({ "Topic": Topic, "TopicCount": TopicCount, "ThinkMode": "/nothink" if not ThinkMode else ""})
        )
        for Element in Structure.Topics:
            if re.match("^[0-9]{1,}\.", Element) == None: 
                ExpTest = False
                break
        if not ExpTest:
            continue
        logprintln(Structure)
        if wait_cmd("Устраивает результат?")[0] == "continue":
            break
    
    #########################################################
    #
    #########################################################
    for SElement in Structure.Topics:
        CurrentTopics = [SElement]
        if SubTopicGen:
            """
            Генерация дополнительных подтем.
            """
            print(f"# -> ({SElement}) Генерирование подтемы...")
            i = 0
            while True:
                i += 1
                print(f"# -> Генерирование суб-структуры (Попытка {i})")
                ExpTest = True
                Result = AI_Topic_G2.invoke(
                    ProjectAutocreatorT.Template_2.invoke({"CurrTopic": CurrentTopics[0], "ThinkMode": "/nothink" if not ThinkMode else "", "CurNum": re.search("[0-9]{1,}\.", SElement).group()})
                ).Topics
                for Element in Result:
                    if re.match("^[0-9]{1,}\.", Element) == None: 
                        ExpTest = False
                        break
                if not ExpTest:
                    continue
                break
                
            
            CurrentTopics.extend(
                Result
            )
            logprintln("# -> Подтемы:")
            pprint.pprint(CurrentTopics[1:])
            """
            
            """
            logprintln(f"# -> (START) Генерирование введения в главу {CurrentTopics[0]}")
            ResultText += "\n" + LLMFunc.DeleteThinking(AI_Basic.invoke(
                ProjectAutocreatorT.Template_5.invoke({"Topic": CurrentTopics[0], "AllTopics": "\n".join(CurrentTopics[1:]), "ThinkMode": "/nothink" if not ThinkMode else ""})
            ).content) +  "\n"
            for SubElement in CurrentTopics[1:]:
                logprintln(f"# -> (START) Генерирование подглавы {SubElement}")
                ResultText += "\n" +  LLMFunc.DeleteThinking(AI_Basic.invoke(
                    ProjectAutocreatorT.Template_6.invoke({"Subtopic": SubElement, "Topic": CurrentTopics[0], "AllTopics": "\n".join(CurrentTopics[1:]), "ThinkMode": "/nothink" if not ThinkMode else ""})
                ).content) +  "\n"
        else:
            """
            
            """
            logprintln(f"# -> Генерирование главы: {SElement}")
            ResultText += "\n" +  LLMFunc.DeleteThinking(AI_Basic.invoke(
                ProjectAutocreatorT.Template_7.invoke({"Topic": SElement, "MainTopic": Topic, "AllTopics": "\n".join(Structure.Topics), "ThinkMode": "/nothink" if not ThinkMode else ""})
            ).content) +  "\n"
        FullStructure.extend(CurrentTopics)
    
    
    ResultText = "\n" + LLMFunc.DeleteThinking(AI_Basic.invoke(
        ProjectAutocreatorT.Template_3.invoke({"Themes": "\n".join(FullStructure), "ThinkMode": "/nothink" if not ThinkMode else ""}
        )    
    ).content) + "\n" + ResultText
    
    ResultText += "\n" +  LLMFunc.DeleteThinking(AI_Basic.invoke(
        ProjectAutocreatorT.Template_4.invoke({"Themes": "\n".join(FullStructure), "ThinkMode": "/nothink" if not ThinkMode else ""})    
    ).content)  +  "\n"
    FileName = Topic.replace(".", "")
    
    ResultData = LLMFunc.FixLLMFormula(ResultData)
    
    with open("Docs/" + FileName + ".md", "w", encoding="utf-8") as FileWriter:
        FileWriter.write(ResultText)
    if GenPDF:
        PDF = markdown_pdf.MarkdownPdf(toc_level=1)
        PDF.add_section(Section(ResultText, toc=False))
        PDF.save("Docs/" + FileName + ".pdf")
    logprintln("# -> Файл успешно сохранен!")
    global FinalFile
    FinalFile = FileName + ".pdf"
    global GenerationState
    GenerationState = "Complete"
    
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
    
    Files = [File for File in os.listdir("Docs/") if os.path.isfile(f"Docs/{File}")]
    print(Files)
    Files.sort(key=lambda x: os.stat(f"Docs/{x}").st_ctime)
    print(Files)
    
    if len(Files) == 0: Files.append("No Files Found")
    
    return templates.TemplateResponse("autocreator.html", {
        "request": request,
        "title": f"Project: {ProjectName}",
        "provider_models": Config.OpenAI_API_Providers,
        "models": Models,
        "files": Files
    })

@AutocreatorUI.get("/autocreator_log", response_class=PlainTextResponse)
async def get_log(requests: Request):
    return LogsText

@AutocreatorUI.get("/autocreator_getfile", response_class=PlainTextResponse)
async def get_file(requests: Request):
    global FinalFile
    return FinalFile

@AutocreatorUI.get("/autocreator_getstate", response_class=PlainTextResponse)
async def get_state(requests: Request):
    global GenerationState
    return GenerationState

@AutocreatorUI.post("/autocreator_command", response_class=PlainTextResponse)
async def set_cmd(cmd: SiteCMD):
    global LastCommand
    logprintln(LastCommand)
    LastCommand = [cmd.CMD, LastCommand[1] + 1]
    
@AutocreatorUI.post("/autocreator_generate", response_class=PlainTextResponse)
async def get_state(nnparameters: NNParameters):
    global CurrentGeneration
    if not CurrentGeneration:
        CurrentGeneration = True
        threading.Thread(target=GenerateProject, 
                         args=(
                            nnparameters.Topic, 
                            nnparameters.TopicCount, 
                            nnparameters.SubTopicGen, 
                            nnparameters.ThinkMode, 
                            nnparameters.GenPDF, 
                            nnparameters.ModelInfo, 
                            nnparameters.ModelFunc, 
                            nnparameters.ModelInfoProvider, 
                            nnparameters.ModelFuncProvider)
        ).start()

if __name__ == "__main__":
    uvicorn.run(AutocreatorUI, host="127.0.0.1", port=22222)
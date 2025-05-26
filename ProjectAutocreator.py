from datetime import datetime
import LLMLibrary.ProjectFunctions as LLMFunc
from langchain_openai import ChatOpenAI
from markdown_pdf import Section
import ProjectAutocreatorT
import markdown_pdf
import Config
import pprint
import re

if __name__ == "__main__":
    # ----- PROGRAM START -----
    print("#-------------------------------------------------#")
    print("# -> PROJECT: Auto Creator")
    print("#-------------------------------------------------#")
    from ProjectTemplate import *
    # -------------------------
    Topic = input("# -> Введите тему проекта: ")
    TopicCount = input("# -> Желаемое количество тем: ")
    SubTopicGen = True if input("# -> Генерировать подглавы? (Да\Нет): ") == "Да" else False 
    ThinkMode = True if input("# -> Включить мысли модели? (Да\Нет): ") == "Да" else False 
    GenPDF = True if input("# -> Генерировать PDF (Да\Нет): ") == "Да" else False 
    print("#-------------------------------------------------#")
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
        print(f"# -> Генерирование структуры (Попытка {i})")
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
        print(Structure)
        if input("# Устраивает результат? (Да\Нет): ") == "Да":
            print("#-------------------------------------------------#") 
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
            print(f"# -> Подтемы:")
            pprint.pprint(CurrentTopics[1:])
            """
            
            """
            print(f"# -> (START) Генерирование введения в главу {CurrentTopics[0]}")
            ResultText += "\n" + LLMFunc.DeleteThinking(AI_Basic.invoke(
                ProjectAutocreatorT.Template_5.invoke({"Topic": CurrentTopics[0], "AllTopics": "\n".join(CurrentTopics[1:]), "ThinkMode": "/nothink" if not ThinkMode else ""})
            ).content) +  "\n"
            for SubElement in CurrentTopics[1:]:
                print(f"# -> (START) Генерирование подглавы {SubElement}")
                ResultText += "\n" +  LLMFunc.DeleteThinking(AI_Basic.invoke(
                    ProjectAutocreatorT.Template_6.invoke({"Subtopic": SubElement, "Topic": CurrentTopics[0], "AllTopics": "\n".join(CurrentTopics[1:]), "ThinkMode": "/nothink" if not ThinkMode else ""})
                ).content) +  "\n"
        else:
            """
            
            """
            print(f"# -> Генерирование главы: {SElement}")
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
    with open(FileName + ".md", "w", encoding="utf-8") as FileWriter:
        FileWriter.write(ResultText)
    if GenPDF:
        PDF = markdown_pdf.MarkdownPdf(toc_level=1)
        PDF.add_section(Section(ResultText, toc=False))
        PDF.save(FileName + ".pdf")
    print("# -> Файл успешно сохранен!")
        
from datetime import datetime
import LLMLibrary.ProjectFunctions as LLMFunc
from langchain_openai import ChatOpenAI
import ProjectAutocreatorT
import Config
import pprint
import re

if __name__ == "__main__":
    print("#-------------------------------------------------#")
    print("# -> PROVIDERS INSTALLED ")
    Providers = list(Config.OpenAI_API_Providers.keys())
    for Provider in Providers:
        print(f"# {Providers.index(Provider)} -> {Provider}")
    print("#-------------------------------------------------#")
    print("# -> BASIC MODEL (INFORMATION)"); Choise = -1
    while int(Choise) not in range(0, len(Providers)):
        Choise = input("# -> Введите номер провайдера API: ")
    Model = input(f"# -> Введите название модели ({Config.OpenAI_API_Providers[Providers[int(Choise)]]['model']}):")
    if Model == "": Model = Config.OpenAI_API_Providers[Providers[int(Choise)]]["model"]
    Config.OpenAI_API_Providers[Providers[int(Choise)]]["model"] = Model
    AI_Basic = ChatOpenAI(**Config.OpenAI_API_Providers[Providers[int(Choise)]])
    print("#-------------------------------------------------#")
    print("# -> FUNCTIONAL MODEL (OUTPUT)"); Choise = -1
    while int(Choise) not in range(0, len(Providers)):
        Choise = input("# -> Введите номер провайдера API: ")
    Model = input(f"# -> Введите название модели ({Config.OpenAI_API_Providers[Providers[int(Choise)]]['model']}):")
    if Model == "": Model = Config.OpenAI_API_Providers[Providers[int(Choise)]]["model"]
    Config.OpenAI_API_Providers[Providers[int(Choise)]]["model"] = Model
    AI_Function = ChatOpenAI(**Config.OpenAI_API_Providers[Providers[int(Choise)]])
    print("#-------------------------------------------------#")
    Topic = input("# -> Введите тему проекта: ")
    TopicCount = input("# -> Желаемое количество тем: ")
    SubTopicGen = True if input("# -> Генерировать подглавы? (Да\Нет): ") == "Да" else False 
    ThinkMode = True if input("# -> Включить мысли модели? (Да\Нет): ") == "Да" else False 
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
            ProjectAutocreatorT.Template_1.invoke(
                {
                    "Topic": Topic,
                    "TopicCount": TopicCount,
                    "ThinkMode": "/nothink" if not ThinkMode else ""
                }
            )
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
                    ProjectAutocreatorT.Template_2.invoke(
                        {
                            "CurrTopic": CurrentTopics[0],
                            "ThinkMode": "/nothink" if not ThinkMode else "",
                            "CurNum": re.search("[0-9]{1,}\.", SElement).group()
                        }
                    )
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
            ResultText += LLMFunc.DeleteThinking(AI_Basic.invoke(
                ProjectAutocreatorT.Template_5.invoke(
                    {
                        "Topic": CurrentTopics[0],
                        "AllTopics": "\n".join(CurrentTopics[1:]),
                        "ThinkMode": "/nothink" if not ThinkMode else ""
                    }
                )
            ).content)
            for SubElement in CurrentTopics[1:]:
                print(f"# -> (START) Генерирование подглавы {SubElement}")
                ResultText += LLMFunc.DeleteThinking(AI_Basic.invoke(
                    ProjectAutocreatorT.Template_6.invoke(
                        {
                            "Subtopic": SubElement,
                            "Topic": CurrentTopics[0],
                            "AllTopics": "\n".join(CurrentTopics[1:]),
                            "ThinkMode": "/nothink" if not ThinkMode else ""
                        }
                    )
                ).content)
        else:
            """
            
            """
            print(f"# -> Генерирование главы: {SElement}")
            ResultText += LLMFunc.DeleteThinking(AI_Basic.invoke(
                ProjectAutocreatorT.Template_7.invoke(
                    {
                        "Topic": SElement,
                        "ThinkMode": "/nothink" if not ThinkMode else ""
                    }
                )
            ).content)
        FullStructure.extend(CurrentTopics)
    
    
    ResultText = LLMFunc.DeleteThinking(AI_Basic.invoke(
        ProjectAutocreatorT.Template_3.invoke(
            {
                "Themes": "\n".join(FullStructure),
                "ThinkMode": "/nothink" if not ThinkMode else ""
            }
        )    
    ).content) + ResultText
    
    ResultText += LLMFunc.DeleteThinking(AI_Basic.invoke(
        ProjectAutocreatorT.Template_4.invoke(
            {
                "Themes": "\n".join(FullStructure),
                "ThinkMode": "/nothink" if not ThinkMode else ""
            }
        )    
    ).content)
    
    with open(input("# -> Введите название файла, в который необходимо сохранить результат: ") + ".md", "w", encoding="utf-8") as FileWriter:
        FileWriter.write(ResultText)
    print("# -> Файл успешно сохранен!")
        
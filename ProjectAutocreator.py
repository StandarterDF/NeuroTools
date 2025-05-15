from datetime import datetime
import LLMLibrary.ProjectFunctions as LLMFunc
from langchain_openai import ChatOpenAI
import ProjectAutocreatorT
import Config
import pprint
import os

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
    AI_Basic = ChatOpenAI(**Config.OpenAI_API_Providers[Providers[int(Choise)]])
    print("#-------------------------------------------------#")
    print("# -> FUNCTIONAL MODEL (OUTPUT)"); Choise = -1
    while int(Choise) not in range(0, len(Providers)):
        Choise = input("# -> Введите номер провайдера API: ")
    AI_Function = ChatOpenAI(**Config.OpenAI_API_Providers[Providers[int(Choise)]])
    print("#-------------------------------------------------#")
    Topic = input("# -> Введите тему проекта: ")
    TopicCount = input("# -> Желаемое количество тем: ")
    TopicA1Gen = True if input("# -> Генерировать подглавы? (Да\Нет): ") == "Да" else False 
    print("#-------------------------------------------------#")
    AI_Topic_G1 = AI_Function.with_structured_output(ProjectAutocreatorT.TopicGenerator)
    AI_Topic_G2 = AI_Function.with_structured_output(ProjectAutocreatorT.TopicGeneratorA1)
    
    Structure = []
    
    while True:
        Structure = AI_Topic_G1.invoke(
            ProjectAutocreatorT.Template_1.invoke(
                {
                    "Topic": Topic,
                    "TopicCount": TopicCount,
                }
            )
        )
        print(Structure)
        if input("# Устраивает результат? (Да\Нет): ") == "Да":
            print("#-------------------------------------------------#") 
            break
    TopicsTexts = []
    if TopicA1Gen:
        StructureFinal = []
        StructureFinal.append(Structure.Topics[0])
        for TopicA1 in Structure.Topics[1:-1]:
            CurrTopic = TopicA1
            CurrTopicA1 = AI_Topic_G2.invoke(
                ProjectAutocreatorT.Template_2.invoke(
                    {
                        "CurrTopic": CurrTopic
                    }
                )
            ).Topics
            print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) Генерация подглав -> {CurrTopic} ({len(CurrTopicA1)})")
            StructureFinal.append(CurrTopic)
            StructureFinal.extend(CurrTopicA1)
        StructureFinal.append(Structure.Topics[-1])
    else:
        StructureFinal = Structure.Topics
    pprint.pprint(StructureFinal)
    print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) -> Генерирую оглавление!")
    TopicsTexts.append(
        LLMFunc.DeleteThinking(
            AI_Basic.invoke(
                ProjectAutocreatorT.Template_3.invoke(
                    {
                        "Themes": chr(10).join(StructureFinal)
                    }
                )
            ).content
        )
    )
    with open(Config.BaseDir + "/" + "Output.md", "w", encoding="utf-8") as FileWriter:
        for ITopic in StructureFinal:
            print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) -> Генерирую главу: {ITopic} ", end="")
            while True :
                TTopic = LLMFunc.DeleteThinking(
                    AI_Basic.invoke(
                        ProjectAutocreatorT.Template_4.invoke(
                            {
                                "Themes": chr(10).join(StructureFinal),
                                "Topic": Topic,
                                "ITopic": ITopic,
                            }
                        )
                    ).content
                )
                if Config.TopicText_AutoGenerator or input("# Устраивает результат? (Да\Нет): ") != "Да":
                    print(f"(Успех) / {len(TTopic)} символов")
                    TopicsTexts.append(TTopic)
                    break
        print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) -> Генерирую список литературы!")
        TopicsTexts.append(
            LLMFunc.DeleteThinking(
                AI_Basic.invoke(
                    ProjectAutocreatorT.Template_5.invoke(
                        {
                            "Themes": chr(10).join(StructureFinal),
                        }
                    )
                ).content
            )
        )
        FileWriter.write("\n".join(TopicsTexts))
        print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) Ваш проект на тему {Topic} успешно сохранен в Output.md!")
        
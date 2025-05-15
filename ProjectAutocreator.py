from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
import ProjectDatabase
import ProjectSearcher
import ProjectAI
import Config
import pprint
import os

if __name__ == "__main__":
    print("#-------------------------------------------------#")
    print("# -> PROVIDERS INSTALLED ")
    for Provider in Config.OpenAI_API_Providers.keys():
        print(f"# -> {Provider}")
    Choise = ""
    print("#-------------------------------------------------#")
    while Choise not in Config.OpenAI_API_Providers.keys():
        Choise = input("# -> Введите провайдера API: ")
    Config.OpenAI_API_BaseURL = Config.OpenAI_API_Providers[Choise]["base_url"]
    Config.OpenAI_API_Key = Config.OpenAI_API_Providers[Choise]["key"]
    Config.OpenAI_API_Model = Config.OpenAI_API_Providers[Choise]["model"]
    print("#-------------------------------------------------#")
    Topic = input("Введите тему проекта: ")
    TopicCount = input("Желаемое количество тем: ")
    TopicA1Gen = True if input("Генерировать подглавы? (Да\Нет): ") == "Да" else False 
    print("#-------------------------------------------------#")
    
    AI = ProjectAI.ProjectAI()
    DDGS = ProjectSearcher.ProjectSearcher()
    
    #DB = ProjectDatabase.ProjectDatabase()
    #DB.ChromaUpdate("HelloWorld", [IText.page_content for IText in TextSplitter.create_documents([Text])])
    #print(DB.ChromaSearch("HelloWorld", "любимый предмет"))
    
    Structure = []
    
    while True:
        Structure = AI.TopicAI.invoke(
            f"""
            /nothink Напиши оглавление для проекта на тему: {Topic}.
            Очень хотелось бы, чтоб количество глав было минимум {TopicCount}.
            Пример названия главы: "1. Название главы"
            Пример названия главы: "2. Другое название"
            Обязательно соблюдай формат названия, который указан в примере.
            Писать желательно на русском.
            Все главы должны быть четко структурированы.
            """
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
            CurrTopicA1 = AI.TopicA1AI.invoke(
                f"""
                /nothink Напиши подглавы для основной главы: {CurrTopic}.
                Очень хотелось бы, чтоб количество подглав было минимум 2-3.
                Пример названия подглавы: "{CurrTopic[0]}.1. Название главы"
                Пример названия подглавы: "{CurrTopic[0]}.3. Другое название"
                Обязательно соблюдай формат названия, который указан в примере.
                Важно, чтоб номер подглавы начинался с номера главы, как в примере.
                Писать желательно на русском.
                Все подглавы должны быть четко структурированы и их тема относится к основной главе.
                """
            ).Topics
            print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) Генерация подглав -> {CurrTopic} ({len(CurrTopicA1)})")
            StructureFinal.append(CurrTopic)
            StructureFinal.extend(CurrTopicA1)
        StructureFinal.append(Structure.Topics[-1])
    else:
        StructureFinal = Structure.Topics
    pprint.pprint(StructureFinal)
    print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) -> Генерирую оглавление!")
    TopicsTexts.append(AI.GenerateResponse(
            f"""
            Вот список тем:
            {chr(10).join(StructureFinal)}
            Красиво запиши их так, чтоб получилось оглавление.
            Ничего, кроме оглавления писать не нужно.
            Для форматирования можешь использовать markdown.
            Пример вывода:
            #Оглавление
            ## 1. Введение
            ## 2. Первая глава
            ## n. n-нная глава
            ## Заключение.
            """
    ).replace("<think>\n\n</think>\n", ""))
    with open(Config.BaseDir + "/" + "Output.md", "w", encoding="utf-8") as FileWriter:
        for ITopic in StructureFinal:
            print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) -> Генерирую главу: {ITopic} ", end="")
            while True :
                TTopic = AI.GenerateResponse(
                    f"""
                    Вот список тем:
                    {chr(10).join(StructureFinal)}
                    Твоя задача написать главу для проекта про {Topic}.
                    В данный момент ты пишешь главу: {ITopic}.
                    Глава должна быть оформлена так:
                    # {ITopic} если это основная глава (Пример "1. Глава")
                    ## {ITopic} если это подглава (Пример "1.1 Подглава")
                    Основной текст расположен в подглавах. В главах (Пример "1. Глава") же очень краткий обзор на то, что будет далее в поглавах. 
                    Это можешь посмотреть выше, в структуре.
                    Учитывай положение, в котором ты сейчас находишься при ответе.
                    Форматирование проекта может осуществляться посредством markdown.
                    То есть, название  глав и подглав и так далее можно выделять, делать жирним, курсивом и так далее.
                    В твоем ответе должен содержаться только текст главы, ничего больше. Это важно.
                    Генерируй строго по структуре. Не пытайся добавить что-то от себя.
                    """
                ).replace("<think>\n\n</think>\n", "")
                if Config.TopicText_AutoGenerator or input("# Устраивает результат? (Да\Нет): ") != "Да":
                    print(f"(Успех) / {len(TTopic)} символов")
                    TopicsTexts.append(TTopic)
                    break
        print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) -> Генерирую список литературы!")
        TopicsTexts.append(AI.GenerateResponse(
            f"""
            Вот список тем:
            {chr(10).join(StructureFinal)}
            По этим темам сделай список литературы.
            Ничего, кроме списка писать не нужно.
            Для форматирования можешь использовать markdown.
            Список должен быть по ГОСТУ. Это обязательно.
            Книг минимум 15. Это важно.
            Ответ должен начинаться с:
            Список литературы
            """
        ).replace("<think>\n\n</think>\n", ""))
        FileWriter.write("\n".join(TopicsTexts))
        print(f"# ({datetime.now().minute:02d}:{datetime.now().second:02d}) Ваш проект на тему {Topic} успешно сохранен в Output.md!")
        
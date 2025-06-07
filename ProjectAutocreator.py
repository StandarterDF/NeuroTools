import LLMLibrary.ProjectFunctions as LLMFunc
from markdown_pdf import Section
from ProjectTemplate import *
import ProjectAutocreatorT
import markdown_pdf
import pprint
import re

def get_user_input(prompt, yes_no=False):
    """Получение ввода от пользователя с возможностью обработки да/нет вопросов"""
    user_input = input(prompt)
    return user_input == "Да" if yes_no else user_input

def validate_structure(topics):
    """Проверка корректности структуры тем"""
    return all(re.match(r"^[0-9]{1,}\.", topic) for topic in topics)

def generate_main_structure(topic, topic_count, think_mode, ai_generator, template):
    """Генерация основной структуры проекта"""
    attempt = 0
    while True:
        attempt += 1
        print(f"# -> Генерирование структуры (Попытка {attempt})")
        
        structure = ai_generator.invoke(
            template.invoke({
                "Topic": topic,
                "TopicCount": topic_count,
                "ThinkMode": "/nothink" if not think_mode else ""
            })
        )
        
        if validate_structure(structure.Topics):
            pprint.pprint(structure)
            if get_user_input("# Устраивает результат? (Да\Нет): ", yes_no=True):
                print("#-------------------------------------------------#") 
                return structure

def generate_subtopics(main_topic, think_mode, ai_generator, template):
    """Генерация подтем для основной темы"""
    attempt = 0
    while True:
        attempt += 1
        print(f"# -> Генерирование суб-структуры (Попытка {attempt})")
        
        current_num = re.search(r"[0-9]{1,}\.", main_topic).group()
        result = ai_generator.invoke(
            template.invoke({
                "CurrTopic": main_topic,
                "ThinkMode": "/nothink" if not think_mode else "",
                "CurNum": current_num
            })
        ).Topics
        
        if validate_structure(result):
            return result

if __name__ == "__main__":
    # ----- PROGRAM START -----
    print("#-------------------------------------------------#")
    print("# -> PROJECT: Auto Creator")
    print("#-------------------------------------------------#")
    
    # Получение параметров от пользователя
    main_topic = get_user_input("# -> Введите тему проекта: ")
    topics_count = get_user_input("# -> Желаемое количество тем: ")
    generate_subtopics_flag = get_user_input("# -> Генерировать подглавы? (Да\Нет): ", yes_no=True)
    think_mode_enabled = get_user_input("# -> Включить мысли модели? (Да\Нет): ", yes_no=True)
    generate_pdf = get_user_input("# -> Генерировать PDF (Да\Нет): ", yes_no=True)
    
    print("#-------------------------------------------------#")
    
    # Инициализация AI генераторов
    topic_generator_1 = AI_Function.with_structured_output(ProjectAutocreatorT.TopicGenerator)
    topic_generator_2 = AI_Function.with_structured_output(ProjectAutocreatorT.TopicGeneratorA1)
    
    full_structure = []
    result_text = ""
    
    # Генерация основной структуры
    structure = generate_main_structure(
        main_topic,
        topics_count,
        think_mode_enabled,
        topic_generator_1,
        ProjectAutocreatorT.Template_1
    )
    
    # Генерация контента для каждой темы
    for topic in structure.Topics:
        current_topics = [topic]
        
        if generate_subtopics_flag:
            print(f"# -> ({topic}) Генерирование подтемы...")
            subtopics = generate_subtopics(
                current_topics[0],
                think_mode_enabled,
                topic_generator_2,
                ProjectAutocreatorT.Template_2
            )
            
            current_topics.extend(subtopics)
            print("# -> Подтемы:")
            pprint.pprint(current_topics[1:])
            
            # Генерация введения для главы
            print(f"# -> (START) Генерирование введения в главу {current_topics[0]}")
            result_text += "\n" + LLMFunc.DeleteThinking(AI_Basic.invoke(
                ProjectAutocreatorT.Template_5.invoke({
                    "Topic": current_topics[0],
                    "AllTopics": "\n".join(current_topics[1:]),
                    "ThinkMode": "/nothink" if not think_mode_enabled else ""
                })
            ).content) + "\n"
            
            # Генерация контента для каждой подтемы
            for subtopic in current_topics[1:]:
                print(f"# -> (START) Генерирование подглавы {subtopic}")
                result_text += "\n" + LLMFunc.DeleteThinking(AI_Basic.invoke(
                    ProjectAutocreatorT.Template_6.invoke({
                        "Subtopic": subtopic,
                        "Topic": current_topics[0],
                        "AllTopics": "\n".join(current_topics[1:]),
                        "ThinkMode": "/nothink" if not think_mode_enabled else ""
                    })
                ).content) + "\n"
        else:
            print(f"# -> Генерирование главы: {topic}")
            result_text += "\n" + LLMFunc.DeleteThinking(AI_Basic.invoke(
                ProjectAutocreatorT.Template_7.invoke({
                    "Topic": topic,
                    "MainTopic": main_topic,
                    "AllTopics": "\n".join(structure.Topics),
                    "ThinkMode": "/nothink" if not think_mode_enabled else ""
                })
            ).content) + "\n"
        
        full_structure.extend(current_topics)
    
    # Добавление введения и заключения
    result_text = (
        "\n" + LLMFunc.DeleteThinking(AI_Basic.invoke(
            ProjectAutocreatorT.Template_3.invoke({
                "Themes": "\n".join(full_structure),
                "ThinkMode": "/nothink" if not think_mode_enabled else ""
            })    
        ).content) + "\n" + result_text
    )
    
    result_text += "\n" + LLMFunc.DeleteThinking(AI_Basic.invoke(
        ProjectAutocreatorT.Template_4.invoke({
            "Themes": "\n".join(full_structure),
            "ThinkMode": "/nothink" if not think_mode_enabled else ""
        })    
    ).content) + "\n"
    
    result_text = LLMFunc.FixLLMFormula(result_text)
    
    # Сохранение результатов
    file_name = main_topic.replace(".", "")
    with open(file_name + ".md", "w", encoding="utf-8") as file:
        file.write(result_text)
    
    if generate_pdf:
        pdf = markdown_pdf.MarkdownPdf(toc_level=1)
        pdf.add_section(Section(result_text, toc=False))
        pdf.save(file_name + ".pdf")
    
    print("# -> Файл успешно сохранен!")
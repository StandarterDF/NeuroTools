import gradio as gr
import os
import threading
import datetime
import re
import pprint
import time
import markdown_pdf
from langchain_openai import ChatOpenAI
from markdown_pdf import Section

import Config
import LLMLibrary.ProjectFunctions as LLMFunc
from LLMLibrary.ProjectAI import ProjectAI_Tools
import ProjectAutocreatorT

# Инициализация
PAI = ProjectAI_Tools()

Models = {}
for provider in Config.OpenAI_API_Providers.keys():
    Models[provider] = PAI.models2list(
        PAI.get_models(Config.OpenAI_API_Providers[provider]["base_url"])
    )

#
ModuleName = "Autocreator"
#
Providers = list(Config.OpenAI_API_Providers.keys())
Provider_Info = Providers[0] if Providers else ""
Provider_Func = Providers[0] if Providers else ""
SModel_Info = Models[Provider_Info][0] if Provider_Info in Models and Models[Provider_Info] else ""
SModel_Func = Models[Provider_Func][0] if Provider_Func in Models and Models[Provider_Func] else ""

# Глобальные переменные
LogsText = "---------LOG STARTED--------\n"
CurrentGeneration = False
FinalFile = ""
generation_thread = None
stop_generation_flag = False

# Блокировка для потокобезопасности
import threading
log_lock = threading.Lock()

# Функции логирования
def logprint(Text):
    global LogsText
    with log_lock:
        current_time = datetime.datetime.now().strftime("(%H:%M:%S)")
        print(f"{current_time}" + str(Text), end="")
        LogsText += str(f"{current_time}" + str(Text))
        return LogsText

def logprintln(Text):
    global LogsText
    with log_lock:
        current_time = datetime.datetime.now().strftime("(%H:%M:%S)")
        print(f"{current_time}" + str(Text))
        LogsText += str(f"{current_time}" + str(Text)) + "\n"
        return LogsText

def logclear():
    global LogsText
    with log_lock:
        LogsText = "---------LOG STARTED--------\n"
        return LogsText

# Функции изменения моделей
def ChangeModel_Info(Value):
    global SModel_Info
    SModel_Info = Value
    print("# Logs (Update Model):", [SModel_Info])
    return gr.update()

def ChangeModel_Func(Value):
    global SModel_Func
    SModel_Func = Value
    print("# Logs (Update Model):", [SModel_Func])
    return gr.update()

# Функция для обновления моделей при смене провайдера
def update_models_info(provider):
    if provider in Models:
        return gr.update(choices=Models[provider], value=Models[provider][0] if Models[provider] else "")
    return gr.update(choices=[], value="")

def update_models_func(provider):
    if provider in Models:
        return gr.update(choices=Models[provider], value=Models[provider][0] if Models[provider] else "")
    return gr.update(choices=[], value="")

# Функция для получения текущих логов (для обновления в реальном времени)
def get_current_logs():
    with log_lock:
        return LogsText

# Основная функция генерации проекта (выполняется в отдельном потоке)
def GenerateProjectThread(
    Topic,
    TopicCount,
    SubTopicGen,
    ThinkMode,
    GenPDF,
    ModelInfo,
    ModelFunc,
    ProviderInfo,
    ProviderFunc
):
    global LogsText, FinalFile, stop_generation_flag
    
    try:
        # Настройка моделей
        Config.OpenAI_API_Providers[ProviderInfo]["model"] = ModelInfo
        AI_Basic = ChatOpenAI(**Config.OpenAI_API_Providers[ProviderInfo])
        Config.OpenAI_API_Providers[ProviderFunc]["model"] = ModelFunc
        AI_Function = ChatOpenAI(**Config.OpenAI_API_Providers[ProviderFunc])

        AI_Topic_G1 = AI_Function.with_structured_output(ProjectAutocreatorT.TopicGenerator)
        AI_Topic_G2 = AI_Function.with_structured_output(ProjectAutocreatorT.TopicGeneratorA1)

        Structure = []
        FullStructure = []
        ResultText = ""

        #########################################################
        # Generate basic structure
        #########################################################
        i = 0
        max_attempts = 3
        while i < max_attempts and not stop_generation_flag:
            i += 1
            logprintln(f"# -> Генерирование структуры (Попытка {i})")
            try:
                Structure = AI_Topic_G1.invoke(
                    ProjectAutocreatorT.Template_1.invoke(
                        {
                            "Topic": Topic,
                            "TopicCount": str(TopicCount),
                            "ThinkMode": "/nothink" if not ThinkMode else "",
                        }
                    )
                )
                logprintln(f"Структура получена: {Structure}")
                if hasattr(Structure, 'Topics') and Structure.Topics:
                    break
                else:
                    logprintln("Получена пустая структура, повторная попытка...")
            except Exception as e:
                logprintln(f"Ошибка при генерации структуры: {str(e)}")
                if i >= max_attempts:
                    raise
                time.sleep(1)

        if stop_generation_flag:
            logprintln("Генерация прервана пользователем")
            return

        if not hasattr(Structure, 'Topics') or not Structure.Topics:
            raise Exception("Не удалось сгенерировать структуру после всех попыток")

        #########################################################
        # Генерация контента
        #########################################################
        total_topics = len(Structure.Topics)
        for idx, SElement in enumerate(Structure.Topics):
            if stop_generation_flag:
                logprintln("Генерация прервана пользователем")
                return
                
            logprintln(f"Обработка темы [{idx+1}/{total_topics}]: {SElement}")
            
            CurrentTopics = [SElement]
            if SubTopicGen and len(SElement) > 0:
                """
                Генерация дополнительных подтем.
                """
                logprintln(f"# -> ({SElement}) Генерирование подтемы...")
                try:
                    Result = AI_Topic_G2.invoke(
                        ProjectAutocreatorT.Template_2.invoke(
                            {
                                "CurrTopic": CurrentTopics[0],
                                "ThinkMode": "/nothink" if not ThinkMode else "",
                                "CurNum": re.search("[0-9]{1,}\.", SElement).group() if re.search("[0-9]{1,}\.", SElement) else "1.",
                            }
                        )
                    ).Topics
                    CurrentTopics.extend(Result)
                    logprintln("# -> Подтемы:")
                    pprint.pprint(CurrentTopics[1:])
                except Exception as e:
                    logprintln(f"Ошибка при генерации подтем: {str(e)}")

                logprintln(f"# -> (START) Генерирование введения в главу {CurrentTopics[0]}")
                try:
                    content = AI_Basic.invoke(
                        ProjectAutocreatorT.Template_5.invoke(
                            {
                                "Topic": CurrentTopics[0],
                                "AllTopics": "\n".join(CurrentTopics[1:]) if len(CurrentTopics) > 1 else "",
                                "ThinkMode": "/nothink" if not ThinkMode else "",
                            }
                        )
                    ).content
                    ResultText += "\n" + LLMFunc.DeleteThinking(content) + "\n"
                except Exception as e:
                    logprintln(f"Ошибка при генерации введения: {str(e)}")

                for SubElement in CurrentTopics[1:]:
                    if stop_generation_flag:
                        logprintln("Генерация прервана пользователем")
                        return
                    logprintln(f"# -> (START) Генерирование подглавы {SubElement}")
                    try:
                        content = AI_Basic.invoke(
                            ProjectAutocreatorT.Template_6.invoke(
                                {
                                    "Subtopic": SubElement,
                                    "Topic": CurrentTopics[0],
                                    "AllTopics": "\n".join(CurrentTopics[1:]) if len(CurrentTopics) > 1 else "",
                                    "ThinkMode": "/nothink" if not ThinkMode else "",
                                }
                            )
                        ).content
                        ResultText += "\n" + LLMFunc.DeleteThinking(content) + "\n"
                    except Exception as e:
                        logprintln(f"Ошибка при генерации подглавы: {str(e)}")
            else:
                """
                Генерация простой главы
                """
                logprintln(f"# -> Генерирование главы: {SElement}")
                try:
                    content = AI_Basic.invoke(
                        ProjectAutocreatorT.Template_7.invoke(
                            {
                                "Topic": SElement,
                                "MainTopic": Topic,
                                "AllTopics": "\n".join(Structure.Topics),
                                "ThinkMode": "/nothink" if not ThinkMode else "",
                            }
                        )
                    ).content
                    ResultText += "\n" + LLMFunc.DeleteThinking(content) + "\n"
                except Exception as e:
                    logprintln(f"Ошибка при генерации главы: {str(e)}")
            
            FullStructure.extend(CurrentTopics)

        # Добавление введения и заключения
        if not stop_generation_flag:
            logprintln("Финализация...")
            try:
                intro_content = AI_Basic.invoke(
                    ProjectAutocreatorT.Template_3.invoke(
                        {
                            "Themes": "\n".join(FullStructure),
                            "ThinkMode": "/nothink" if not ThinkMode else "",
                        }
                    )
                ).content
                ResultText = "\n" + LLMFunc.DeleteThinking(intro_content) + "\n" + ResultText
            except Exception as e:
                logprintln(f"Ошибка при добавлении введения: {str(e)}")

            try:
                conclusion_content = AI_Basic.invoke(
                    ProjectAutocreatorT.Template_4.invoke(
                        {
                            "Themes": "\n".join(FullStructure),
                            "ThinkMode": "/nothink" if not ThinkMode else "",
                        }
                    )
                ).content
                ResultText += "\n" + LLMFunc.DeleteThinking(conclusion_content) + "\n"
            except Exception as e:
                logprintln(f"Ошибка при добавлении заключения: {str(e)}")
        
        # Очистка имени файла
        if stop_generation_flag:
            logprintln("Генерация прервана пользователем")
            return
            
        FileName = re.sub(r'[^\w\-_\. ]', '', Topic).replace(".", "_")
        if not FileName or FileName.strip() == "":
            FileName = "project"
        
        # Создание директории если не существует
        os.makedirs("Docs", exist_ok=True)
        os.makedirs(f"Docs/{ModuleName}", exist_ok=True)

        ResultText = LLMFunc.FixLLMFormula(ResultText)

        with open(f"Docs/{ModuleName}/{FileName}.md", "w", encoding="utf-8") as FileWriter:
            FileWriter.write(ResultText)
            
        if GenPDF:
            try:
                PDF = markdown_pdf.MarkdownPdf(toc_level=1)
                PDF.add_section(Section(ResultText, toc=False))
                PDF.save(f"Docs/{ModuleName}/{FileName}.pdf")
            except Exception as e:
                logprintln(f"Ошибка при создании PDF: {str(e)}")
            
        logprintln("# -> Файл успешно сохранен!")
        FinalFile = f"{ModuleName}/{FileName}.pdf"
        
    except Exception as e:
        error_msg = f"# -> Ошибка: {str(e)}"
        logprintln(error_msg)
    finally:
        global CurrentGeneration
        CurrentGeneration = False
        stop_generation_flag = False

# Функция для запуска генерации в отдельном потоке
def start_generation(topic, topic_count, sub_topic_gen, think_mode, gen_pdf, model_info, model_func, provider_info, provider_func):
    global CurrentGeneration, generation_thread, stop_generation_flag
    
    if CurrentGeneration:
        logprintln("Генерация уже запущена")
        return get_current_logs(), gr.Markdown("Генерация уже запущена"), "Генерация уже запущена"
    
    if not topic or not topic_count:
        error_msg = "Пожалуйста, заполните тему и количество глав"
        logprintln(error_msg)
        return get_current_logs(), gr.Markdown(error_msg), "Ошибка"
    
    # Очищаем логи и запускаем генерацию
    logclear()
    logprintln("#-------------------------------------------------#")
    logprintln("# -> PROJECT: Auto Creator")
    logprintln("#-------------------------------------------------#")
    
    CurrentGeneration = True
    stop_generation_flag = False
    
    # Запускаем генерацию в отдельном потоке
    generation_thread = threading.Thread(
        target=GenerateProjectThread,
        args=(topic, topic_count, sub_topic_gen, think_mode, gen_pdf, model_info, model_func, provider_info, provider_func)
    )
    generation_thread.daemon = True
    generation_thread.start()
    
    return get_current_logs(), gr.Markdown("Генерация запущена..."), "Запущено"

# Функция для остановки генерации
def stop_generation():
    global CurrentGeneration, stop_generation_flag, generation_thread
    if CurrentGeneration:
        stop_generation_flag = True
        logprintln("Остановка генерации...")
        CurrentGeneration = False
        generation_thread = None
        return get_current_logs(), gr.Markdown("Генерация остановлена"), "Остановлено"
    else:
        return get_current_logs(), gr.Markdown("Генерация не запущена"), "Не запущено"

# Функция для очистки логов
def clear_logs():
    return logclear()

# Функция для обновления списка файлов
def update_file_list():
    try:
        os.makedirs(f"Docs/{ModuleName}", exist_ok=True)
        if not os.path.exists(f"Docs/{ModuleName}"):
            return gr.Markdown("Директория не существует")
            
        Files = [File for File in os.listdir(f"Docs/{ModuleName}/") if os.path.isfile(f"Docs/{ModuleName}/{File}")]
        Files = [File for File in Files if File.endswith((".pdf", ".md"))]
        Files.sort(key=lambda x: -os.stat(f"Docs/{ModuleName}/{x}").st_ctime)
        Files = Files[:10]
        
        if not Files:
            return gr.Markdown("Нет сгенерированных файлов")
        
        # Создаем HTML список файлов
        file_list_html = "<div>"
        for File in Files:
            file_path = f"/file={os.path.abspath(f'Docs/{ModuleName}/{File}')}"
            file_list_html += f'<div><a href="{file_path}" target="_blank">{File}</a></div>'
        file_list_html += "</div>"
        
        return gr.HTML(file_list_html)
        
    except Exception as e:
        return gr.Markdown(f"Ошибка при загрузке файлов: {str(e)}")

# Функция для обновления логов в реальном времени
def update_logs():
    return get_current_logs()

# Создание интерфейса Gradio
with gr.Blocks(title="AutoCreator") as demo:
    gr.Markdown("# AutoCreator: UI")
    
    # Таймер для обновления логов
    logs_update_timer = gr.Timer(1)  # Обновление каждую секунду
    
    with gr.Row():
        with gr.Column(scale=2):
            logs_output = gr.TextArea(label="Логи создания", lines=25, interactive=False, value=LogsText)
            with gr.Row():
                generate_btn = gr.Button("Генерировать")
                stop_btn = gr.Button("Остановить")
                clear_logs_btn = gr.Button("Очистить логи")
                
        with gr.Column():
            topic_input = gr.Text(label="Тема проекта", placeholder="Заданная тема (Пример: Нейросети)")
            topic_count_input = gr.Number(label="Количество глав", value=3, minimum=1, maximum=20)
            
            with gr.Accordion("Модели", open=True):
                with gr.Column():
                    Model_Info = gr.Dropdown(
                        choices=Models.get(Provider_Info, []) if Provider_Info in Models else [],
                        value=SModel_Info if SModel_Info in (Models.get(Provider_Info, []) or []) else (Models.get(Provider_Info, [""])[0] if Models.get(Provider_Info, []) else ""),
                        label="Информационная модель", 
                        info="Модель, которая будет использоваться для генерации текстов (Самая умная модель)"
                    )
                    Model_Func = gr.Dropdown(
                        choices=Models.get(Provider_Func, []) if Provider_Func in Models else [],
                        value=SModel_Func if SModel_Func in (Models.get(Provider_Func, []) or []) else (Models.get(Provider_Func, [""])[0] if Models.get(Provider_Func, []) else ""),
                        label="Функциональная модель", 
                        info="Модель, которая будет использоваться для Functional Calling"
                    )
                    # Changers
                    Model_Info.change(fn=ChangeModel_Info, inputs=Model_Info)
                    Model_Func.change(fn=ChangeModel_Func, inputs=Model_Func)
                    
            with gr.Accordion("Конфигурации (OpenAI API)", open=False):
                with gr.Column():
                    Provider_Info_Selector = gr.Dropdown(
                        choices=Providers, 
                        value=Provider_Info if Provider_Info in Providers else (Providers[0] if Providers else ""),
                        label="Информационный провайдер"
                    )
                    Provider_Func_Selector = gr.Dropdown(
                        choices=Providers, 
                        value=Provider_Func if Provider_Func in Providers else (Providers[0] if Providers else ""),
                        label="Функциональный провайдер"
                    )
                    # Обновление моделей при смене провайдера
                    Provider_Info_Selector.change(fn=update_models_info, inputs=Provider_Info_Selector, outputs=Model_Info)
                    Provider_Func_Selector.change(fn=update_models_func, inputs=Provider_Func_Selector, outputs=Model_Func)
                    
            with gr.Accordion("Дополнительные опции", open=False):
                gen_pdf_checkbox = gr.Checkbox(label="Generate PDF", value=True, info="Будет преобразовать сгенерированный Markdown контент проекта в PDF файл")
                sub_topic_gen_checkbox = gr.Checkbox(label="Генерировать подглавы", value=False, info="Вместо использования главы как единицы позволяет увеличить объем итогового текста, структурируя подглавы")
                think_mode_checkbox = gr.Checkbox(label="Рассуждать перед генерацией главы", value=False, info="В Reasoning моделях позволяет проводить рассуждения перед ответом (Помогает в проектах со сложной структурой)")
    
    with gr.Column():
        with gr.Accordion("Последние генерации", open=False):
            files_output = gr.Markdown("Файлы будут отображаться здесь")
    
    # Статус генерации
    status_output = gr.Textbox(label="Статус", visible=True)
    
    # Обработчики событий
    generate_btn.click(
        fn=start_generation,
        inputs=[
            topic_input, topic_count_input, sub_topic_gen_checkbox, 
            think_mode_checkbox, gen_pdf_checkbox, Model_Info, Model_Func,
            Provider_Info_Selector, Provider_Func_Selector
        ],
        outputs=[logs_output, files_output, status_output]
    )
    
    stop_btn.click(
        fn=stop_generation,
        outputs=[logs_output, files_output, status_output]
    )
    
    clear_logs_btn.click(
        fn=clear_logs,
        outputs=[logs_output]
    )
    
    # Автоматическое обновление логов
    logs_update_timer.tick(
        fn=update_logs,
        outputs=[logs_output]
    )
    
    # Автоматическое обновление списка файлов при запуске
    demo.load(fn=update_file_list, outputs=[files_output])

if __name__ == "__main__":
    demo.launch()
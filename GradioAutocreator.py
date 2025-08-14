import gradio as gr
import os
import Config
import LLMLibrary.ProjectFunctions as LLMFunc
from LLMLibrary.ProjectAI import ProjectAI_Tools

import GradioInitialize
if __name__ != "__main__":

    Models = GradioInitialize.Models
    
    #
    ModuleName = "Autocreator"
    #
    Providers = list(Config.OpenAI_API_Providers.keys())
    Provider_Info = Providers[0]
    Provider_Func = Providers[0]
    SModel_Info = Models[Provider_Info][0]
    SModel_Func = Models[Provider_Func][0]
    #
    def ChangeModel_Info(Value):
        global SModel_Info
        SModel_Info = Value
        print("# Logs (Update Model):", [SModel_Info])
    def ChangeModel_Func(Value):
        global SModel_Func
        SModel_Func = Value
        print("# Logs (Update Model):", [SModel_Func])
    #
    gr.Markdown("# AutoCreator: UI")
    with gr.Row():
        with gr.Column("Логи создания", scale=2):
            gr.TextArea(lines=25, interactive=False)
            with gr.Row():
                gr.Button("Генерировать")
                gr.Button("Подтвердить")
                gr.Button("Остановить")
        with gr.Column():
            gr.Text(label="Тема проекта", placeholder="Заданная тема (Пример: Нейросети)")
            gr.Number(label="Количество глав")
            with gr.Accordion("Модели", open=True):
                with gr.Column():
                    Model_Info = gr.Dropdown(choices=Models[Provider_Info], label="Информационная модель", info="Модель, которая будет использоваться для генерации текстов (Самая умная модель)")
                    Model_Func = gr.Dropdown(choices=Models[Provider_Func], label="Функциональная модель", info="Модель, которая будет использоваться для Functional Calling")
                    # Changers
                    Model_Info.change(fn=lambda x: ChangeModel_Info(x), inputs=Model_Info)
                    Model_Func.change(fn=lambda x: ChangeModel_Func(x), inputs=Model_Func)
                    print("# Models updated:", [SModel_Info, SModel_Func])
                    
                    
            with gr.Accordion("Конфигурации (OpenAI API)", open=False):
                with gr.Column():
                    Provider_Func_Selector = gr.Dropdown(choices=Providers, value=Provider_Info, label="Информационный провайдер")
                    Provider_Info_Selector = gr.Dropdown(choices=Providers, value=Provider_Func, label="Функциональный провайдер")
                    # Changers
                    Provider_Info_Selector.change(fn=lambda x: 0, inputs=Provider_Info_Selector)
                    Provider_Func_Selector.change(fn=lambda x: 0, inputs=Provider_Func_Selector)
            with gr.Accordion("Дополнительные опции", open=False):
                gr.Checkbox(label="Generate PDF", info="Будет преобразовать сгенерированный Markdown контент проекта в PDF файл")
                gr.Checkbox(label="Генерировать подглавы", info="Вместо использования главы как единицы позволяет увеличить объем итогового текста, структурируя подглавы")
                gr.Checkbox(label="Рассуждать перед генерацией главы", info="В Reasoning моделях позволяет проводить рассуждения перед ответом (Помогает в проектах со сложной структурой)")
    with gr.Column():
        with gr.Accordion("Последние генерации", open=False):
            Files = [File for File in os.listdir(f"Docs/{ModuleName}/") if os.path.isfile(f"Docs/{ModuleName}/{File}")]
            Files = [File for File in os.listdir(f"Docs/{ModuleName}/") if File.endswith(".pdf")]
            Files.sort(key=lambda x: -os.stat(f"Docs/{ModuleName}/{x}").st_ctime)
            Files = Files[:10]
            for File in Files:
                gr.File(f"Docs/{ModuleName}/{File}", show_label=False)
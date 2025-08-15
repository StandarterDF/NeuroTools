import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("## Мой простой выпадающий список")

    # Просто создаем Dropdown
    animal_dropdown = gr.Dropdown(
        choices=["Кошка", "Собака", "Попугай", "Хомяк"], # Список вариантов
        label="Выберите животное",
        value="Кошка", # Опционально: значение по умолчанию
        info="Можно выбрать только одно животное" # Опционально: подсказка
    )
    def show_selected(animal):
        return f"Выбрано: {animal}"
    animal_dropdown.change(fn=show_selected, inputs=animal_dropdown)


if __name__ == "__main__":
    demo.launch()
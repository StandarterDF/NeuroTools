from datetime import datetime
import LLMLibrary.ProjectFunctions as LLMFunc
from langchain_openai import ChatOpenAI
from markdown_pdf import Section
import ProjectAutoanswerT
import markdown_pdf
import Config
import pprint
import re

# ----- PROGRAM START -----
print("#-------------------------------------------------#")
print("# -> PROJECT: Auto Answer")
print("#-------------------------------------------------#")
from ProjectTemplate import *
# -------------------------
if __name__ == "__main__":
    ResultData = ""
    FileData = LLMFunc.ReadFile(input("# -> Файл с вопросами: "))
    FileName = input("# -> Файл вывода результатов: ")
    QuestionTopic = input("# -> Тематика вопросов (None = Auto): ")
    QuestionLength = input("# -> Отвечать нужно так: ")
    QuestionParser = AI_Function.with_structured_output(ProjectAutoanswerT.QuestionParser)
    Questions = QuestionParser.invoke(FileData, temperature = 0)
    print("#-------------------------------------------------#")
    print("Все вопросы:")
    pprint.pprint(Questions)
    print("#-------------------------------------------------#")
    ResultData += "\n# " + f"Нейро ({QuestionTopic})" + "\n"
    ResultData += "\n".join(Questions.Questions)
    for Question in Questions.Questions:
        LLMFunc.TimedPrint(f"LLMGeneration -> {Question}", flush=True, end="")
        ResultData += "\n# " + Question + "\n"
        ResultData += LLMFunc.DeleteThinking(AI_Basic.invoke(
            ProjectAutoanswerT.Template_1.invoke({"QuestionTopic": QuestionTopic, "Question": Question, "Length": QuestionLength})
        ).content)
        print(" (Done)", flush=True)
    with open(FileName + ".md", "w", encoding="utf-8") as FileWriter:
        FileWriter.write(ResultData)
    PDF = markdown_pdf.MarkdownPdf(toc_level=3)
    PDF.add_section(Section(ResultData, toc=False))
    PDF.save(FileName + ".pdf")
    print("# -> Файл успешно сохранен!")
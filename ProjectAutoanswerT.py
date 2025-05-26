from typing import List
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

class QuestionParser(BaseModel):
    Questions: List[str] = Field(description="Список всех вопросов, которые тут есть. У каждого вопроса должен быть порядковый номер. Так же важно, чтоб были затронуты все вопросы из файла.")

Template_1 = PromptTemplate.from_template(
    """
    Твоя задача ответить на вопрос по теме {QuestionTopic}.
    Ты профессионал в этой теме, но нужно объяснить так, чтоб было просто.
    Отвечать нужно так: {Length}
    чтоб максимально дать понимание всего вопроса.
    Ничего, кроме самого ответа на вопрос быть не должно:
    Сам вопрос, на который нужно ответить: {Question}
    """
)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
import Config

class TopicGenerator(BaseModel):
    Topics: List[str] = Field(description="Список всех глав для проекта")

class TopicGeneratorA1(BaseModel):
    Topics: List[str] = Field(description="Подглавы для главы")

class ProjectAI:
    def __init__(self):
        self.AI = ChatOpenAI(
            base_url=Config.OpenAI_API_BaseURL,
            api_key=Config.OpenAI_API_Key,
            model=Config.OpenAI_API_Model
        )
        self.TopicAI = self.AI.with_structured_output(TopicGenerator)
        self.TopicA1AI = self.AI.with_structured_output(TopicGeneratorA1)
    
    def GenerateResponse(self, text, model=Config.OpenAI_API_Providers["OpenAI_API_Default"], disable_think=True):
        return self.AI.invoke(text + ("/nothink" if disable_think else "")).content
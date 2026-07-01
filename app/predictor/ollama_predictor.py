from typing import AsyncGenerator
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.settings import settings
from app.predictor.constants import default_translate_system_prompt, default_system_prompt
from app.predictor.predictor import Predictor


class OllamaPredictor(Predictor):
    async def translate(self, language_code: str, text: str) -> str:
        llm = ChatOllama(model=settings.MODEL_NAME, temperature=0.2)
        prompt = ChatPromptTemplate.from_messages([
            ('system', default_translate_system_prompt),
            ('human', '{text}')
        ])
        chain = prompt | llm | StrOutputParser()
        translated_text = await chain.ainvoke({'language_code': language_code, 'text': text})
        return translated_text

    async def generate_prediction(self, language_code: str) -> AsyncGenerator[str, None]:
        llm = ChatOllama(model=settings.MODEL_NAME, temperature=settings.TEMPERATURE)
        prompt = ChatPromptTemplate.from_messages([
            ('system', default_system_prompt),
            ('human', 'Predict the future.')
        ])
        chain = prompt | llm

        async for chunk in chain.astream({'language_code': language_code}):
            if chunk.content:
                yield chunk.content

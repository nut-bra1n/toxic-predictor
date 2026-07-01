from typing import AsyncGenerator
from abc import ABC, abstractmethod


class Predictor(ABC):
    @abstractmethod
    async def translate(self, language_code: str, text: str) -> str:
        pass

    @abstractmethod
    async def generate_prediction(self, language_code: str) -> AsyncGenerator[str, None]:
        pass

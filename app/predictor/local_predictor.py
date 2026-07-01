import pathlib
import torch
from typing import AsyncGenerator
from threading import Thread
from transformers import AutoTokenizer, AutoModelForCausalLM, AsyncTextIteratorStreamer

from app.settings import settings
from app.predictor.constants import default_translate_system_prompt, default_system_prompt
from app.predictor.predictor import Predictor


class LocalPredictor(Predictor):
    def __init__(self):
        self.__device = 'cuda' if torch.cuda.is_available() else 'cpu'

        model_path = pathlib.Path(settings.LOCAL_MODEL_PATH)
        if model_path.is_file() and len(model_path.name.split('.')) > 0 and model_path.name.split('.')[-1] == 'gguf':
            model_dir = model_path.parent
            model_file = model_path.name
            self.__tokenizer = AutoTokenizer.from_pretrained(model_dir, gguf_file=model_file)
            self.__model = AutoModelForCausalLM.from_pretrained(model_dir,
                                                                gguf_file=model_file,
                                                                device_map='auto',
                                                                torch_dtype=torch.float16 if self.__device ==
                                                                                             'cuda' else torch.float32)
        else:
            self.__tokenizer = AutoTokenizer.from_pretrained(settings.LOCAL_MODEL_PATH)
            self.__model = AutoModelForCausalLM.from_pretrained(settings.LOCAL_MODEL_PATH,
                                                                device_map='auto',
                                                                torch_dtype=torch.float16 if self.__device ==
                                                                                             'cuda' else torch.float32)

    async def translate(self, language_code: str, text: str) -> str:
        messages = [
            {'role': 'system', 'content': default_translate_system_prompt.format(language_code)},
            {'role': 'user', 'content': text}
        ]
        prompt = self.__tokenizer.apply_chat_template(messages,
                                                      tokenize=True,
                                                      add_generation_prompt=True,
                                                      return_tensors='pt')
        streamer = AsyncTextIteratorStreamer(self.__tokenizer, skip_prompt=True, skip_special_tokens=True)
        generation_kwargs = dict(
            input_ids=prompt,
            streamer=streamer,
            max_new_tokens=512,
            temperature=settings.TEMPERATURE
        )
        thread = Thread(target=self.__model.generate, kwargs=generation_kwargs)
        thread.start()

        translated_text = ''

        async for chunk in streamer:
            translated_text += chunk

        return translated_text

    async def generate_prediction(self, language_code: str) -> AsyncGenerator[str, None]:
        messages = [
            {'role': 'system', 'content': default_system_prompt.format(language_code)},
            {'role': 'user', 'content': 'Predict the future.'}
        ]
        prompt = self.__tokenizer.apply_chat_template(messages,
                                                      tokenize=True,
                                                      add_generation_prompt=True,
                                                      return_tensors='pt')
        streamer = AsyncTextIteratorStreamer(self.__tokenizer, skip_prompt=True, skip_special_tokens=True)
        generation_kwargs = dict(
            input_ids=prompt,
            streamer=streamer,
            max_new_tokens=512,
            temperature=settings.TEMPERATURE
        )
        thread = Thread(target=self.__model.generate, kwargs=generation_kwargs)
        thread.start()

        async for chunk in streamer:
            yield chunk

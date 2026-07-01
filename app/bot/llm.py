import os
import sys
from loguru import logger
from dotenv import load_dotenv
from app.settings import settings


load_dotenv()
if os.environ.get('LOCAL_MODEL_PATH'):
    from app.predictor.local_predictor import LocalPredictor
    predictor = LocalPredictor()
elif os.environ.get('OPENAI_API_BASE'):
    if not os.environ.get('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY
    if not settings.MODEL_NAME:
        logger.error('MODEL_NAME is not set. Check .env file.')
        sys.exit(-1)
    from app.predictor.openai_predictor import OpenAIPredictor
    predictor = OpenAIPredictor()
elif os.environ.get('OLLAMA_BASE_URL'):
    if not settings.MODEL_NAME:
        logger.error('MODEL_NAME is not set. Check .env file.')
        sys.exit(-1)
    from app.predictor.ollama_predictor import OllamaPredictor
    predictor = OllamaPredictor()
else:
    logger.error('Environment variables LOCAL_MODEL_PATH, OPENAI_API_BASE, OLLAMA_BASE_URL are not set. Check .env file.')
    sys.exit(-1)

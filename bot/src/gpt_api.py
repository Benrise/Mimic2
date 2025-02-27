import logging
import random
import joblib

from typing import List
from openai import AsyncOpenAI
from httpx import AsyncClient
from uuid import UUID

from .classifier import ModelClassifier
from .utils import human_sleep, introduce_typos
from .database import select_messages_by_dialog
from .schemas import GetMessageRequestModel
from .config import (
    PROXY_URL, 
    OPEN_AI_API_KEY, 
    BOTHUB_API_KEY,
    BOTHUB_API_BASE_URL,
    SYS_PROMPT, 
    BOT_MODEL,
    BOT_NAMES,
    BOT_REGISTERS,
    BOT_AGES,
    BOT_SPECIALIZATION,
    BOT_FAVORITE_TRASH_WORDS,
    BOT_GREETINGS
)

logger = logging.getLogger(__name__)

_classifier = None

def load_classifier():
    global _classifier
    if _classifier is None:
        logger.info("Loading classifier...")
        _classifier = ModelClassifier()
    return _classifier

if BOTHUB_API_KEY and BOTHUB_API_BASE_URL:
    logger.info("Using BotHub API")
    api_key = BOTHUB_API_KEY
    base_url = BOTHUB_API_BASE_URL
    http_client = None 
elif OPEN_AI_API_KEY and PROXY_URL:
    logger.info("Using Alex's OpenAI API")
    api_key = OPEN_AI_API_KEY
    base_url = None 
    http_client = AsyncClient(proxy=PROXY_URL) if PROXY_URL else None
else:
    logger.error("Neither BotHub API nor OpenAI API credentials found.")

client = AsyncOpenAI(
    api_key=api_key,
    base_url=base_url,
    http_client=http_client,
)


async def build_openai_messages(dialog_id: UUID, last_msg_text: str) -> List[dict]:
    """
    Собирает весь контекст диалога из БД, преобразует
    в формат сообщений для ChatCompletion (role: user/assistant).
    Добавляет текущее новое сообщение пользователя в конце.
    
    participant_index=0 => user, participant_index=1 => assistant
    """
    sys_prompt_filled = SYS_PROMPT.format(
        random_name=random.choice(BOT_NAMES),
        random_register=random.choice(BOT_REGISTERS),
        random_age=random.choice(BOT_AGES),
        random_specialization=random.choice(BOT_SPECIALIZATION),
        random_favorite_trash_word=random.choice(BOT_FAVORITE_TRASH_WORDS),
        random_greeting=random.choice(BOT_GREETINGS),
    )
    
    db_messages = select_messages_by_dialog(dialog_id)

    messages_for_openai = []
    messages_for_openai.append({"role": "system", "content": sys_prompt_filled})

    for msg in db_messages:
        role = "user" if msg["participant_index"] == 0 else "assistant"
        messages_for_openai.append({"role": role, "content": msg["text"]})

    messages_for_openai.append({"role": "user", "content": last_msg_text})
    return messages_for_openai


async def query_openai_with_context(body: GetMessageRequestModel) -> str:
    """
    Формирует сообщения для OpenAI, включая весь контекст диалога,
    затем отправляет запрос и возвращает текст ответа.
    """
    model = BOT_MODEL
    
    logger.info(f"Using model: {model}")

    messages = await build_openai_messages(body.dialog_id, body.last_msg_text)

    chat_completion = await client.chat.completions.create(
        messages=messages,
        model=model,
    )
    logger.info(str(chat_completion))

    answer_text = chat_completion.choices[0].message.content
    logger.info(f"OpenAI answer: {answer_text}")
    
    answer_text = await retry_if_botlike(answer_text, messages)
    
    human_sleep(answer_text)
    return answer_text


async def query_openai_with_local_context(dialog: list) -> str:
    """
    Формирует сообщения для OpenAI, с локальным контекстом диалога,
    затем отправляет запрос и возвращает текст ответа.
    """
    model = BOT_MODEL
    
    logger.info(f"Using model: {model}")
    
    chat_completion = await client.chat.completions.create(
        messages=dialog,
        model=model,
    )
    
    logger.info(str(chat_completion))
    
    answer_text = introduce_typos(chat_completion.choices[0].message.content)
    
    logger.info(f"OpenAI answer: {answer_text}")
    
    answer_text = await retry_if_botlike(answer_text, dialog)
    
    human_sleep(answer_text)
    return answer_text

async def retry_if_botlike(answer_text: str, messages: List[dict], max_retries: int = 1) -> str:
    """
    Проверяет, является ли ответ ботоподобным. 
    Если да, то запрашивает OpenAI на перегенерацию.
    """
    classifier = load_classifier()
    
    modified_messages = messages.copy()

    for attempt in range(max_retries + 1):
        if classifier.predict(answer_text) == 0:
            return answer_text

        if attempt < max_retries:
            logger.warning(f"Retrying response, detected as bot-like (attempt {attempt + 1})")

            modified_messages.append({
                "role": "user",
                "content": "[СИСТЕМА] Сгенерированное тобой сообщение не прошло проверку на бота. Перегенерируй его."
            })
            
            logger.warning(f"Bot detected message before: {answer_text}")

            chat_completion = await client.chat.completions.create(
                messages=modified_messages,
                model=BOT_MODEL,
            )
            answer_text = chat_completion.choices[0].message.content
            
            logger.warning(f"Bot detected message after: {answer_text}")

        else:
            logger.error("Max retries reached, returning last response.")
            break

    if modified_messages != messages:
        modified_messages.pop()

    return answer_text



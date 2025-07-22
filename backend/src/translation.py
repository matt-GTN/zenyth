# /backend/src/translation.py
import os
from typing import Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr
from config import create_llm_instance

def translate_text(text: str, target_language: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Traduit un texte donné dans une langue cible en utilisant un LLM.

    Args:
        text (str): Le texte à traduire.
        target_language (str): La langue de destination (ex: "english", "français").

    Returns:
        Tuple[Optional[str], Optional[str]]: Un tuple contenant le texte traduit et une erreur éventuelle.
    """
    try:
        if not text or not text.strip():
            return None, "The text to translate is empty."

        llm = create_llm_instance()

        prompt = ChatPromptTemplate.from_template(
            "You are a high-quality, professional translator. "
            "Your task is to translate the following text into **{target_language}**. "
            "Do not add any comments, notes, or introductions. "
            "Your output must be ONLY the direct translation of the text provided.\n\n"
            "Text to translate:\n---\n{text}\n---\n\n"
            "Direct translation in {target_language}:"
        )

        chain = prompt | llm | StrOutputParser()

        translated_text = chain.invoke({
            "text": text,
            "target_language": target_language
        })

        return translated_text, None

    except Exception as e:
        return None, f"Error during translation: {e}"
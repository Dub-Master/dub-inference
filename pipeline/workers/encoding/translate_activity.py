import os

import openai
from common.params import TranslateParams
from dotenv import load_dotenv
from temporalio import activity

load_dotenv()

openai.organization = os.getenv("OPENAI_ORG_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")

TRANSLATE_SYS_PROMPT = "You are a professional translator."
TRANSLATE_PROMPT = """You are a professional translator.
Translate the following text to {target_language} if it is not
already written in {target_language}. If it is already written
in {target_language}, return the Text as is without translating it.
Text: {text}
Translation: """


@activity.defn
async def translate(params: TranslateParams) -> str:
    print('translate_params', params)
    prompt = TRANSLATE_PROMPT.format(
        target_language=params.target_language,
        text=params.text)
    completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": TRANSLATE_SYS_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    resp = completion.choices[0].message.content
    print('resp', resp)
    return resp

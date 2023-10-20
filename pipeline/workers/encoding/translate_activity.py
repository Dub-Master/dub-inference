import os
import openai
from temporalio import activity
from params import TranslateParams

openai.organization = os.getenv("OPENAI_ORG_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")

TRANSLATE_SYS_PROMPT = "You are a professional translator."
TRANSLATE_PROMPT = """You are a professional translator.
Translate the following text to {target_language}.
Text: {text}
Translation: """


@activity.defn
async def translate(params: TranslateParams) -> str:
    prompt = TRANSLATE_PROMPT.format(target_language=params.target_language, text=params.text)
    completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": TRANSLATE_SYS_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    resp = completion.choices[0].message.content
    return resp

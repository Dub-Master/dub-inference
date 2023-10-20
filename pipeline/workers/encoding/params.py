from dataclasses import dataclass

@dataclass
class TranslateParams:
    text: str
    target_language: str

@dataclass
class TextToSpeechParams:
    text: str
    voice: str

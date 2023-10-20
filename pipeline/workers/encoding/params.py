from dataclasses import dataclass

@dataclass
class TranslateParams:
    text: str
    target_language: str

@dataclass
class TextToSpeechParams:
    text: str
    voice: str

@dataclass
class CloneVoiceParams:
    voice_name: str
    s3_audio_files: list[str]

@dataclass
class DeleteVoiceParams:
    voice_id: str

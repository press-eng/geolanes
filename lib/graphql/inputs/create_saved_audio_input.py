import strawberry


@strawberry.input
class CreateSavedAudioInput:
    audio: str

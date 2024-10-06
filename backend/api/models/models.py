from pydantic import BaseModel

class Prompt(BaseModel):
    prompt: str

class LLMInput(BaseModel):
    input: str

class FileModel(BaseModel):
    name: str
    location: str
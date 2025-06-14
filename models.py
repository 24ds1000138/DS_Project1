from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 string

class SingleAnswer(BaseModel):
    answer: str
    links: List[dict]

class AnswerResponse(BaseModel):
    results: List[SingleAnswer]

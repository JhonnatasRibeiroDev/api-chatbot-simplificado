from pydantic import BaseModel

class SessionResponse(BaseModel):
    session_id : str

class MessageResponse(BaseModel):
    role: str
    content: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    history: list[MessageResponse]


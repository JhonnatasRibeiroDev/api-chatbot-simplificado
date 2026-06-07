from pydantic import BaseModel


class SessionRequest(BaseModel):
    client_id: str | None = None


class SessionResponse(BaseModel):
    client_id: str
    session_id: str

class MessageResponse(BaseModel):
    role: str
    content: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    history: list[MessageResponse]


class ClientSessionResponse(BaseModel):
    session_id: str
    created_at: str


class ClientSessionsResponse(BaseModel):
    client_id: str
    sessions: list[ClientSessionResponse]


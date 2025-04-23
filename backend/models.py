from sqlmodel import SQLModel, Field
from typing import Optional


class CodeBlock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    template: str
    solution: str

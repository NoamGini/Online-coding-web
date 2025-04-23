from sqlmodel import SQLModel, create_engine, Session, select
import os
from models import CodeBlock

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./codeblocks.db")
engine = create_engine(DB_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)
    initial_db()


def initial_db():
    with Session(engine) as session:
        existing = session.exec(select(CodeBlock)).all()
        if existing:
            return
            # Define 4 blocks manually
    blocks = [
        CodeBlock(
            title="Async Case",
            template='async function fetchData() {\n  // your code here\n}',
            solution='async function fetchData() {\n  return await fetch("https://api.example.com");\n}'
        ),
        CodeBlock(
            title="Promise Example",
            template='const promise = new Promise((resolve, reject) => {\n  // your code here\n});',
            solution='const promise = new Promise((resolve, reject) => {\n  resolve("done");\n});'
        ),
        CodeBlock(
            title="Map Function",
            template='const arr = [1, 2, 3];\nconst result = arr.map(/* your function here */);',
            solution='const arr = [1, 2, 3];\nconst result = arr.map(x => x * 2);'
        ),
        CodeBlock(
            title="Set Timeout",
            template='setTimeout(() => {\n  // your code here\n}, 1000);',
            solution='setTimeout(() => {\n  console.log("Done");\n}, 1000);'
        ),
    ]

    for block in blocks:
        session.add(block)
    session.commit()

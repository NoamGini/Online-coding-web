from sqlmodel import SQLModel, create_engine, Session, select, delete
import os
from models import CodeBlock

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./codeblocks.db")
engine = create_engine(DB_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)
    initial_db()


# initialize the data base to static code blocks
def initial_db():
    with Session(engine) as session:
        existing = session.exec(select(CodeBlock)).all()
        if existing:
            return
    blocks = [
        CodeBlock(
            title="Async Case",
            template='// TODO: Fetch the todo with id 1 from "https://jsonplaceholder.typicode.com/todos/:id"\n'
                     '// and return its title\n'
                     'async function fetchData() {\n'
                     '\n'
                     '}',
            solution='// TODO: Fetch the todo with id 1 from "https://jsonplaceholder.typicode.com/todos/:id"\n'
                     '// and return its title\n'
                     'async function fetchData() {\n'
                     '  const response = await fetch("https://jsonplaceholder.typicode.com/todos/1");\n'
                     '  const data = await response.json();\n'
                     '  return data.title;\n'
                     '}'
        ),
        CodeBlock(
            title="Promise",
            template='// TODO: Randomly resolve with "You win!" or reject with "Try again!"\n'
                     'const luckyDraw = new Promise((resolve, reject) => {\n'
                     '\n'
                     '});',
            solution='// TODO: Randomly resolve with "You win!" or reject with "Try again!"\n'
                     'const luckyDraw = new Promise((resolve, reject) => {\n'
                     '  const isWinner = Math.random() > 0.5;\n'
                     '  if (isWinner) {\n'
                     '    resolve("You win!");\n'
                     '  } else {\n'
                     '    reject("Try again!");\n'
                     '  }\n'
                     '});'
        ),
        CodeBlock(
            title="Map Function",
            template='// TODO: Create a function that takes an array and returns a new array\n'
                     '// where all elements are multiplied by 2\n'
                     'function multiplyByTwo(arr) {\n'
                     '\n'
                     '}',
            solution='// TODO: Create a function that takes an array and returns a new array\n'
                     '// where all elements are multiplied by 2\n'
                     'function multiplyByTwo(arr) {\n'
                     '  return arr.map(element => element * 2);\n'
                     '}'
        ),
        CodeBlock(
            title="Set Timeout",
            template='// TODO: Create a function that gets another function as a parameter\n'
                     '// and executes it after 1 second.\n'
                     'function delayedExecutor(callback) {\n'
                     '\n'
                     '}',
            solution='// TODO: Create a function that gets another function as a parameter\n'
                     '// and executes it after 1 second.\n'
                     'function delayedExecutor(callback) {\n'
                     '  setTimeout(callback, 1000);\n'
                     '}'
        )

    ]

    for block in blocks:
        session.add(block)
    session.commit()


# Clear the database
def clear_codeblocks():
    with Session(engine) as session:
        session.execute(delete(CodeBlock))
        session.commit()

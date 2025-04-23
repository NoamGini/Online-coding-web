from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List
from collections import defaultdict
from sqlmodel import Session, select

from db import engine
from models import CodeBlock

router = APIRouter()


def normalize_code(code: str) -> str:
    return "\n".join(line.strip() for line in code.strip().splitlines() if line.strip())


class ConnectionManager:

    def __init__(self):
        self.active_students_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.mentor_connections: Dict[str, WebSocket] = {}
        self.code_states: Dict[str, str] = {}
        self.solutions: Dict[str, str] = {}

    def load_solutions_from_db(self):
        with Session(engine) as session:
            blocks = session.exec(select(CodeBlock)).all()
            for block in blocks:
                self.solutions[str(block.id)] = block.solution
                self.code_states[str(block.id)] = block.template
                print(f"Loaded: {block.title} (ID: {block.id})")

    def connect(self, code_block_id: str, web_socket: WebSocket):

        if code_block_id not in self.mentor_connections:
            self.mentor_connections[code_block_id] = web_socket
        else:
            self.active_students_connections[code_block_id].append(web_socket)

    def get_students_count(self, code_block_id: str):
        return max(0, len(self.active_students_connections.get(code_block_id, [])))

    async def broadcast_code(self, code_block_id: str, code: str):
        self.code_states[code_block_id] = code
        for conn in self.active_students_connections.get(code_block_id, []):
            await conn.send_json({"type": "code_update", "code": code, })
        mentor_conn = self.mentor_connections.get(code_block_id)
        if mentor_conn:
            await mentor_conn.send_json({"type": "code_update", "code": code, })

        # Check solution match
        if normalize_code(self.solutions.get(code_block_id)) == normalize_code(code):
            for conn in self.active_students_connections.get(code_block_id):
                await conn.send_json({"type": "solution_match"})
            mentor_conn = self.mentor_connections.get(code_block_id)
            if mentor_conn:
                await mentor_conn.send_json({"type": "solution_match"})

    async def broadcast_student_count(self, code_block_id: str):
        count = self.get_students_count(code_block_id)
        for conn in self.active_students_connections.get(code_block_id, []):
            await conn.send_json({"type": "students_count", "students_count": count})
        mentor_conn = self.mentor_connections.get(code_block_id)
        if mentor_conn:
            await mentor_conn.send_json({"type": "students_count", "students_count": count})

    def is_mentor(self, code_block_id: str, web_socket: WebSocket) -> bool:
        return self.mentor_connections.get(code_block_id) == web_socket

    def get_students(self, code_block_id: str) -> List[WebSocket]:
        return self.active_students_connections[code_block_id]

    def disconnect(self, code_block_id: str, web_socket: WebSocket):
        if self.is_mentor(code_block_id, web_socket):
            del self.mentor_connections[code_block_id]
            return "mentor_left"
        else:
            if code_block_id in self.active_students_connections:
                self.active_students_connections[code_block_id].remove(web_socket)
            return "student_left"

    def is_solution_correct(self, code_block_id: str, current_code: str) -> bool:
        solution = self.solutions.get(code_block_id)
        if not solution:
            return False
        if normalize_code(current_code) == normalize_code(solution):
            return True


@router.websocket("/ws/{block_id}")
async def web_socket_endpoint(block_id: str, web_socket: WebSocket):
    await web_socket.accept()
    manager.connect(block_id, web_socket)

    role = "mentor" if manager.is_mentor(block_id, web_socket) else "student"
    await web_socket.send_json({
        "type": "init",
        "role": role,
        "code": manager.code_states[block_id],
        "students_count": manager.get_students_count(block_id)
    })

    await manager.broadcast_student_count(block_id)

    try:
        while True:
            data = await web_socket.receive_json()
            if data["type"] == "code_update" and role == "student":
                await manager.broadcast_code(block_id, data["code"])

    except WebSocketDisconnect:
        result = manager.disconnect(block_id, web_socket)
        if result == "mentor_left":
            for student in manager.get_students(block_id)[:]:
                await student.send_json({"type": "redirect", "code": manager.solutions[block_id]})
                await student.close()
            manager.active_students_connections[block_id] = []
            manager.code_states[block_id] = manager.solutions[block_id]

            with Session(engine) as session:
                block = session.exec(select(CodeBlock).where(CodeBlock.id == int(block_id))).first()
            if block:
                manager.code_states[block_id] = block.template
        else:
            await manager.broadcast_student_count(block_id)


@router.get("/codeblocks")
def get_codeblocks():
    with Session(engine) as session:
        blocks = session.exec(select(CodeBlock)).all()
        return blocks


manager = ConnectionManager()

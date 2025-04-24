from difflib import SequenceMatcher

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List
from collections import defaultdict
from sqlmodel import Session, select

from db import engine
from models import CodeBlock

router = APIRouter()


# static helper fucntions
def normalize_code(code: str) -> str:
    return ''.join(code.split())


# get the code from the actual starting point the user should be typing from
def extract_editable_region_from_brace(code: str) -> str:
    brace_index = code.find('{')
    if brace_index != -1:
        return code[brace_index + 1:].rstrip('}')  # optionally strip trailing }
    return code


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

    # handle new connection
    def connect(self, code_block_id: str, web_socket: WebSocket):

        if code_block_id not in self.mentor_connections:
            self.mentor_connections[code_block_id] = web_socket
        else:
            self.active_students_connections[code_block_id].append(web_socket)

    # get students number in each code block page
    def get_students_count(self, code_block_id: str):
        return max(0, len(self.active_students_connections.get(code_block_id, [])))

    # update all the other users on the code's changes
    async def broadcast_code(self, code_block_id: str, code: str,sender_conn=None):
        self.code_states[code_block_id] = code

        # update the progress according to the students code changes
        progress = self.calculate_progress(code_block_id, code)

        # update the students but not the one who wrote the code
        for conn in self.active_students_connections.get(code_block_id, []):
            if conn != sender_conn:
                await conn.send_json({"type": "code_update", "code": code, "progress": progress})

        # update the mentor
        mentor_conn = self.mentor_connections.get(code_block_id)
        if mentor_conn:
            await mentor_conn.send_json({"type": "code_update", "code": code, "progress": progress})

        # Check the code matches the solution and update both students and mentor in the room
        if progress == 100:
            for conn in self.active_students_connections.get(code_block_id):
                await conn.send_json({"type": "solution_match"})
            mentor_conn = self.mentor_connections.get(code_block_id)
            if mentor_conn:
                await mentor_conn.send_json({"type": "solution_match"})

    # upadte all of the student count - when student leave or connect
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
        # if mentor left - remove the block id from the mentors connections
        if self.is_mentor(code_block_id, web_socket):
            del self.mentor_connections[code_block_id]
            return "mentor_left"
        else:
            # if student left - remove from the block id list
            if code_block_id in self.active_students_connections:
                self.active_students_connections[code_block_id].remove(web_socket)
            return "student_left"

    def is_solution_correct(self, code_block_id: str, current_code: str) -> bool:
        solution = self.solutions.get(code_block_id)
        if not solution:
            return False
        if normalize_code(current_code) == normalize_code(solution):
            return True

    def calculate_progress(self, code_block_id: str, student_code: str) -> int:
        # calculating the progress of the students code by squence matcher
        solution = self.solutions.get(code_block_id)
        expected = extract_editable_region_from_brace(solution)
        actual = extract_editable_region_from_brace(student_code)

        ratio = SequenceMatcher(None, normalize_code(actual), normalize_code(expected)).ratio()
        return int(ratio * 100)


@router.websocket("/ws/{block_id}")
async def web_socket_endpoint(block_id: str, web_socket: WebSocket):
    await web_socket.accept()
    # add the web socket to the mentor connection dict
    manager.connect(block_id, web_socket)

    # check whether the role is mentor or student
    role = "mentor" if manager.is_mentor(block_id, web_socket) else "student"
    # send the initial connection message through websocket
    await web_socket.send_json({
        "type": "init",
        "role": role,
        "code": manager.code_states[block_id],
        "students_count": manager.get_students_count(block_id)
    })
    # update all - student count changed
    await manager.broadcast_student_count(block_id)

    try:
        # connections is open
        while True:
            # get messages
            data = await web_socket.receive_json()
            # if the type is code update then get the new code and boradcast it to all
            if data["type"] == "code_update" and role == "student":
                await manager.broadcast_code(block_id, data["code"],sender_conn=web_socket)

    # handle diconnection
    except WebSocketDisconnect:
        result = manager.disconnect(block_id, web_socket)

        # if the mentor left - close students connections on this block id
        if result == "mentor_left":
            for student in manager.get_students(block_id)[:]:
                await student.send_json({"type": "redirect", "code": manager.solutions[block_id]})
                await student.close()
            manager.active_students_connections[block_id] = []

            # update the code to be the initial template
            with Session(engine) as session:
                block = session.exec(select(CodeBlock).where(CodeBlock.id == int(block_id))).first()
            if block:
                manager.code_states[block_id] = block.template
        else:
            await manager.broadcast_student_count(block_id)


# get all code blocks
@router.get("/codeblocks")
def get_codeblocks():
    with Session(engine) as session:
        blocks = session.exec(select(CodeBlock)).all()
        return blocks


manager = ConnectionManager()

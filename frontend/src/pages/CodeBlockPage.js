import React, { useEffect, useState, useRef } from 'react'
import CodeBlock from '../components/CodeBlock';
import { useLocation, useNavigate, useParams } from "react-router-dom";
import './CodeBlockPage.css'

export default function BlockCodePage() {

  const location = useLocation();
  const { id } = useParams();
  const title = location.state?.title || "";
  const [role, setRole] = useState('');
  const [code, setCode] = useState('');
  const [showSmiley, setShowSmiley] = useState(false);
  const [studentsOnline, setStudentsOnline] = useState(0);
  const socketRef = useRef(null);


  const navigate = useNavigate();

  const handleBack = () => {
    navigate(-1); // This goes back one page in history
  };

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/${id}`);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log('websocket open')


    }
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'init') {
        const data = JSON.parse(event.data)

        setRole(data.role)
        setCode(data.code)
        setStudentsOnline(data.students_count)
      }

      if (data.type === "code_update") {
        console.log("Received code:", data.code)
        if (data.code !== code) {
          setCode(data.code);
        }
      }
      if (data.type === "solution_match") {
        setShowSmiley(true);
        setTimeout(() => setShowSmiley(false), 3000);
      }
      if (data.type === "students_count") {
        setStudentsOnline(data.students_count);
      }
      if (data.type === "redirect") {
        setCode(data.code);
        navigate("/");
      }
    };
    return () => {
      socket.close();
    };
  }, [id, navigate]);

  const handleCodeChange = (updatedCode) => {
    if (role === 'student' && socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: "code_update",
        code: updatedCode,
      }));
    }
  };

  return (
    <div className="page-container">
      <button className="back-btn" onClick={handleBack}>Go Back to Lobby</button>
      <div className="header">
        <h1>{title}</h1>
      </div>
      <div className="editor-container">
        <div className='code-editor-wrapper'>
          <CodeBlock code={code} onChangeCode={handleCodeChange} role={role}></CodeBlock>
        </div>
        <div className="online-indicator">
          <span className="online-dot"></span>
          <span className="students-online">{studentsOnline} online</span>
        </div>
      </div>
      {showSmiley && (
        <div className="smiley-overlay">
          You did great!😊
        </div>
      )}
    </div>
  )
}

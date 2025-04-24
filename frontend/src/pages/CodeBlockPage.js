import React, { useEffect, useState, useRef, useCallback } from 'react'
import CodeBlock from '../components/CodeBlock';
import { useLocation, useNavigate, useParams } from "react-router-dom";
import './CodeBlockPage.css'
import ToggleButton from '../components/ToggleButton';

export default function BlockCodePage() {

  //get the title from state when nvigating to this page
  const location = useLocation();
  const title = location.state?.title || "";

  //get id param form the path
  const { id } = useParams();
  const [role, setRole] = useState('');
  const [code, setCode] = useState('');
  const [showSmiley, setShowSmiley] = useState(false);
  const [studentsOnline, setStudentsOnline] = useState(0);

  //create socket ref - opening the socket once and use it
  const socketRef = useRef(null);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // the student proggress feature from 0 to 100
  const [progress, setProgress] = useState(0);
  const codeRef = useRef(code);
  const navigate = useNavigate();
  
  // This goes back one page - for the go back button
  const handleBack = () => {
    navigate(-1);
  };

  // // Establish and manage WebSocket connection
  // useEffect(() => {
  //   const socket = new WebSocket(`${process.env.REACT_APP_WS_URL}/ws/${id}`);
  //   socketRef.current = socket;

  //   // WebSocket opened
  //   socket.onopen = () => {
  //     console.log('WebSocket connection established');
  //   };

  //   socket.onmessage = (event) => {
  //     const data = JSON.parse(event.data);

  //     switch (data.type) {
  //       case 'init':
  //         // set initial role, code, and online students count
  //         setRole(data.role);
  //         setCode(data.code);
  //         setStudentsOnline(data.students_count);
  //         break;

  //       case 'code_update':
  //         // update code and progress only if changed
  //         if (data.code !== code) {
  //           setCode(data.code);
  //           setProgress(data.progress);
  //         }
  //         break;

  //       case 'solution_match':
  //         // show smiley animation for 3 seconds
  //         setShowSmiley(true);
  //         setTimeout(() => setShowSmiley(false), 3000);
  //         break;

  //       case 'students_count':
  //         // Update number of students online
  //         setStudentsOnline(data.students_count);
  //         break;

  //       case 'redirect':
  //         // Redirect user and update code before navigating
  //         setCode(data.code);
  //         navigate("/");
  //         break;

  //       default:
  //         console.warn("Unhandled WebSocket message type:", data.type);
  //     }
  //   };

  //   return () => {
  //     // clean up WebSocket
  //     socket.close();
  //   };
  // }, [id, navigate]);

  useEffect(() => {
    // Initialize WebSocket connection
    const socket = new WebSocket(`${process.env.REACT_APP_WS_URL}/ws/${id}`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'init':
          // set initial role, code, and online students count
          setRole(data.role);
          setCode(data.code);
          setStudentsOnline(data.students_count);
          codeRef.current = data.code; // Update the ref with the new code
          break;

        case 'code_update':
          // Only update if the code has actually changed
          if (data.code !== codeRef.current) {
            setCode(data.code);
            codeRef.current = data.code; // Update the ref with the new code
            setProgress(data.progress)
          }
          break;

        case 'solution_match':
          // Show smiley animation for 3 seconds
          setShowSmiley(true);
          setTimeout(() => setShowSmiley(false), 3000);
          break;

        case 'students_count':
          // Update number of students online
          setStudentsOnline(data.students_count);
          break;

        case 'redirect':
          // Redirect user and update code before navigating
          setCode(data.code);
          navigate("/");
          break;

        default:
          console.warn("Unhandled WebSocket message type:", data.type);
      }
    };

    // Clean up WebSocket connection on component unmount
    return () => {
      socket.close();
    };
  }, [id, navigate]);

  // Send updated code to server if the user is a student and WebSocket is open
  const handleCodeChange = useCallback((updatedCode) => {
    if (role === 'student' && socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: "code_update",
        code: updatedCode,
      }));
    }
  },[role]);

  return (
    <div className="page-container">

      {/* Top bar with back button and theme toggle */}
      <div className="top-bar">
        <button className="back-btn" onClick={handleBack}> ←  Go Back</button>
        <ToggleButton onToggle={() => setIsDarkMode(prev => !prev)} isOn={isDarkMode} />
      </div>

      {/* Page title */}
      <div className="header">
        <h1>{title}</h1>
      </div>

      {/* Code editor */}
      <div className="editor-container">
        <div className={`code-editor-wrapper ${isDarkMode ? 'dark' : 'light'}`}>
          <CodeBlock code={code} onChangeCode={handleCodeChange} role={role} isDarkMode={isDarkMode}></CodeBlock>
        </div>

        {/* Side bar panel */}
        <div className="sidebar-panel">
          <h2 className="sidebar-title">Session info</h2>
          <div className="online-indicator">
            <span className="online-dot"></span>
            <span className="students-online">{studentsOnline} online</span>
          </div>

          {/* Progress bar */}
          <div className="progress-container">
            <div className="progress-text">{progress}%</div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Smiley face on success */}
      {showSmiley && (
        <div className="smiley-overlay">
          You did great!😊
        </div>
      )}
    </div>
  )
}

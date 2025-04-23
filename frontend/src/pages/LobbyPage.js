import React, { useEffect } from 'react'
import { useState } from 'react'
import { useNavigate } from "react-router-dom";


export default function LobbyPage() {

  const navigate = useNavigate();

  // TODO: Replace with backend fetch
  const [codeBlockList, setCodeBlockList] = useState([])

  useEffect(() => {
    fetch('http://localhost:8000/codeblocks')
      .then(response => response.json())
      .then(data => setCodeBlockList(data))
      .catch(error => console.log(error));

  }, [])

  const handleNavigation = ((codeBlock) => {
    navigate(`/codeBlock/${codeBlock.id}`, { state: { title: codeBlock.title } })
  });

  const listItems = codeBlockList.map((codeBlock) => (
    <li key={codeBlock.id}>
      <button onClick={() => handleNavigation(codeBlock)}>{codeBlock.title}</button>
    </li>))

  return (
    <div>
      <h1>Choose code block</h1>
      <ul>
        {listItems}
      </ul>
    </div>
  )
}

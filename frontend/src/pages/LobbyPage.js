import React, { useEffect } from 'react'
import { useState } from 'react'
import { useNavigate } from "react-router-dom";


export default function LobbyPage() {

  const navigate = useNavigate();
  const [codeBlockList, setCodeBlockList] = useState([])

   // first check sessionStorage for cached codeBlocks data
  useEffect(() => {
    const cached = sessionStorage.getItem('codeBlocks');

    if (cached) {
      // if data exists in sessionStorage, use it
      setCodeBlockList(JSON.parse(cached));
    } else {
      //if no cached data, fetch from backend and save in sessionStorage
      fetch('http://localhost:8000/codeblocks')
        .then(response => response.json())
        .then(data => {
          setCodeBlockList(data);
          sessionStorage.setItem('codeBlocks', JSON.stringify(data));
        })
        .catch(error => console.log(error));
    }
  }, []);

  //navigate to the codeBlock pgae with the coresponded id 
  const handleNavigation = ((codeBlock) => {
    navigate(`/codeBlock/${codeBlock.id}`, { state: { title: codeBlock.title } })
  });

  //generate a list of code block buttons that navigate to the selected code block when clicked
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

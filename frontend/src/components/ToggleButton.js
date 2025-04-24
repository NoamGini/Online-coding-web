import React from 'react'
import './ToggleButton.css'

export default function ToggleButton({onToggle, isOn }) {

  return (
    <div className="toggle-container" onClick={onToggle}>
      <div className={`toggle-btn ${isOn ? 'on' : 'off'}`}>
        {isOn ?'☀️ Light' : '🌙 Dark'}
      </div>
    </div>
  )
}

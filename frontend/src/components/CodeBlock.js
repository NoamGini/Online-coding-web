import React, { useState, useCallback, useEffect } from 'react'
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { okaidia } from '@uiw/codemirror-theme-okaidia';
import './CodeBlock.css'

export default function CodeBlock({ code, onChangeCode, role }) {

    const onChange = useCallback((val, viewUpdate) => {
        console.log(val)
        if (role === 'student') {
            onChangeCode(val)
        }
    }, [onChangeCode, role]);


    return (
        <div className="code-block-container">
            <div className="editor-header">
                <div className='role-indicator'>
                    <span className="role-dot"></span>
                    <span>{role} </span>
                </div>
            </div>
            <CodeMirror value={code} theme={okaidia} extensions={[javascript()]} onChange={onChange} editable={role === 'student'} />
        </div>
    )
}

import React, {useCallback } from 'react'
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { okaidia } from '@uiw/codemirror-theme-okaidia';
import { githubLight } from '@uiw/codemirror-theme-github'
import './CodeBlock.css'

export default function CodeBlock({ code, onChangeCode, role, isDarkMode}) {

    // when the code changes call onChanageCode function from props 
    const onChange = useCallback((val) => {
        onChangeCode(val)
        
    }, [onChangeCode,]);


    return (
        <div>
        
        <div className="code-block-container">
            <div className="editor-header">
                <div className='role-indicator'>
                    <span className="role-dot"></span>
                    <span>{role} </span>
                </div>
            </div>
            <CodeMirror value={code} theme={isDarkMode ? okaidia : githubLight} extensions={[javascript()]} onChange={onChange} editable={role === 'student'} />
        </div>
        </div>
    )
}

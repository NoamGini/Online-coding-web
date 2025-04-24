import { BrowserRouter, Routes, Route } from "react-router-dom";
import LobbyPage from "./pages/LobbyPage";
import CodeBlockPage from "./pages/CodeBlockPage";
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LobbyPage />}></Route>
        <Route path="/codeBlock/:id" element={<CodeBlockPage />}></Route>
      </Routes>
    </BrowserRouter>

  );
}


export default App;

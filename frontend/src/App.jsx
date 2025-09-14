import { useState } from 'react'
import Navbar from './components/Navbar'
import HomeScreen from './components/HomeScreen'
import ChatPanel from './components/ChatPanel'
import './App.css'

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false)

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen)
  }

  return (
    <div className="app">
      <Navbar onToggleChat={toggleChat} isChatOpen={isChatOpen} />
      <div className="main-content">
        <HomeScreen />
        <ChatPanel isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
      </div>
    </div>
  )
}

export default App

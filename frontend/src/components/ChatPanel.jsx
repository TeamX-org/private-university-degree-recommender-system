import { useState, useRef, useEffect } from 'react'
import './ChatPanel.css'

const ChatPanel = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    const question = inputValue.trim()
    if (!question || isLoading) return

    // Add user message
    const userMessage = { type: 'user', content: question }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          question,
          thread_id: 'main_session'
        })
      })

      const data = await response.json()
      
      // Add bot response
      const botMessage = { 
        type: 'bot', 
        content: data.answer || 'Sorry, I could not process your request.' 
      }
      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = { 
        type: 'bot', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>')
  }

  return (
    <div className={`chat-panel ${isOpen ? 'open' : ''}`}>
      <div className="chat-header">
        <div className="chat-title">
          <span className="chat-icon">🎓</span>
          <span>EduCompass Assistant</span>
        </div>
        <button className="close-btn" onClick={onClose}>
          ✕
        </button>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>👋 Hello! I'm your EduCompass assistant.</p>
            <p>Ask me anything about private universities and courses in Sri Lanka!</p>
            <div className="suggested-questions">
              <p><strong>Try asking:</strong></p>
              <ul>
                <li>What are the best computer science programs?</li>
                <li>Tell me about APIIT university</li>
                <li>What are the admission requirements?</li>
                <li>Show me scholarship opportunities</li>
              </ul>
            </div>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <div 
              className="message-content"
              dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
            />
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about universities, courses, admissions..."
          disabled={isLoading}
        />
        <button 
          onClick={sendMessage} 
          disabled={!inputValue.trim() || isLoading}
          className="send-btn"
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatPanel

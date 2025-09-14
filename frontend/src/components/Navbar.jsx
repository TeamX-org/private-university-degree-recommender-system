import './Navbar.css'

const Navbar = ({ onToggleChat, isChatOpen }) => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <span className="brand-icon">🎓</span>
          <span className="brand-text">EduCompass</span>
        </div>
        
        <div className="navbar-actions">
          <button 
            className={`chat-toggle-btn ${isChatOpen ? 'active' : ''}`}
            onClick={onToggleChat}
            title={isChatOpen ? 'Close Assistant' : 'Open Assistant'}
          >
            <span className="chat-icon">💬</span>
            <span className="chat-text">
              {isChatOpen ? 'Close' : 'Ask Assistant'}
            </span>
          </button>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

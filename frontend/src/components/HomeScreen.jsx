import './HomeScreen.css'

const HomeScreen = () => {
  return (
    <div className="home-screen">
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Welcome to <span className="highlight">EduCompass</span>
          </h1>
          <p className="hero-subtitle">
            Your intelligent guide to private universities and courses in Sri Lanka
          </p>
          <p className="hero-description">
            Discover the perfect educational path with personalized recommendations, 
            detailed course information, and expert guidance tailored to your aspirations.
          </p>
          
          <div className="hero-features">
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Personalized Recommendations</h3>
              <p>Get course suggestions based on your interests and career goals</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h3>Comprehensive Information</h3>
              <p>Access detailed information about universities, courses, and admissions</p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">💰</div>
              <h3>Financial Guidance</h3>
              <p>Learn about fees, scholarships, and financial aid opportunities</p>
            </div>
          </div>
          
          <div className="cta-section">
            <p className="cta-text">Ready to explore your educational journey?</p>
            <p className="cta-hint">Click "Ask Assistant" in the top right to get started!</p>
          </div>
        </div>
      </div>
      
      <div className="info-section">
        <div className="info-content">
          <h2>Why Choose EduCompass?</h2>
          <div className="info-grid">
            <div className="info-item">
              <h4>🤖 AI-Powered</h4>
              <p>Advanced AI technology provides accurate and up-to-date information</p>
            </div>
            <div className="info-item">
              <h4>🇱🇰 Sri Lanka Focused</h4>
              <p>Specialized knowledge of private universities and courses in Sri Lanka</p>
            </div>
            <div className="info-item">
              <h4>🔄 Real-time Updates</h4>
              <p>Always current information from university websites and official sources</p>
            </div>
            <div className="info-item">
              <h4>💬 Interactive Chat</h4>
              <p>Natural conversation interface for easy information discovery</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomeScreen

// App.js
import React, {useState} from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import './App.css';
import AuthForm from './LoginForm';  

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };
  const closeMenu = () => {
    setIsMenuOpen(false)
  }

  return (
    <Router>
      <div className="app-container">
        {/* Background blobs */}
        <div className="scene" aria-hidden="true">
          <div className="scene__blob scene__blob--1"></div>
          <div className="scene__blob scene__blob--2"></div>
          <div className="scene__blob scene__blob--3"></div>
        </div>

        {/* HEADER AREA*/}
        <header className='navbar glass'>
          <nav className="desktop-nav">
            <NavLink to="/" className="glass-nav__item" end>Solution</NavLink>
            <NavLink to="/about" className="glass-nav__item" end>About</NavLink>
          </nav>

           <div className='navbar-logo'>
            <span className='logo-icon'>🐾</span> <strong>PulseCheck</strong>
          </div>

          <nav className='desktop-nav'>
            <NavLink to="/signup" className="glass-nav__item" end>Sign up</NavLink>
            <NavLink to="/login" className="glass-nav__item" end>Login</NavLink>
          </nav>

           {/* hamburger button (only mobile) */}
          <button className='hamburger-btn' onClick={toggleMenu}>
            {isMenuOpen ? 'X' : '☰'}
          </button>

          {/* Mobile Drawer */}
          <nav className={`navbar-menu ${isMenuOpen ? 'open' : ''}`}>
           <NavLink to="/" onClick={closeMenu}>Solution</NavLink>
           <NavLink to="/about" onClick={closeMenu}>About</NavLink>
           <NavLink to="/signup" onClick={closeMenu}>Signup</NavLink>
           <NavLink to="/login" onClick={closeMenu}>Login</NavLink>
          </nav>   
        </header>

        {/* MIDDLE (HERO) SECTION*/}
        <main className='main-content'>
          <Routes>
            <Route path="/" element={<section className='hero-section'>
              <h1 className='hero-title'>Monitoring as a Service</h1>
                <span className='hero-sub'>
                  Work that moves at the speed of trust. Shared language, 
                  aligned direction, and a process that makes collaboration 
                  feel genuinely effortless.
                </span>
              </section>
            } />
            <Route path="/about" element={<section className='hero-section'>
              <h1 className='hero-title'>About Us</h1>
                <span className='hero-sub'>
                  We are building the future of real-time server and application monitoring.
                </span>
              </section>
            } />
            <Route path="/signup" element={<AuthForm type="signup" />} />
            <Route path="/login" element={<AuthForm type="login" />} />
          </Routes>
         </main>

        {/* FOOTER AREA */}
        <footer className='footer'>
          <p>&copy; 2026 PulseCheck Inc. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
// App.js
import React, {useState, useEffect} from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import './App.css';
import AuthForm from './LoginForm';  
import ProtectedRoute from './ProtectedRoute';

// TODO: create dashboard component
const Dashboard = () => <h2> 🐾 PulseCheck Dashboard - Successfully logged in. 🐾 </h2>

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const checkAuth = async () => {
      try{
        const response = await fetch('http://localhost:8000/me',{
          method: 'GET',
          credentials: 'include' //HTTP-COOKIE
        });
        if (response.ok){
          setIsAuthenticated(true);
        }else{
          setIsAuthenticated(false);
        }
      }catch(error){
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth()
  },[]);

  useEffect(()=> {
    setIsMenuOpen(false);
  }, [isAuthenticated]);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };
  const closeMenu = () => {
    setIsMenuOpen(false)
  }
  const handleLogout = async() => {
    try{
      const response = await fetch('http://localhost:8000/logout',{
        method: 'POST',
        credentials: 'include'
      });
      if (response.ok){
        setIsAuthenticated(false);
      }else {
        console.error("Server Error - Can't delete token.")
      }

    } catch(error){
      console.error("Logout error", error);
    }
  }

  if (isLoading){
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#0f172a', color: '#fff' }}>
        Loading PulseCheck...
      </div>
    );
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
            {isAuthenticated && <NavLink to="/dashboard" className="glass-nav__item">Dashboard</NavLink>}
          </nav>

           <div className='navbar-logo'>
            <span className='logo-icon'>🐾</span> <strong>PulseCheck</strong>
          </div>

          <nav className='desktop-nav'>
            {!isAuthenticated ? (
              <>
                <NavLink to="/signup" className="glass-nav__item" end>Sign up</NavLink>
                <NavLink to="/login" className="glass-nav__item" end>Login</NavLink>
              </>
            ) : (
              <button 
                onClick={handleLogout} 
                className="glass-nav__item" 
                style={{ background: 'none', border: 'none', cursor: 'pointer' }}
              >
                Logout
              </button>
            )}  
          </nav>

           {/* hamburger button (only mobile) */}
          <button className='hamburger-btn' onClick={toggleMenu}>
            {isMenuOpen ? 'X' : '☰'}
          </button>

          {/* Overlay pentru inchiderea meniului la click in afara */}
          {isMenuOpen && <div className="navbar-overlay" onClick={closeMenu} />}

          {/* Mobile Drawer */}
          <nav className={`navbar-menu ${isMenuOpen ? 'open' : ''}`}>
            <NavLink to="/" onClick={closeMenu}>Solution</NavLink>
            <NavLink to="/about" onClick={closeMenu}>About</NavLink>
            {!isAuthenticated ? (
              <>
                <NavLink to="/signup" onClick={closeMenu}>Signup</NavLink>
                <NavLink to="/login" onClick={closeMenu}>Login</NavLink>
              </>
            ) : (
              <NavLink to="/dashboard" onClick={closeMenu}>Dashboard</NavLink>
            )}
          </nav>
        </header>

        {/* MIDDLE (HERO) SECTION*/}
        <main className='main-content'>
          <Routes>
            <Route path="/" element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> :
              <section className='hero-section'>
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
            <Route path="/signup" element={isAuthenticated ? <Navigate to="/dashboard" replace/> : <AuthForm type="signup" />} />
            <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <AuthForm setIsAuthenticated={setIsAuthenticated} />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated} isLoading={isLoading}>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
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
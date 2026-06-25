//LoginForm.jsx
import React, { useState } from 'react';
import { Link,useNavigate, useSearchParams } from 'react-router-dom';
import './LoginForm.css';

import googleIcon from './assets/google-logo.svg'
import githubIcon from './assets/github-logo.svg'

export default function LoginForm({ setIsAuthenticated }) {
  const [loginData,setLoginData] = useState({email: '',pswd: ''});
  const [message, setMessage] = useState('');
  const [searchParams] = useSearchParams();

  const navigate = useNavigate();
  const handleChange = (e) => {
    setLoginData({...loginData, [e.target.name]: e.target.value});
  }
  
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://localhost:8000/login", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ email: loginData.email, password: loginData.pswd}),
        credentials: 'include'
      });
      const data = await response.json()
      if (response.ok) {
        setIsAuthenticated(true);
        setMessage("Logged in successfully!");
        const nextRoute = searchParams.get('next') || "/dashboard";
        navigate(nextRoute)
      } else {
        setMessage(data.message || data.detail)
      }
      
    } catch(error) {
      console.error("Login failed",error);
      setMessage("Server error, please try again.");
    }
  };
  

  // 3. TEST PROTECTED ROUTE
  const handleFetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/me', {
        method: 'GET',
        // CRITICAL: This tells the browser to attach the HttpOnly cookie to the request
        credentials: 'include' 
      });
      const data = await response.json();
      
      setMessage(JSON.stringify(data));
    } catch (error) {
      console.error("Fetch profile failed", error);
    }
  };

 return (
    <div className="auth-page-container">
      {/* Left Section - Branding */}
      <div className='auth-left-branding'>
        <div className='branding-content'>
          <span className='branding-icon'>🐾</span>
          <h1 className='hero-title'>PulseCheck</h1>
          <p className='hero-sub'>
            Incredibly crisp, liquid-smooth real-time application monitoring.          
          </p>
        </div>
      </div>

      {/* Right Section - Form */}
      <div className='auth-right-form'>
        <form className='glass-form glass' onSubmit={handleLogin}>
          <h2 className='glass-card__title'>Welcome back</h2>
          <p className='glass-card__body'>Enter your details to access your dashboard.</p>

          {/* Afișare mesaje */}
          {message && <div className="auth-message">{message}</div>}

          {/* Butoane OAuth2 */}
          <div className='social-auth-buttons'>
            <button type="button" className='glass-btn glass-btn--ghost social-btn'>
              <img src={googleIcon} alt="Google" className="social-icon-img" /> Sign in with Google
            </button>
            <button type="button" className="glass-btn glass-btn--ghost social-btn">
             <img src={githubIcon} alt="GitHub" className="social-icon-img" /> Sign in with GitHub
            </button>
          </div>

          <div className='auth-divider'>
            <span>or continue with email</span>
          </div>

          <div className="form-field">
            <label>Email Address</label>
            <div className="glass-input-wrap">
              <input 
                type="email" 
                name="email" 
                className="glass-input" 
                placeholder="name@domain.com" 
                onChange={handleChange}
                required 
              />
            </div>
          </div>

          <div className="form-field">
            <label>Password</label>
            <div className="glass-input-wrap">
              <input 
                type="password" 
                name="pswd" 
                className="glass-input" 
                placeholder="••••••••" 
                onChange={handleChange}
                required 
              />
            </div>
          </div>

          <button type="submit" className="glass-btn glass-btn--primary submit-auth-btn">
            Log In
          </button>

          <p className="auth-switch-text">
            Don't have an account? <Link to="/signup">Sign up</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
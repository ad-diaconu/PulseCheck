import React, { useState } from 'react';
import './AuthForm.css';

export default function AuthForm() {
  // State for forms
  const [signupData, setSignupData] = useState({ email: '', pswd: '', txt: '', broj: '' });
  const [loginData, setLoginData] = useState({ email: '', pswd: '' });
  const [message, setMessage] = useState('');

  // 1. SIGNUP FLOW
  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: signupData.email, password: signupData.pswd })
      });
      const data = await response.json();
      setMessage(data.message || data.detail);
    } catch (error) {
      console.error("Signup failed", error);
    }
  };

  // 2. LOGIN FLOW
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginData.email, password: loginData.pswd }),
        // CRITICAL: This tells the browser to accept the HttpOnly cookie from the backend
        credentials: 'include' 
      });
      const data = await response.json();
      setMessage(data.message || data.detail);
    } catch (error) {
      console.error("Login failed", error);
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
    <div className="main">  
      <input type="checkbox" id="chk" aria-hidden="true" />

      {/* Message Display for testing */}
      {message && <div style={{color: 'white', textAlign: 'center', padding: '10px'}}>{message}</div>}
      
      <button onClick={handleFetchProfile} style={{position: 'absolute', top: '-40px', left: '0'}}>
        Test Protected Route (/me)
      </button>

      <div className="signup">
        <form onSubmit={handleSignup}>
          <label htmlFor="chk" aria-hidden="true">Sign up</label>
          <input type="text" placeholder="User name" onChange={e => setSignupData({...signupData, txt: e.target.value})} required />
          <input type="email" placeholder="Email" onChange={e => setSignupData({...signupData, email: e.target.value})} required />
          <input type="password" placeholder="Password" onChange={e => setSignupData({...signupData, pswd: e.target.value})} required />
          <button type="submit" className="primary-btn">Sign up</button>
        </form>
      </div>

      <div className="login">
        <form onSubmit={handleLogin}>
          <label htmlFor="chk" aria-hidden="true">Login</label>
          <input type="email" placeholder="Email" onChange={e => setLoginData({...loginData, email: e.target.value})} required />
          <input type="password" placeholder="Password" onChange={e => setLoginData({...loginData, pswd: e.target.value})} required />
          <button type="submit" className="primary-btn">Login</button>
        </form>
      </div>
    </div>
  );
}
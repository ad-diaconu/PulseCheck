import React from 'react';
import './AuthForm.css'; // Make sure to import the CSS file

export default function AuthForm() {
  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Handle standard email/password login or signup logic here
    console.log("Form submitted!");
  };

  const handleOAuthLogin = (provider) => {
    // TODO: Redirect to your FastAPI backend OAuth endpoints
    // Example: window.location.href = `http://localhost:8000/auth/login/${provider}`;
    console.log(`Initiating ${provider} OAuth2 flow...`);
  };

  return (
    <div className="main">  
      <input type="checkbox" id="chk" aria-hidden="true" />

      <div className="signup">
        <form onSubmit={handleSubmit}>
          <label htmlFor="chk" aria-hidden="true">Sign up</label>
          <input type="text" name="txt" placeholder="User name" required />
          <input type="email" name="email" placeholder="Email" required />
          <input type="number" name="broj" placeholder="Phone Number" required />
          <input type="password" name="pswd" placeholder="Password" required />
          <button type="submit" className="primary-btn">Sign up</button>
        </form>
      </div>

      <div className="login">
        <form onSubmit={handleSubmit}>
          <label htmlFor="chk" aria-hidden="true">Login</label>
          <input type="email" name="email" placeholder="Email" required />
          <input type="password" name="pswd" placeholder="Password" required />
          <button type="submit" className="primary-btn">Login</button>
          
          <div className="oauth-divider">
            <span>or</span>
          </div>

          <div className="oauth-buttons">
            <button 
              type="button" 
              className="oauth-btn google-btn" 
              onClick={() => handleOAuthLogin('google')}
            >
              Log in with Google
            </button>
            <button 
              type="button" 
              className="oauth-btn github-btn" 
              onClick={() => handleOAuthLogin('github')}
            >
              Log in with GitHub
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
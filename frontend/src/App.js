// App.js
import React from 'react';
import AuthForm from './AuthForm'; // Import your new component
import './App.css'; // Optional: Keep this if you have global app styles

function App() {
  return (
    <div className="App">
      {/* Render the AuthForm component here */}
      <AuthForm />
    </div>
  );
}

export default App;
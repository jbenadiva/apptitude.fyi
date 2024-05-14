import React from 'react';
import './Header.css';


const Header = () => {
  return (
    <header className="app-header">
      <div className="logo-container">
        <img src="/logo.png" alt="Apptitudes Logo" /> 
      </div>
      <div className="contact-info">
        <p>
          Built by: <br />
          Joshua Benadiva (looking for a job!) <br />
          <a href="https://www.linkedin.com/in/jbenadiva/" className="linkedin-link">Linkedin</a>
        </p>
      </div>
    </header>
  );
};


export default Header;


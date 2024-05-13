import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [preference, setPreference] = useState('');
  const [workLifeBalance, setWorkLifeBalance] = useState('');
  const [salaryDesire, setSalaryDesire] = useState('');
  const [resume, setResume] = useState(null);
  const [result, setResult] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('preference', preference);
    formData.append('work_life_balance', workLifeBalance);
    formData.append('salary_desire', salaryDesire);
    formData.append('resume', resume);
  
    try {
      const response = await axios.post('http://localhost:5000/', formData);
      setResult(response.data.result);  // Ensure to handle nested 'result' if that's how data is structured in JSON response
    } catch (error) {
      console.error('Error posting form data:', error);
    }
  };
  

  return (
    <div className="App">
      <header className="App-header">
        <h1>Apptitude.ai Job Preferences</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Enter what you like to do"
            value={preference}
            onChange={e => setPreference(e.target.value)}
          />
          <input
            type="text"
            placeholder="Enter your work-life balance"
            value={workLifeBalance}
            onChange={e => setWorkLifeBalance(e.target.value)}
          />
          <input
            type="text"
            placeholder="Enter your desired salary"
            value={salaryDesire}
            onChange={e => setSalaryDesire(e.target.value)}
          />
          <input
            type="file"
            onChange={e => setResume(e.target.files[0])}
          />
          <button type="submit">Generate Job Recommendations</button>
        </form>
        {result && <div className="result">{result}</div>}
      </header>
    </div>
  );
}

export default App;


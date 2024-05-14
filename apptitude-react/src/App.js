import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import Header from './components/Header';


function App() {
  const [workPace, setWorkPace] = useState(50); // Default pace value
  const [salaryDesire, setSalaryDesire] = useState('');
  const [resume, setResume] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [uploadError, setUploadError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('work_pace', workPace); // Send work pace
    formData.append('salary_desire', salaryDesire);

    if (resume && (resume.type === 'application/pdf' || resume.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
      formData.append('resume', resume);
    } else {
      setUploadError('Please upload a valid resume format (PDF or DOCX).');
      return;
    }

    try {
      const response = await axios.post('http://localhost:5000/', formData);
      setRecommendations(response.data.result);
      setUploadError('');
    } catch (error) {
      console.error('Error posting form data:', error);
      setUploadError('Failed to upload data. Please try again.');
    }
  };

  return (
    <div className="App">
      <Header />
      <div className="main-content">
        <h1>What should I do with my life...</h1>
        <h2>Get personalized career advice, refine your resume, and unlock new opportunities...let's get started!</h2>
        <form onSubmit={handleSubmit}>
        <div className="slider-container" style={{width: '90%', margin: '20px 0'}}>
        <label htmlFor="work-pace-slider">How quickly or intensely do you like to work?</label>
          <div style={{width: '100%'}}>
            <div style={{display: 'flex', alignItems: 'left'}}>
              <span style={{color: "#667085", fontSize: '18px'}}>Relaxed pace</span>
              <input 
                type="range" 
                id="work-pace-slider" 
                min="1" 
                max="100" 
                value={workPace} 
                onChange={e => setWorkPace(e.target.value)}
                style={{
                  width: '100%', 
                  background: `linear-gradient(to right, #0F91D2 0%, #0F91D2 ${workPace}%, rgba(48, 127, 226, 0.3) ${workPace}%, rgba(48, 127, 226, 0.3) 100%)`
                }}
              />
              <span style={{color: "#667085", fontSize: '18px'}}>Fast paced</span>
            </div>
          </div>
        </div>
          <input type="text" placeholder="Enter your desired salary" value={salaryDesire} onChange={e => setSalaryDesire(e.target.value)} />
          <input type="file" onChange={e => setResume(e.target.files[0])} />
          <button type="submit">+ Generate Job Recommendations</button>
        </form>
        {uploadError && <div className="error-message">{uploadError}</div>}
        {recommendations && (
          <div className="result">
            <h2>Here are your job recommendations:</h2>
            {Object.entries(recommendations).map(([key, { title, description }]) => (
              <div key={key}>
                <h3>{key}. {title}</h3>
                <p style={{ fontSize: 'smaller' }}>{description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
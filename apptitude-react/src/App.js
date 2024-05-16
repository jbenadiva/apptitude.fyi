import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import Header from './components/Header';

function App() {
  const [workPace, setWorkPace] = useState(50); // Default pace value
  const [resume, setResume] = useState(null);
  const [workStyles, setWorkStyles] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [uploadError, setUploadError] = useState('');
  const [interactionStyles, setInteractionStyles] = useState([]);  // New state for interaction styles


  const handleWorkStyleChange = (style, event) => {
    event.preventDefault();  // Prevents the form from submitting when clicking on the checkbox
    event.stopPropagation(); // Stops the event from propagating further
    setWorkStyles(prev => {
        if (prev.includes(style)) {
            return prev.filter(s => s !== style);
        } else {
            return [...prev, style];
        }
    });
};

const handleInteractionChange = (style, event) => {
  event.preventDefault();
  event.stopPropagation();
  setInteractionStyles(prev => {
      if (prev.includes(style)) {
          return prev.filter(s => s !== style);
      } else {
          return [...prev, style];
      }
  });
};

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    if (file.size <= 10485760 && (file.type === "application/pdf" || file.type === "application/msword")) {
      setResume(file);
    } else {
      setUploadError('Please upload a DOC or PDF file no larger than 10MB.');
    }
  }
};

const handleFileDrop = (event) => {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file) {
    if (file.size <= 10485760 && (file.type === "application/pdf" || file.type === "application/msword")) {
      setResume(file);
    } else {
      setUploadError('Please upload a DOC or PDF file no larger than 10MB.');
    }
  }
};


  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('work_pace', workPace);
    formData.append('work_styles', JSON.stringify(workStyles)); // Send work styles as a JSON string
    formData.append('interaction_styles', JSON.stringify(interactionStyles)); // Send interaction styles as a JSON string

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
        <div className="work-style">
                        <label>What is your preferred style of work?</label>
                        {[
                            { id: 'methodical', option: '🔍 Careful & Methodical', description: 'I need to plan and think through every possibility and have incredible attention to detail' },
                            { id: 'innovation', option: '💡 Constant innovation', description: 'I enjoy frequent brainstorming and creativeness' },
                            { id: 'data-oriented', option: '📊 Evidence & data oriented', description: 'I like to make decisions based on hard evidence and data' },
                            { id: 'task-oriented', option: '✅ Task-oriented', description: 'I prefer to get a checklist and knock things off one-by-one!' }
                        ].map(option => (
                            <label key={option.id} className="form-check" onClick={(e) => handleWorkStyleChange(option.id, e)}>
                                <input
                                    type="checkbox"
                                    className="form-check-input"
                                    id={option.id}
                                    checked={workStyles.includes(option.id)}
                                    onChange={(e) => handleWorkStyleChange(option.id, e)} // Ensure to handle event here
                                    style={{ marginRight: '10px', cursor: 'pointer' }} // Ensure cursor pointer is on the checkbox too
                                />
                                <div>
                                    <span className="option-header">{option.option}</span>
                                    <p>{option.description}</p>
                                </div>
                            </label>
                        ))}
                    </div>
                    <div className="interaction-style">
            <label>What kind of day-to-day interaction do you like?</label>
            {[
              { id: 'customer-facing', option: '🤝 Customer-facing', description: 'I love talking to customers, selling & pitching every day' },
              { id: 'collaboration', option: '👥 Collaboration', description: 'I enjoy working in a team, working together to achieve great things' },
              { id: 'independence', option: '🏝 Independence', description: 'I like to work with minimal supervision, and like to grind out tasks on my own' },
              { id: 'leadership', option: '👑 Leadership', description: 'I like to manage a team and group of people, leading everyone in our shared purpose!' }
            ].map(option => (
              <label key={option.id} className="form-check" onClick={(e) => handleInteractionChange(option.id, e)}>
                <input
                  type="checkbox"
                  className="form-check-input"
                  id={option.id}
                  checked={interactionStyles.includes(option.id)}
                  onChange={(e) => handleInteractionChange(option.id, e)}
                  style={{ marginRight: '10px', cursor: 'pointer' }}
                />
                <div>
                  <span className="option-header">{option.option}</span>
                  <p>{option.description}</p>
                </div>
              </label>
            ))}
          </div>
          <div className="upload-section">
          <label htmlFor="file-upload" className="upload-label">Finally, upload your resume!</label>
                <div className="drag-drop-area" onClick={() => document.getElementById('file-upload').click()}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={handleFileDrop}>
                    <input id="file-upload" type="file" style={{ display: 'none' }} onChange={handleFileSelect} accept=".doc,.pdf"/>
                    <p>Select a file or drag and drop here</p>
                    <p className="file-info">DOC or PDF, file size no more than 10MB</p>
                    <button type="submitbutton">Select file</button>
                </div>
            </div>
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
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { FaHome, FaHistory } from 'react-icons/fa';
import Header from './components/Header';
import FormInput from './components/FormInput';
import ResultCard from './components/ResultCard';
import HistoryList from './components/HistoryList';
import './App.css';

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    study_hours: '',
    sleep_hours: '',
    break_frequency: '',
    concentration_level: ''
  });

  // Load saved form data from localStorage on component mount
  useEffect(() => {
    const savedFormData = localStorage.getItem('formData');
    if (savedFormData) {
      setFormData(JSON.parse(savedFormData));
    }
  }, []);

  const handleAnalyze = (data) => {
    localStorage.setItem('studyHabitsUsername', data.input_data.username);
    setAnalysisResult(data);
    setTimeout(() => {
      const resultsElement = document.getElementById('results');
      if (resultsElement) resultsElement.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  // Save form data to localStorage whenever it changes
  const handleFormChange = (newFormData) => {
    setFormData(newFormData);
    localStorage.setItem('formData', JSON.stringify(newFormData));
  };

  return (
    <Router>
      <div className="app-container">
        <Header />
        
        <div className="nav-container">
          <nav className="nav-menu">
            <NavLink 
              to="/" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <FaHome className="nav-icon" /> Home
            </NavLink>
            <NavLink 
              to="/history" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <FaHistory className="nav-icon" /> History
            </NavLink>
          </nav>
        </div>

        <main className="main-content">
          <Routes>
            <Route
              path="/"
              element={
                <>
                  <div className="input-section">
                    <FormInput 
                      onAnalyze={handleAnalyze} 
                      savedData={formData}
                      onFormChange={handleFormChange}
                    />
                  </div>
                  {analysisResult && (
                    <div id="results" className="results-section">
                      <ResultCard result={analysisResult} />
                    </div>
                  )}
                </>
              }
            />
            <Route path="/history" element={<HistoryList />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
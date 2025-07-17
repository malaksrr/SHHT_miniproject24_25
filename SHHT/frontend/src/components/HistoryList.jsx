import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './HistoryList.css';

const HistoryList = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('week');
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteRange, setDeleteRange] = useState('hour');
  const [username, setUsername] = useState('');
  const [inputUsername, setInputUsername] = useState('');
  const [usernames, setUsernames] = useState([]);
  const [loadingUsernames, setLoadingUsernames] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUsername = localStorage.getItem('studyHabitsUsername');
    if (storedUsername) {
      setUsername(storedUsername);
      setInputUsername(storedUsername);
    }
    fetchUsernames();
  }, []);

  useEffect(() => {
    if (username) {
      fetchHistory(username);
    }
  }, [username, timeRange]);

  const fetchUsernames = async () => {
    try {
      setLoadingUsernames(true);
      const res = await axios.get('http://localhost:5000/usernames');
      if (res.data.status === 'success') {
        setUsernames(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching usernames:', err);
    } finally {
      setLoadingUsernames(false);
    }
  };

  const fetchHistory = async (username) => {
    try {
      setLoading(true);
      const res = await axios.get('http://localhost:5000/history', {
        params: { 
          username,
          range: timeRange 
        }
      });
      
      if (res.data.status === 'success') {
        const formattedData = res.data.data.map(session => ({
          ...session,
          timestamp: new Date(session.timestamp).toLocaleString(),
          burnout_risk: session.risk_score > 70,
          risk_probability: session.risk_score
        }));
        setHistory(formattedData);
        setError(null);
      } else {
        throw new Error(res.data.message || 'Failed to load history');
      }
    } catch (err) {
      setError(err.message || 'Failed to load history. Please try again later.');
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (inputUsername.trim()) {
      setUsername(inputUsername.trim());
      localStorage.setItem('studyHabitsUsername', inputUsername.trim());
    }
  };

  const handleClearHistory = async () => {
    if (!username) return;

    try {
      setDeleting(true);
      const res = await axios.delete('http://localhost:5000/clear-history', {
        params: { 
          username,
          range: deleteRange 
        }
      });
      
      if (res.data.status === 'success') {
        await fetchHistory(username);
        setShowConfirm(false);
        alert(`✅ Successfully deleted ${res.data.deleted_count} records from ${getRangeLabel(deleteRange)}`);
      } else {
        throw new Error(res.data.message || 'Failed to clear history');
      }
    } catch (err) {
      setError(err.message || 'Failed to clear history. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  const getRangeLabel = (range) => {
    const rangeLabels = {
      hour: 'the last hour',
      day: 'the last day',
      week: 'the last week',
      month: 'the last month',
      all: 'all time'
    };
    return rangeLabels[range] || range;
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner"></div>
        Loading your study history...
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        <p>⚠️ {error}</p>
        <button onClick={() => fetchHistory(username)}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="user-search-container">
        <form onSubmit={handleSearch} className="user-search-form">
          <input
            type="text"
            list="usernames-list"
            value={inputUsername}
            onChange={(e) => setInputUsername(e.target.value)}
            placeholder="Enter username to view history"
            className="user-search-input"
          />
          <datalist id="usernames-list">
            {usernames.map((name) => (
              <option key={name} value={name} />
            ))}
          </datalist>
          <button 
            type="submit" 
            className="search-button"
            disabled={loadingUsernames}
          >
            {loadingUsernames ? 'Loading...' : 'Search History'}
          </button>
        </form>
        {usernames.length > 0 && (
          <div className="username-suggestions">
            <p>Recent users: {usernames.slice(0, 3).join(', ')}...</p>
          </div>
        )}
      </div>

      {username && (
        <>
          <div className="history-header">
            <h3>{username}'s Study History ({history.length} sessions)</h3>
            <div className="time-range-selector">
              <label>Time Range:</label>
              <select
                className="time-range-select"
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                disabled={deleting}
              >
                <option value="hour">Last Hour</option>
                <option value="day">Last Day</option>
                <option value="week">Last Week</option>
                <option value="month">Last Month</option>
                <option value="all">All Time</option>
              </select>
            </div>
            {history.length > 0 && (
              <button 
                className="clear-history-btn"
                onClick={() => setShowConfirm(true)}
                disabled={deleting}
              >
                {deleting ? 'Clearing...' : 'Clear History'}
              </button>
            )}
          </div>

          {showConfirm && (
            <div className="confirmation-dialog">
              <h4>Confirm Deletion</h4>
              <div className="form-group">
                <label>Delete records from:</label>
                <select
                  className="delete-range-select"
                  value={deleteRange}
                  onChange={(e) => setDeleteRange(e.target.value)}
                  disabled={deleting}
                >
                  <option value="hour">Last Hour</option>
                  <option value="day">Last Day</option>
                  <option value="week">Last Week</option>
                  <option value="month">Last Month</option>
                  <option value="all">All Time</option>
                </select>
              </div>
              
              <div className="warning-message">
                <p>⚠️ This will permanently delete all records from {getRangeLabel(deleteRange)}!</p>
                <p>This action cannot be undone.</p>
              </div>

              <div className="action-buttons">
                <button
                  className="cancel-btn"
                  onClick={() => setShowConfirm(false)}
                  disabled={deleting}
                >
                  Cancel
                </button>
                <button
                  className="confirm-btn danger"
                  onClick={handleClearHistory}
                  disabled={deleting}
                >
                  {deleting ? (
                    <>
                      <span className="spinner small"></span> Deleting...
                    </>
                  ) : (
                    `Delete ${getRangeLabel(deleteRange)}`
                  )}
                </button>
              </div>
            </div>
          )}

          {history.length === 0 ? (
            <div className="empty-state">
              <p>No study sessions recorded yet for {username}.</p>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Study Hours</th>
                    <th>Sleep Hours</th>
                    <th>Break Frequency</th>
                    <th>Concentration</th>
                    <th>Burnout Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((session) => (
                    <tr 
                      key={session.id} 
                      className={
                        session.risk_score > 70 ? 'high-risk' : 
                        session.risk_score > 40 ? 'medium-risk' : 'low-risk'
                      }
                    >
                      <td>{session.timestamp}</td>
                      <td>{session.study_hours}h</td>
                      <td>{session.sleep_hours}h</td>
                      <td>Every {session.break_frequency} min</td>
                      <td>
                        <div className="concentration-rating">
                          {[1, 2, 3, 4, 5].map((num) => (
                            <span
                              key={num}
                              className={num <= session.concentration_level ? 'active' : ''}
                            >
                              ★
                            </span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <span className={`risk-badge ${session.risk_level || 
                          (session.risk_score > 70 ? 'high' : 
                           session.risk_score > 40 ? 'medium' : 'low')}`}>
                          {session.risk_score > 70 ? 'High' : 
                           session.risk_score > 40 ? 'Medium' : 'Low'} Risk
                          {session.risk_probability && (
                            <span className="probability">
                              ({Math.round(session.risk_probability)}%)
                            </span>
                          )}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default HistoryList;
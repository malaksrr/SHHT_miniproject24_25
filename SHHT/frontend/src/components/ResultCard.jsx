import React from 'react';
import './ResultCard.css';

const ResultCard = ({ result }) => {
  if (!result) return null;

  // Safely access properties with defaults
  const mlPrediction = result.ml_prediction || { risk_score: 0 };
  const ruleAnalysis = result.rule_based_analysis || { warnings: [], recommendations: [] };
  const recommendations = result.recommendations || [];

  // Ensure risk score is between 0-100 (some models output 0-1, others 0-100)
  const rawRiskScore = parseFloat(mlPrediction.risk_score || 0);
  const normalizedRiskScore = rawRiskScore > 1 ? rawRiskScore : rawRiskScore * 100;
  const riskPercentage = Math.min(100, Math.max(0, normalizedRiskScore)).toFixed(1);

  const getRiskColor = () => {
    const score = parseFloat(riskPercentage);
    if (score > 70) return '#e53935'; // Red for high risk
    if (score > 40) return '#ff8c00a5'; // Orange for medium risk
    return '#43a047'; // Green for low risk
  };

  return (
    <div className="result-card">
      <div className="card-header">
        <h3>📊 Analysis Results</h3>
      </div>

      {/* Burnout Risk Meter */}
      <div className="risk-section">
        <div className="risk-meter">
          <div
            className="risk-progress"
            style={{
              width: `${riskPercentage}%`,
              backgroundColor: getRiskColor()
            }}
          ></div>
        </div>
        <div className="risk-percentage" style={{ color: getRiskColor() }}>
          Burnout Risk: {riskPercentage}%
          {parseFloat(riskPercentage) > 70 && (
            <span className="risk-alert"> ⚠️ High Risk</span>
          )}
        </div>
      </div>

      {/* Warnings Section */}
      {ruleAnalysis.warnings && ruleAnalysis.warnings.length > 0 && (
        <div className="section">
          <h4>⚠️ Warnings</h4>
          <ul>
            {ruleAnalysis.warnings.map((warning, index) => (
              <li key={index} className="warning-item">{warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations Section */}
      {recommendations.length > 0 && (
        <div className="section">
          <h4>💡 Recommendations</h4>
          <ul>
            {recommendations.map((recommendation, index) => (
              <li key={index} className="recommendation-item">{recommendation}</li>
            ))}
          </ul>
        </div>
      )}

      {/* ChatGPT Advice Section */}
      {result.chatgpt_advice && (
        <div className="section chatgpt-section">
          <h4> Smart Coach Advice</h4>
          <p>{result.chatgpt_advice}</p>
        </div>
      )}




      {/* Debug Info (remove in production) */}
      <div className="debug-info">
        <small>Raw Risk Score: {rawRiskScore.toFixed(4)}</small>
        {mlPrediction.error && (
          <small className="error">Error: {mlPrediction.error}</small>
        )}
      </div>
    </div>
  );
};

export default ResultCard;
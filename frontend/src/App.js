import React, { useEffect, useState } from 'react';
import './App.css';
import API_BASE_URL from './config';

function App() {
  const [latestRecommendations, setLatestRecommendations] = useState([]);
  const [expanded, setExpanded] = useState({});

  const toggleOverview = (contentId) => {
    setExpanded((prev) => ({
      ...prev,
      [contentId]: !prev[contentId],
    }));
  };

  useEffect(() => {
    console.log("API ENDPOINT:", API_BASE_URL);

    fetch(`${API_BASE_URL}/latest-recommendations`)
      .then(res => res.json())
      .then(data => {
        setLatestRecommendations(data.recent_recommendations || []);
      });
  }, []);

  const renderCards = (recommendations) => (
    <div className="recommendation-grid">
      {recommendations.map((item) => (
        <div
          className="card"
          key={item.content_id}
          onClick={() => toggleOverview(item.content_id)}
        >
          <img className="poster" src={item.poster_url} alt={item.title} />
          <div className="title">{item.title}</div>
          {expanded[item.content_id] && (
            <div className="overview">{item.overview || "줄거리 없음"}</div>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <div className="App">
      <h1>🎬 영화 추천</h1>
      {renderCards(latestRecommendations)}
    </div>
  );
}

export default App;

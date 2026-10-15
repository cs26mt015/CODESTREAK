import { useEffect, useState } from "react";

export default function App() {
  const [apiStatus, setApiStatus] = useState("Checking API...");

  useEffect(() => {
    fetch("/api/health")
      .then((response) => {
        if (!response.ok) throw new Error("API unavailable");
        return response.json();
      })
      .then((data) => setApiStatus(data.status === "ok" ? "Connected" : "Unavailable"))
      .catch(() => setApiStatus("Unavailable"));
  }, []);

  return (
    <main className="page">
      <nav className="navbar">
        <a className="brand" href="/">CodeStreak<span>.</span></a>
        <span className="nav-label">COMPETITIVE PROGRAMMING</span>
      </nav>

      <section className="hero">
        <div className="eyebrow"><span className="dot" /> YOUR NEXT STREAK STARTS HERE</div>
        <h1>Practice smarter.<br /><span>Stay consistent.</span></h1>
        <p className="intro">
          Build your problem-solving skills, track your progress,
          and turn daily practice into a habit.
        </p>

        <div className="actions">
          <a className="primary-button" href="/docs">Explore API <span>↗</span></a>
          <a className="secondary-button" href="/api/health">Check backend</a>
        </div>

        <div className="status-card">
          <div className="status-icon">✓</div>
          <div>
            <strong>Backend status</strong>
            <p>FastAPI connection: {apiStatus}</p>
          </div>
          <span className="status-dot" />
        </div>
      </section>

      <footer>CODESTREAK · BUILD YOUR DAILY PRACTICE HABIT</footer>
    </main>
  );
}

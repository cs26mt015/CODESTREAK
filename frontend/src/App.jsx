const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'

function App() {
  return (
    <main className="page">
      <section className="welcome-card" aria-labelledby="page-title">
        <p className="eyebrow">ASDL · Application</p>
        <h1 id="page-title">Frontend is ready</h1>
        <p className="description">
          The React application is set up and ready for the project interface.
        </p>
        <div className="connection">
          <span className="connection-dot" aria-hidden="true" />
          <span>API base URL</span>
          <code>{apiBaseUrl}</code>
        </div>
      </section>
    </main>
  )
}

export default App

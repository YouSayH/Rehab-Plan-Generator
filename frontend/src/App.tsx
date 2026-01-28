import { useState, useEffect } from 'react'

function App() {
  const [message, setMessage] = useState('Loading...')

  useEffect(() => {
    // Backendへの接続テスト
    // Nginx経由なので http://localhost/api/ が Backendに繋がる
    fetch('/api/')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => setMessage(`Connection Error: ${err}`))
  }, [])

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Rehab Plan Generator (Phase 1)</h1>
      <hr />
      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ border: '1px solid #ccc', padding: '10px', width: '50%' }}>
          <h2>Frontend Status</h2>
          <p>React 19 is running!</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '10px', width: '50%' }}>
          <h2>Backend Status</h2>
          <p>Response: <strong>{message}</strong></p>
        </div>
      </div>
    </div>
  )
}

export default App
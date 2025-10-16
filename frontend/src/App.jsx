import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import UnifiedSearch from './pages/UnifiedSearch'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<UnifiedSearch />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';

import Register from './pages/Register';
import InteractiveMap from './pages/Map';
import ChatProfiler from './pages/ChatProfiler';
import { ChatProvider } from './context/ChatContext';

function App() {
  return (
    <ChatProvider>
      <Router>
        <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profiler" element={<ChatProfiler />} />
        <Route path="/dashboard" element={<InteractiveMap />} />
      </Routes>
    </Router>
    </ChatProvider>
  );
}

export default App;

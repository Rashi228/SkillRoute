import type { ReactNode } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Register from './pages/Register';
import InteractiveMap from './pages/Map';
import ChatProfiler from './pages/ChatProfiler';
import { ChatProvider } from './context/ChatContext';

function RequireAccess({ children }: { children: ReactNode }) {
  const hasAccess = localStorage.getItem('skillroute_access_granted') === 'true';
  return hasAccess ? children : <Navigate to="/" replace />;
}

function App() {
  return (
    <ChatProvider>
      <Router>
        <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profiler" element={<RequireAccess><ChatProfiler /></RequireAccess>} />
        <Route path="/dashboard" element={<RequireAccess><InteractiveMap /></RequireAccess>} />      
      </Routes>
    </Router>
    </ChatProvider>
  );
}

export default App;

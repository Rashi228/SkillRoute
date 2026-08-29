import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, CheckCircle, Loader2, Compass, BrainCircuit, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useChatContext } from '../context/ChatContext';

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function ChatProfiler() {
  const { messages, setMessages, profile, setProfile, isComplete, setIsComplete, chats, currentChatId, setCurrentChatId, createNewChat } = useChatContext();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();
  
  const userEmail = localStorage.getItem('userEmail') || 'ADMIN@SKILLROUTE.COM';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    if (!input.trim() || isComplete) return;

    const userMessage = input;
    setInput('');
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setLoading(true);

    // Artificial delay to allow user to see the Thought Process steps (12s)
    await new Promise(resolve => setTimeout(resolve, 12000));

    try {
      const res = await fetch(`${API_URL}/api/chat/profiler`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          history: newMessages.slice(0, -1)
        })
      });

      const data = await res.json();
      
      setProfile(data.profile);
      
      if (data.is_complete) {
        setIsComplete(true);
        setMessages(prev => [...prev, { 
          role: 'ai', 
          content: "Perfect! I have all the information I need. I've generated your Learner Profile. Let's go to your Interactive Map!" 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          role: 'ai', 
          content: data.follow_up_question || "Could you tell me more about your current skills and available time?" 
        }]);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'ai', content: "Sorry, I had trouble connecting to my brain. Is the backend running?" }]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    createNewChat();
  };

  return (
    <div className="h-screen bg-[#F8FAFC] flex font-sans overflow-hidden">
      
      {/* Left Sidebar (Dark Mode Navigation) */}
      <div className="w-64 bg-[#111827] text-slate-300 flex flex-col flex-shrink-0 shadow-2xl z-20">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3">
          <div className="p-1.5 bg-teal-500 rounded-lg">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <span className="text-white font-bold tracking-tight">SkillRoute</span>
        </div>
        
        {/* Navigation Sections */}
        <div className="p-4 flex-1 overflow-y-auto">
          
          <div className="text-xs font-bold text-slate-500 mb-4 mt-2 flex justify-between items-center">
            <span>RECENT CHATS</span>
            <span className="cursor-pointer hover:text-white" onClick={handleNewChat} title="New Chat">+</span>
          </div>
          <div className="space-y-1">
            {chats.map(chat => (
              <button 
                key={chat.id}
                onClick={() => setCurrentChatId(chat.id)}
                className={`w-full text-left p-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${chat.id === currentChatId ? 'bg-slate-800 text-teal-400' : 'text-slate-500 hover:bg-slate-800 hover:text-slate-300'}`}
              >
                <Bot className="w-4 h-4" /> {chat.title}
              </button>
            ))}
          </div>
        </div>
        
        {/* User Profile */}
        <div className="p-4 border-t border-slate-800 flex items-center gap-3 hover:bg-slate-800 cursor-pointer transition-colors">
          <div className="w-8 h-8 bg-teal-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
            ME
          </div>
          <div>
            <div className="text-sm font-bold text-white">My Workspace</div>
            <div className="text-[10px] text-slate-500 uppercase">{userEmail}</div>
          </div>
        </div>
      </div>

      {/* Middle Column (Chat Area) */}
      <div className="flex-1 flex flex-col bg-white border-r border-slate-200 shadow-xl z-10 relative">
        <div className="h-14 border-b border-slate-100 flex items-center px-6 gap-3">
          <Bot className="w-5 h-5 text-teal-600" />
          <h1 className="font-bold text-slate-800">Learning Coach Chat</h1>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 pb-40">
          {messages.map((msg: any, idx: any) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'ai' && (
                <div className="w-8 h-8 rounded bg-teal-50 flex items-center justify-center flex-shrink-0 border border-teal-100 mt-auto mb-2">
                  <Bot className="w-5 h-5 text-teal-700" />
                </div>
              )}
              
              <div className="flex flex-col max-w-[80%]">
                {/* Thought Process for AI responses (skip the first greeting) */}
                {msg.role === 'ai' && idx > 0 && (
                  <ThoughtProcess isRunning={false} />
                )}

                <div className={`px-5 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                  msg.role === 'user' 
                    ? 'bg-slate-100 text-slate-800 rounded-br-none ml-auto' 
                    : 'text-slate-700 bg-white border border-slate-100 rounded-tl-none'
                }`}>
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-4 justify-start">
              <div className="w-8 h-8 rounded bg-teal-50 flex items-center justify-center flex-shrink-0 border border-teal-100 mt-2">
                <Bot className="w-5 h-5 text-teal-700" />
              </div>
              <div className="w-full max-w-[80%]">
                <ThoughtProcess isRunning={true} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-white via-white to-transparent">
          {/* Quick Action Pills */}
          {!isComplete && (
            <div className="flex flex-wrap gap-2 mb-4">
              <span className="text-[10px] font-bold text-slate-400 uppercase mr-2 flex items-center">Context:</span>
              <button type="button" onClick={() => setInput("Software Engineering")} className="px-3 py-1 bg-teal-50 text-teal-700 text-xs font-semibold rounded-full border border-teal-200 shadow-sm hover:bg-teal-100 transition-colors">Software Engineering</button>
              <button type="button" onClick={() => setInput("No Budget")} className="px-3 py-1 bg-teal-50 text-teal-700 text-xs font-semibold rounded-full border border-teal-200 shadow-sm hover:bg-teal-100 transition-colors">No Budget</button>
              <button type="button" onClick={() => setInput("6 Months")} className="px-3 py-1 bg-teal-50 text-teal-700 text-xs font-semibold rounded-full border border-teal-200 shadow-sm hover:bg-teal-100 transition-colors">6 Months</button>
            </div>
          )}

          <form onSubmit={handleSubmit} className="relative">
            <input 
              type="text" 
              value={input}
              onChange={(e: any) => setInput(e.target.value)}
              disabled={loading || isComplete}
              placeholder={isComplete ? "Profile complete! Click the button below." : "Ask across all your skills..."}
              className="w-full pl-6 pr-14 py-4 bg-white border border-slate-200 rounded-xl focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10 outline-none transition-all disabled:opacity-50 text-sm shadow-sm"
            />
            <button 
              type="submit"
              disabled={loading || !input.trim() || isComplete}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 disabled:opacity-50 transition-colors shadow-sm"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="text-center mt-2">
            <span className="text-[10px] text-slate-400">AI answers can vary. Always review generated routes.</span>
          </div>

          {isComplete && (
            <div className="mt-4 flex justify-center">
              <button onClick={() => navigate('/dashboard')} className="bg-[#2D6A62] hover:bg-teal-700 text-white px-8 py-3 rounded-lg font-bold flex items-center gap-3 transition-colors shadow-lg hover:-translate-y-0.5 duration-200">
                <CheckCircle className="w-5 h-5 text-teal-200" /> 
                <span>Generate & View Map</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Right Column (Live Profile Context) */}
      <div className="w-80 bg-[#FAFAFA] flex flex-col flex-shrink-0 z-0">
        <div className="h-14 border-b border-slate-200 flex items-center justify-between px-4">
          <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-teal-500"></span>
            Live Profile Context
          </h3>
        </div>
        
        <div className="p-6 space-y-6 flex-1 overflow-y-auto">
          <ProfileField label="Target Goal" value={profile?.target_goal} />
          <ProfileField label="Current Skills" value={profile?.current_skills?.join(", ")} />
          <ProfileField label="Budget" value={profile?.budget} />
          <ProfileField label="Time Commitment" value={profile?.time_commitment} />
          <ProfileField label="Deadline" value={profile?.deadline} />
        </div>
      </div>
    </div>
  );
}

const ProfileField = ({ label, value }: any) => (
  <div className="mb-4">
    <div className="text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">{label}</div>
    <div className={`text-sm ${value ? 'text-slate-800' : 'text-slate-400 italic'}`}>
      {value || 'Not yet identified'}
    </div>
  </div>
);

function MapIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon>
      <line x1="9" x2="9" y1="3" y2="18"></line>
      <line x1="15" x2="15" y1="6" y2="21"></line>
    </svg>
  );
}

const ThoughtProcess = ({ isRunning = false }: { isRunning: boolean }) => {
  const [expanded, setExpanded] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (isRunning) {
      setCurrentStep(0);
      const interval = setInterval(() => {
        setCurrentStep(prev => Math.min(prev + 1, 3));
      }, 3000); // Advance step every 3 seconds
      return () => clearInterval(interval);
    }
  }, [isRunning]);

  const steps = [
    { name: 'Intent Extraction (Goals)', status: isRunning ? (currentStep > 0 ? 'done' : currentStep === 0 ? 'loading' : 'pending') : 'done' },
    { name: 'Gap Analysis (Skill Mapping)', status: isRunning ? (currentStep > 1 ? 'done' : currentStep === 1 ? 'loading' : 'pending') : 'done' },
    { name: 'DAG Sequencing (Pathways)', status: isRunning ? (currentStep > 2 ? 'done' : currentStep === 2 ? 'loading' : 'pending') : 'done' },
    { name: 'Roadmap Generation (Finalizing)', status: isRunning ? (currentStep > 3 ? 'done' : currentStep === 3 ? 'loading' : 'pending') : 'done' },
  ];

  if (isRunning) {
    return (
      <div className="bg-white border border-slate-100 rounded-2xl p-4 w-full shadow-sm mb-4">
        <div className="text-[10px] font-bold text-slate-500 tracking-widest uppercase mb-4 flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin text-[#6366f1]" />
          SKILLROUTE-X — PRIVATE MODE RUNNING
        </div>
        <div className="space-y-3">
          {steps.map((step, i) => (
            <div key={i} className="flex items-center gap-3 bg-slate-50 p-3 rounded-xl border border-slate-100">
              {step.status === 'done' ? (
                <div className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-white" />
                </div>
              ) : step.status === 'loading' ? (
                <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center">
                  <Loader2 className="w-4 h-4 text-indigo-500 animate-spin" />
                </div>
              ) : (
                <div className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center">
                  <div className="w-2 h-2 rounded-full bg-slate-400"></div>
                </div>
              )}
              <div>
                <div className="text-sm font-bold text-slate-700">{step.name}</div>
                <div className={`text-[10px] font-medium ${step.status === 'done' ? 'text-emerald-600' : 'text-slate-500'}`}>
                  {step.status === 'done' ? '✓ Complete' : step.status === 'loading' ? 'Processing...' : 'Waiting'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="mb-3">
      <button 
        onClick={() => setExpanded(!expanded)} 
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 bg-white hover:bg-slate-50 px-3 py-1.5 rounded-xl transition-colors border border-slate-200 shadow-sm"
      >
        <BrainCircuit className="w-3.5 h-3.5 text-indigo-500" />
        View Thought Process
        <ChevronDown className={`w-3 h-3 transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </button>
      {expanded && (
        <div className="mt-2 p-4 bg-slate-50 border border-slate-200 rounded-xl max-w-md">
          <ul className="space-y-3">
            {steps.map((step, i) => (
              <li key={i} className="text-xs text-slate-600 flex items-center gap-2 font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                {step.name} — <span className="font-bold text-emerald-600">Done</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};



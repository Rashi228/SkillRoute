import { useState, useCallback, useMemo } from 'react';
import { 
  ReactFlow, Controls, Background, MiniMap, 
  applyNodeChanges, applyEdgeChanges, addEdge,
  MarkerType, Handle, Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { 
  Target, Map as MapIcon, Loader2, Bot, Send, 
  ChevronDown, MessageSquare, CheckCircle, Lock,
  PlaySquare, BookOpen, Wrench, X, Compass, Activity, 
  ArrowRight
} from 'lucide-react';
import { useChatContext } from '../context/ChatContext';

// --- CUSTOM NODES ---

const ResourceNode = ({ data, selected }) => {
  const isGoal = data.status === 'goal';
  const isCurrent = data.status === 'current';
  
  if (isGoal) {
    return (
      <div className={`px-6 py-4 rounded-2xl border-2 shadow-lg transition-all duration-300 ${selected ? 'border-amber-500 scale-105 shadow-amber-500/20 bg-amber-50' : 'border-amber-400 bg-white'} w-64 text-center`}>
        <Handle type="target" position={Position.Bottom} className="w-2 h-2 !bg-amber-500" />
        <div className="flex justify-center mb-2">
          <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center border border-amber-200">
            <Target className="w-5 h-5 text-amber-600" />
          </div>
        </div>
        <div className="text-amber-600 font-bold text-[10px] tracking-widest uppercase mb-1">Destination Target</div>
        <div className="font-bold text-slate-900 text-lg">{data.skill_name}</div>
      </div>
    );
  }

  if (isCurrent) {
    return (
      <div className="px-4 py-2 rounded-full bg-teal-50 border border-teal-500 text-teal-700 text-xs font-bold flex items-center gap-2 shadow-sm">
        <div className="w-2 h-2 rounded-full bg-teal-500 animate-pulse" />
        YOU ARE HERE
        <Handle type="source" position={Position.Top} className="opacity-0" />
      </div>
    );
  }

  const statusConfig = {
    'completed': {
      border: 'border-emerald-500',
      bg: 'bg-white',
      shadow: 'shadow-sm',
      icon: <CheckCircle className="w-4 h-4 text-emerald-500" />,
      text: 'text-emerald-600',
      label: 'Completed'
    },
    'in-progress': {
      border: 'border-teal-500',
      bg: 'bg-teal-50',
      shadow: 'shadow-md shadow-teal-500/10',
      icon: <Activity className="w-4 h-4 text-teal-600 animate-pulse" />,
      text: 'text-teal-700',
      label: 'In Progress'
    },
    'next': {
      border: 'border-blue-500',
      bg: 'bg-blue-50',
      shadow: 'shadow-md shadow-blue-500/10',
      icon: <ArrowRight className="w-4 h-4 text-blue-600" />,
      text: 'text-blue-700',
      label: 'Next Recommended'
    },
    'locked': {
      border: 'border-slate-200',
      bg: 'bg-slate-50',
      shadow: 'shadow-none',
      icon: <Lock className="w-4 h-4 text-slate-400" />,
      text: 'text-slate-500',
      label: 'Locked'
    }
  };

  const config = statusConfig[data.status] || statusConfig['locked'];

  return (
    <div className={`px-4 py-3 rounded-xl border-2 transition-all duration-300 w-60 ${config.bg} ${config.border} ${config.shadow} ${selected ? 'ring-4 ring-blue-500/20 scale-105' : 'hover:scale-[1.02]'}`}>
      <Handle type="target" position={Position.Bottom} className="w-2 h-2 !bg-slate-400 border-none" />
      <div className="flex items-center justify-between mb-2">
        <div className={`flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider ${config.text}`}>
          {config.icon}
          {config.label}
        </div>
      </div>
      <div className={`font-bold text-sm mb-3 ${data.status === 'locked' ? 'text-slate-500' : 'text-slate-900'}`}>
        {data.skill_name}
      </div>
      
      {/* Resource Indicators */}
      {data.resources && data.status !== 'locked' && (
        <div className="flex gap-2">
          {data.resources.some(r => r.type === 'video') && <div className="p-1 rounded bg-red-50 border border-red-100"><PlaySquare className="w-3 h-3 text-red-500" /></div>}
          {data.resources.some(r => r.type === 'course') && <div className="p-1 rounded bg-blue-50 border border-blue-100"><BookOpen className="w-3 h-3 text-blue-500" /></div>}
          {data.resources.some(r => r.type === 'project') && <div className="p-1 rounded bg-amber-50 border border-amber-100"><Wrench className="w-3 h-3 text-amber-600" /></div>}
        </div>
      )}
      <Handle type="source" position={Position.Top} className="w-2 h-2 !bg-slate-400 border-none" />
    </div>
  );
};

// --- DATA STRUCTURES ---

const initialNodes = [
  { id: 'goal', type: 'resource', position: { x: 400, y: -100 }, data: { status: 'goal', skill_name: 'Production RAG Engineer' } },
  { id: 'n8', type: 'resource', position: { x: 100, y: 100 }, data: { status: 'locked', skill_name: 'Docker & Kubernetes', resources: [{type: 'course'}] } },
  { id: 'n9', type: 'resource', position: { x: 400, y: 100 }, data: { status: 'locked', skill_name: 'Evaluation Metrics', resources: [{type: 'video'}] } },
  { id: 'n10', type: 'resource', position: { x: 700, y: 100 }, data: { status: 'locked', skill_name: 'Advanced Agents', resources: [{type: 'project'}] } },
  { id: 'n7', type: 'resource', position: { x: 400, y: 250 }, data: { status: 'locked', skill_name: 'RAG Pipeline Architecture', resources: [{type: 'video'}, {type: 'project'}] } },
  { id: 'n6', type: 'resource', position: { x: 400, y: 400 }, data: { status: 'locked', skill_name: 'Vector Search Algorithms', resources: [{type: 'article'}] } },
  { id: 'n4', type: 'resource', position: { x: 200, y: 550 }, data: { status: 'next', skill_name: 'Vector Databases (Pinecone)', resources: [{type: 'course'}, {type: 'video'}] } },
  { id: 'n5', type: 'resource', position: { x: 600, y: 550 }, data: { status: 'in-progress', skill_name: 'Embeddings & Transformers', resources: [{type: 'video'}] } },
  { id: 'n3', type: 'resource', position: { x: 400, y: 700 }, data: { status: 'completed', skill_name: 'Machine Learning Basics', resources: [] } },
  { id: 'n1', type: 'resource', position: { x: 200, y: 850 }, data: { status: 'completed', skill_name: 'Python Programming', resources: [] } },
  { id: 'n2', type: 'resource', position: { x: 600, y: 850 }, data: { status: 'completed', skill_name: 'Statistics & Probability', resources: [] } },
  { id: 'current', type: 'resource', position: { x: 600, y: 650 }, data: { status: 'current', skill_name: '' } }
];

const defaultEdgeStyle = { stroke: '#cbd5e1', strokeWidth: 2 };
const activeEdgeStyle = { stroke: '#0284c7', strokeWidth: 3 };

const createEdge = (source, target, label, isActive = false) => ({
  id: `e-${source}-${target}`,
  source,
  target,
  label,
  animated: isActive,
  style: isActive ? activeEdgeStyle : defaultEdgeStyle,
  labelStyle: { fill: '#64748b', fontSize: 10, fontWeight: 700 },
  labelBgStyle: { fill: '#ffffff', fillOpacity: 0.9 },
  labelBgPadding: [4, 2],
  labelBgBorderRadius: 4,
  markerEnd: { type: MarkerType.ArrowClosed, color: isActive ? '#0284c7' : '#94a3b8' },
});

const initialEdges = [
  createEdge('n1', 'n3', 'Prerequisite'),
  createEdge('n2', 'n3', 'Prerequisite'),
  createEdge('n3', 'n4', 'Builds On', true),
  createEdge('n3', 'n5', 'Builds On', true),
  createEdge('current', 'n5', '', true),
  createEdge('n4', 'n6', 'Related'),
  createEdge('n5', 'n6', 'Prerequisite'),
  createEdge('n6', 'n7', 'Builds On'),
  createEdge('n7', 'n8', 'Leads To'),
  createEdge('n7', 'n9', 'Leads To'),
  createEdge('n7', 'n10', 'Leads To'),
  createEdge('n8', 'goal', 'Required'),
  createEdge('n9', 'goal', 'Required'),
  createEdge('n10', 'goal', 'Required'),
];

export default function InteractiveMap() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
  const [selectedNode, setSelectedNode] = useState(null);
  const [activeRouteMode, setActiveRouteMode] = useState('BALANCED');

  // Chat Overlay State
  const { messages, setMessages } = useChatContext();
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');

  const nodeTypes = useMemo(() => ({ resource: ResourceNode }), []);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
  
  const onNodeClick = useCallback((event, node) => {
    if (node.id === 'current') return;
    setSelectedNode(node);
  }, []);

  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    setMessages(prev => [...prev, { role: 'user', content: chatInput }]);
    setChatInput('');
    setTimeout(() => {
      setMessages(prev => [...prev, { role: 'ai', content: "I've noted that! I can adjust the graph based on your new preferences." }]);
    }, 1000);
  };

  const handleRouteSelect = (mode) => {
    setActiveRouteMode(mode);
  };

  return (
    <div className="h-screen w-full flex bg-slate-50 font-sans text-slate-700 overflow-hidden">
      
      {/* LEFT SIDEBAR: Routes (250px) */}
      <div className="w-[250px] bg-white border-r border-slate-200 flex flex-col z-10 shadow-sm">
        <div className="p-5 border-b border-slate-100">
          <div className="flex items-center gap-2 mb-1">
            <Compass className="w-5 h-5 text-teal-600" />
            <h1 className="text-lg font-bold text-slate-900 tracking-tight">Route Planner</h1>
          </div>
          <p className="text-xs text-slate-500">Select your preferred learning path</p>
        </div>
        
        <div className="p-4 flex-1 overflow-y-auto">
          <div className="space-y-3">
            {[
              { id: 'FAST', title: 'FAST TRACK', time: '12.5 hrs', stops: 3, desc: 'Direct, covers minimum requirements.' },
              { id: 'BALANCED', title: 'BALANCED', time: '24 hrs', stops: 6, desc: 'Recommended. Mix of theory and practice.' },
              { id: 'DEEP', title: 'DEEP DIVE', time: '40 hrs', stops: 12, desc: 'Comprehensive. Master every concept.' }
            ].map(route => (
              <button 
                key={route.id}
                onClick={() => handleRouteSelect(route.id)}
                className={`w-full text-left p-3 rounded-xl border transition-all duration-300 ${activeRouteMode === route.id ? 'bg-teal-50 border-teal-200 shadow-sm ring-1 ring-teal-500' : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50'}`}
              >
                <div className="flex justify-between items-center mb-1">
                  <div className={`font-bold text-sm ${activeRouteMode === route.id ? 'text-teal-700' : 'text-slate-700'}`}>{route.title}</div>
                  <div className="text-xs text-slate-500 font-mono">{route.time}</div>
                </div>
                <div className="text-[11px] text-slate-500 mb-2">{route.desc}</div>
                <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">{route.stops} STOPS • FREE</div>
              </button>
            ))}
          </div>

          <div className="mt-8 p-4 bg-blue-50 border border-blue-100 rounded-xl">
            <div className="text-xs font-bold text-blue-700 mb-2 flex items-center gap-2">
              <Bot className="w-3 h-3" />
              WHY THIS ROUTE?
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              SkillRoute selected this path because you already know Python and ML Basics. Vector Search is your largest gap to reach Production RAG.
            </p>
          </div>
        </div>
      </div>

      {/* CENTER: React Flow Map (Flexible) */}
      <div className="flex-1 relative flex flex-col min-w-0">
        
        {/* Top Header Overlay */}
        <div className="absolute top-0 left-0 right-0 p-6 z-10 pointer-events-none flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight drop-shadow-sm">Your Learning Map</h2>
            <p className="text-sm text-slate-600 font-medium">Your personalized route to Production RAG Engineer</p>
          </div>
          <div className="pointer-events-auto bg-white border border-slate-200 rounded-lg p-1.5 flex gap-1 shadow-sm">
            <button className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-900 rounded transition-colors">Fit Map</button>
            <div className="w-px bg-slate-200 my-1 mx-1" />
            <button className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-900 rounded transition-colors">Reset</button>
          </div>
        </div>

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          className="bg-slate-50"
          minZoom={0.2}
          maxZoom={1.5}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#cbd5e1" gap={20} size={1} />
          <Controls className="!bg-white !border-slate-200 !fill-slate-600 shadow-sm" />
          <MiniMap 
            className="!bg-white !border-slate-200 rounded-lg overflow-hidden shadow-sm"
            nodeColor={(node) => {
              if (node.data?.status === 'completed') return '#10b981';
              if (node.data?.status === 'in-progress') return '#0d9488';
              if (node.data?.status === 'next') return '#2563eb';
              if (node.data?.status === 'goal') return '#d97706';
              return '#e2e8f0';
            }}
            maskColor="rgba(248, 250, 252, 0.7)"
          />
        </ReactFlow>

        {/* Legend */}
        <div className="absolute bottom-6 left-6 z-10 bg-white/90 backdrop-blur border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs font-bold text-slate-500 mb-3 tracking-wider">LEGEND</div>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-[11px] font-medium text-slate-600">
            <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500" /> Completed</div>
            <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-teal-600" /> In Progress</div>
            <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-600" /> Next</div>
            <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-slate-300" /> Locked</div>
            <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-amber-500" /> Goal</div>
          </div>
        </div>

        {/* Floating Chat Overlay */}
        <div className="absolute bottom-6 right-6 z-50 flex flex-col items-end">
          {isChatOpen ? (
            <div className="w-80 h-96 bg-white rounded-2xl shadow-xl flex flex-col border border-slate-200 overflow-hidden transition-all duration-300">
              <div className="bg-[#2D6A62] p-3 flex justify-between items-center cursor-pointer border-b border-[#21524b]" onClick={() => setIsChatOpen(false)}>
                <div className="flex items-center gap-2">
                  <Bot className="w-4 h-4 text-teal-100" />
                  <span className="font-bold text-sm text-white">AI Coach</span>
                </div>
                <button className="text-teal-100 hover:text-white transition-colors"><ChevronDown className="w-5 h-5" /></button>
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`px-3 py-2 rounded-xl text-xs max-w-[85%] shadow-sm ${
                      msg.role === 'user' ? 'bg-[#2D6A62] text-white rounded-br-none' : 'bg-white border border-slate-200 text-slate-700 rounded-bl-none'
                    }`}>
                      {msg.content}
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-3 bg-white border-t border-slate-100">
                <form onSubmit={handleChatSubmit} className="relative">
                  <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} placeholder="Modify path..." className="w-full pl-3 pr-10 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:border-teal-500 outline-none text-xs text-slate-900" />
                  <button type="submit" className="absolute right-1.5 top-1/2 -translate-y-1/2 p-1 bg-teal-100 text-teal-600 rounded hover:bg-teal-500 hover:text-white transition-colors"><Send className="w-3 h-3" /></button>
                </form>
              </div>
            </div>
          ) : (
            <button onClick={() => setIsChatOpen(true)} className="bg-white hover:bg-slate-50 text-[#2D6A62] p-4 rounded-full shadow-lg hover:scale-105 flex items-center justify-center border border-slate-200 group transition-all">
              <MessageSquare className="w-6 h-6 group-hover:animate-pulse" />
            </button>
          )}
        </div>
      </div>

      {/* RIGHT SIDEBAR: 350px width */}
      <div className="w-[350px] bg-white border-l border-slate-200 flex flex-col z-10 shadow-sm relative overflow-hidden">
        
        {/* Node Selected State */}
        <div className={`absolute inset-0 bg-white z-20 flex flex-col transition-transform duration-500 ease-in-out ${selectedNode ? 'translate-x-0' : 'translate-x-full'}`}>
          {selectedNode && (
            <>
              <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
                <div className="font-bold text-slate-900 truncate pr-4">{selectedNode.data.skill_name}</div>
                <button onClick={() => setSelectedNode(null)} className="p-1.5 hover:bg-slate-200 rounded-lg transition-colors">
                  <X className="w-4 h-4 text-slate-500" />
                </button>
              </div>
              <div className="p-5 flex-1 overflow-y-auto">
                <div className="inline-flex px-2 py-1 bg-blue-100 text-blue-700 border border-blue-200 text-[10px] font-bold uppercase rounded mb-4">
                  {selectedNode.data.status}
                </div>
                
                <h3 className="text-sm font-bold text-slate-900 mb-2">Why you need this</h3>
                <p className="text-xs text-slate-600 leading-relaxed mb-6">
                  This skill is critical for advancing in the RAG pipeline. It builds upon your existing knowledge and bridges the gap to production deployment.
                </p>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">Time</div>
                    <div className="text-sm text-slate-900 font-medium">3.5 Hours</div>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">Difficulty</div>
                    <div className="text-sm text-amber-600 font-medium">Intermediate</div>
                  </div>
                </div>

                <h3 className="text-sm font-bold text-slate-900 mb-3">Recommended Resources</h3>
                <div className="space-y-3">
                  <div className="p-3 bg-white border border-slate-200 shadow-sm rounded-xl hover:border-blue-300 transition-colors cursor-pointer group">
                    <div className="flex gap-3">
                      <div className="mt-0.5"><PlaySquare className="w-4 h-4 text-red-500" /></div>
                      <div>
                        <div className="text-xs font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">Vector Databases Explained</div>
                        <div className="text-[10px] text-slate-500 flex items-center gap-2">YouTube • 2h 15m • Free</div>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 bg-white border border-slate-200 shadow-sm rounded-xl hover:border-blue-300 transition-colors cursor-pointer group">
                    <div className="flex gap-3">
                      <div className="mt-0.5"><BookOpen className="w-4 h-4 text-blue-500" /></div>
                      <div>
                        <div className="text-xs font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition-colors">DeepLearning.ai Course</div>
                        <div className="text-[10px] text-slate-500 flex items-center gap-2">Coursera • 4h • Paid</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Default Dashboard State */}
        <div className="flex flex-col h-full overflow-y-auto">
          {/* Target Card */}
          <div className="p-6 border-b border-slate-100 bg-gradient-to-b from-amber-50 to-white">
            <div className="text-[10px] font-bold tracking-widest text-amber-600 uppercase mb-2">TARGET DESTINATION</div>
            <div className="flex items-start gap-3 mb-4">
              <div className="mt-1"><Target className="w-5 h-5 text-amber-500" /></div>
              <h2 className="text-xl font-bold text-slate-900 leading-tight">Production RAG Engineer</h2>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="text-slate-500">ETA: <span className="text-slate-900 font-semibold">~18 weeks</span></div>
              <div className="text-slate-500">Pace: <span className="text-slate-900 font-semibold">8 hrs/wk</span></div>
            </div>
          </div>

          {/* Readiness Card */}
          <div className="p-6 border-b border-slate-100">
            <div className="flex justify-between items-end mb-4">
              <div className="text-[10px] font-bold tracking-widest text-slate-500 uppercase">OVERALL READINESS</div>
              <div className="text-2xl font-bold text-slate-900">62%</div>
            </div>
            
            <div className="space-y-4">
              {[
                { label: 'Knowledge', val: 81, color: 'bg-emerald-500' },
                { label: 'Practical', val: 68, color: 'bg-blue-500' },
                { label: 'Evaluation', val: 43, color: 'bg-amber-500' },
                { label: 'Deployment', val: 38, color: 'bg-red-500' }
              ].map(stat => (
                <div key={stat.label}>
                  <div className="flex justify-between text-[10px] font-bold text-slate-600 uppercase mb-1.5">
                    <span>{stat.label}</span>
                    <span>{stat.val}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full ${stat.color} rounded-full transition-all duration-1000`} style={{ width: `${stat.val}%` }} />
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-4 text-[11px] text-slate-500 leading-relaxed">
              Your strongest area is <strong className="text-emerald-600">Knowledge</strong>. 
              Deployment is currently your biggest gap.
            </p>
          </div>

          {/* Next Best Action */}
          <div className="p-6">
            <div className="text-[10px] font-bold tracking-widest text-blue-600 uppercase mb-3 flex items-center gap-2">
              <ArrowRight className="w-3 h-3" />
              NEXT UP
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 hover:border-blue-400 transition-colors cursor-pointer shadow-sm" onClick={() => {
              const nextNode = nodes.find(n => n.id === 'n4');
              if(nextNode) setSelectedNode(nextNode);
            }}>
              <div className="font-bold text-blue-900 text-sm mb-1">Vector Databases</div>
              <div className="text-[11px] text-blue-700 mb-3">You have completed the required prerequisites. Ready to begin!</div>
              <div className="flex items-center justify-between text-xs font-semibold">
                <span className="text-blue-600/70">2.5 hours</span>
                <span className="text-blue-700">Continue Learning →</span>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="mt-8 grid grid-cols-2 gap-4">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div className="text-xl font-bold text-slate-900 mb-1">12.5h</div>
                <div className="text-[10px] text-slate-500 font-bold uppercase">Completed</div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div className="text-xl font-bold text-slate-900 mb-1">3/8</div>
                <div className="text-[10px] text-slate-500 font-bold uppercase">Milestones</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

import { useState, useCallback, useMemo, useEffect } from 'react';
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
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [activeRouteMode, setActiveRouteMode] = useState('BALANCED');
  const [loadingGraph, setLoadingGraph] = useState(true);
  const [graphData, setGraphData] = useState(null);
  
  // Dynamic metrics derived from graph
  const completedNodesCount = nodes.filter(n => n.data?.status === 'completed').length;
  const totalNodesCount = Math.max(1, nodes.length - 2); // exclude goal/current
  const baseReadiness = Math.round((completedNodesCount / totalNodesCount) * 100) || 15;
  const knowledgeScore = Math.min(100, baseReadiness + 15);
  const practicalScore = Math.min(100, baseReadiness + 5);
  const evaluationScore = Math.max(5, baseReadiness - 15);
  const deploymentScore = Math.max(5, baseReadiness - 20);
  
  const fastStops = Math.max(1, Math.floor(totalNodesCount * 0.5));
  const balancedStops = totalNodesCount;
  const deepStops = Math.floor(totalNodesCount * 1.5);
  const dynamicRoutes = [
    { id: 'FAST', title: 'FAST TRACK', time: `${Math.round(fastStops * 2.5)} hrs`, stops: fastStops, desc: 'Direct, covers minimum requirements.' },
    { id: 'BALANCED', title: 'BALANCED', time: `${Math.round(balancedStops * 3.5)} hrs`, stops: balancedStops, desc: 'Recommended. Mix of theory and practice.' },
    { id: 'DEEP', title: 'DEEP DIVE', time: `${Math.round(deepStops * 4.5)} hrs`, stops: deepStops, desc: 'Comprehensive. Master every concept.' }
  ];
  
  // Real-time discovery state
  const [loadingResources, setLoadingResources] = useState(false);
  const [sidebarResources, setSidebarResources] = useState([]);

  // Chat Overlay State
  const { messages, setMessages, profile } = useChatContext();
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');

  const nodeTypes = useMemo(() => ({ resource: ResourceNode }), []);

  useEffect(() => {
    const fetchGraph = async () => {
      setLoadingGraph(true);
      try {
        // Use ChatContext profile or fallback
        const payload = {
          user_id: null,
          target_skill_name: profile?.target_goal || "Production RAG Engineer",
          current_skills: profile?.current_skills || ["Python"],
          learner_level: "INTERMEDIATE"
        };
        const res = await fetch('http://127.0.0.1:8000/api/path/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const data = await res.json();
          // If backend couldn't generate a rich DAG (e.g., only 1 node returned for GenAI), fallback to mock graph for presentation
          if (!data.nodes || data.nodes.length <= 1) {
            setNodes(initialNodes);
            setEdges(initialEdges);
          } else {
            setNodes(data.nodes);
            setEdges(data.edges);
            setGraphData(data);
          }
        } else {
          // Fallback to mock data on failure
          setNodes(initialNodes);
          setEdges(initialEdges);
        }
      } catch (err) {
        setNodes(initialNodes);
        setEdges(initialEdges);
      } finally {
        setLoadingGraph(false);
      }
    };
    fetchGraph();
  }, [profile]);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
  
  const onNodeClick = useCallback(async (event, node) => {
    if (node.data.status === 'current') return;
    setSelectedNode(node);
    
    // Check if we need to fetch resources
    if (!node.data.skill_id) {
        // Fallback mock logic
        setSidebarResources([]);
        return;
    }
    
    setLoadingResources(true);
    setSidebarResources([]);
    
    try {
        const payload = {
            skill_id: node.data.skill_id,
            learner_level: "INTERMEDIATE",
            goal: profile?.target_goal || "Production RAG Engineer",
            constraints: { budget: profile?.budget || "FREE" }
        };
        const res = await fetch('http://127.0.0.1:8000/api/resources/youtube/discover', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (res.ok) {
            const data = await res.json();
            setSidebarResources(data.resources || []);
        }
    } catch (err) {
        console.error("Discovery failed", err);
    } finally {
        setLoadingResources(false);
    }
  }, [profile]);

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
            {dynamicRoutes.map((route, idx) => (
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
              SkillRoute selected this path based on your current knowledge of {profile?.current_skills?.slice(0, 2).join(" and ") || "foundational concepts"}. It efficiently bridges the gap to your target goal.
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
            <p className="text-sm text-slate-600 font-medium">Your personalized route to {profile?.target_goal || "Production RAG Engineer"}</p>
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

        {loadingGraph && (
          <div className="absolute inset-0 z-40 bg-slate-50/80 backdrop-blur-sm flex flex-col items-center justify-center">
            <Loader2 className="w-10 h-10 text-teal-500 animate-spin mb-4" />
            <div className="text-sm font-bold text-slate-700 tracking-wider">GENERATING PERSONALIZED GRAPH</div>
            <div className="text-xs text-slate-500 mt-2">Analyzing your profile and prerequisites...</div>
          </div>
        )}

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
                  {selectedNode.data.status === 'goal' ? `Mastering ${selectedNode.data.skill_name} is your ultimate learning destination.` : `Learning ${selectedNode.data.skill_name} is a crucial stepping stone. It provides the required knowledge to unlock advanced concepts in your ${profile?.target_goal || 'learning'} journey.`}
                </p>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">Est. Time</div>
                    <div className="text-sm text-slate-900 font-medium">
                      {sidebarResources.length > 0 
                        ? `${Math.max(1, Math.round(sidebarResources.reduce((acc, r) => acc + (r.duration || 0), 0) / 3600 * 10) / 10)} Hours` 
                        : 'Auto-calculated'}
                    </div>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">Difficulty</div>
                    <div className="text-sm text-amber-600 font-medium">{profile?.learner_level || 'Adaptive'}</div>
                  </div>
                </div>

                <h3 className="text-sm font-bold text-slate-900 mb-3">Recommended Resources</h3>
                
                {loadingResources ? (
                  <div className="flex flex-col items-center justify-center p-6 space-y-3">
                    <Loader2 className="w-6 h-6 text-teal-500 animate-spin" />
                    <div className="text-xs text-slate-500 font-medium animate-pulse">Loading verified recommendations...</div>
                  </div>
                ) : sidebarResources.length > 0 ? (
                  <div className="space-y-4">
                    {sidebarResources.map((res, i) => (
                      <div key={i} className="p-3 bg-white border border-slate-200 shadow-sm rounded-xl hover:border-blue-300 transition-colors group">
                        <div className="flex gap-3 mb-2">
                          <div className="w-24 h-16 rounded overflow-hidden flex-shrink-0 bg-slate-100">
                            {res.thumbnail ? (
                              <img src={res.thumbnail} alt={res.title} className="w-full h-full object-cover" />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center"><PlaySquare className="w-6 h-6 text-slate-400" /></div>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-bold text-slate-900 leading-tight mb-1 line-clamp-2" title={res.title}>{res.title}</div>
                            <div className="text-[10px] text-slate-500 flex items-center gap-1.5 flex-wrap">
                              <span className="font-semibold text-slate-700">{res.channel || 'YouTube'}</span>
                              <span>•</span>
                              <span>{Math.round(res.duration / 60)} min</span>
                              <span>•</span>
                              <span className="text-emerald-600 font-bold">{res.cost_type}</span>
                            </div>
                          </div>
                        </div>
                        
                        {res.why_recommended && (
                          <div className="mt-3 p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                            <div className="text-[10px] font-bold text-slate-500 uppercase mb-1">Why Recommended</div>
                            <div className="space-y-1">
                              <div className="flex items-center gap-1.5 text-[11px] text-slate-600">
                                <CheckCircle className="w-3 h-3 text-emerald-500" /> Matches: {res.why_recommended.skill_match}
                              </div>
                              <div className="flex items-center gap-1.5 text-[11px] text-slate-600">
                                <CheckCircle className="w-3 h-3 text-emerald-500" /> Relevance: {res.why_recommended.semantic_score}
                              </div>
                              {res.verified && (
                                <div className="flex items-center gap-1.5 text-[11px] text-slate-600">
                                  <CheckCircle className="w-3 h-3 text-emerald-500" /> Verified URL
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                        
                        <a href={res.url} target="_blank" rel="noreferrer" className="mt-3 w-full py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition-colors">
                          <PlaySquare className="w-3.5 h-3.5" /> Watch Now
                        </a>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 bg-slate-50 border border-slate-200 border-dashed rounded-xl text-center">
                    <div className="text-xs text-slate-500">No verified resources available right now.</div>
                  </div>
                )}
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
              <h2 className="text-xl font-bold text-slate-900 leading-tight">{profile?.target_goal || graphData?.target?.name || "Production RAG Engineer"}</h2>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="text-slate-500">Timeline: <span className="text-slate-900 font-semibold">{profile?.deadline || "~18 weeks"}</span></div>
              <div className="text-slate-500">Pace: <span className="text-slate-900 font-semibold">{profile?.time_commitment || "8 hrs/wk"}</span></div>
            </div>
          </div>

          {/* Readiness Card */}
          <div className="p-6 border-b border-slate-100">
            <div className="flex justify-between items-end mb-4">
              <div className="text-[10px] font-bold tracking-widest text-slate-500 uppercase">OVERALL READINESS</div>
              <div className="text-2xl font-bold text-slate-900">{baseReadiness}%</div>
            </div>
            
            <div className="space-y-4">
              {[
                { label: 'Knowledge', val: knowledgeScore, color: 'bg-emerald-500' },
                { label: 'Practical', val: practicalScore, color: 'bg-blue-500' },
                { label: 'Evaluation', val: evaluationScore, color: 'bg-amber-500' },
                { label: 'Deployment', val: deploymentScore, color: 'bg-red-500' }
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
              
            <div className="text-[10px] text-slate-400 leading-relaxed font-medium mt-4">
              Your strongest area is <span className="font-bold text-emerald-600">Knowledge</span>. Deployment is currently your biggest gap based on your current skills.
            </div>
          </div>

          {/* Next Best Action */}
          <div className="p-6">
            <div className="text-[10px] font-bold tracking-widest text-blue-600 uppercase mb-3 flex items-center gap-2">
              <ArrowRight className="w-3 h-3" />
              NEXT UP
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 hover:border-blue-400 transition-colors cursor-pointer shadow-sm" onClick={() => {
              const nextNode = nodes.find(n => n.data?.status === 'current' || n.data?.status === 'next') || nodes[1] || nodes[0];
              if(nextNode) setSelectedNode(nextNode);
            }}>
              <div className="font-bold text-slate-900 text-sm mb-1">{nodes.find(n => n.data?.status === 'current' || n.data?.status === 'next')?.data?.skill_name || "Next Milestone"}</div>
              <p className="text-xs text-blue-700 leading-relaxed mb-4">
                You have completed the required prerequisites. Ready to begin!
              </p>
              <div className="flex items-center justify-between mt-auto">
                <span className="text-[10px] font-bold text-slate-500 uppercase">Adaptive</span>
                <span className="text-blue-700">Continue Learning →</span>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="mt-8 grid grid-cols-2 gap-4">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div className="text-xl font-bold text-slate-900 mb-1">{completedNodesCount * 3.5}h</div>
                <div className="text-[10px] text-slate-500 font-bold uppercase">Completed</div>
              </div>
              <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 flex flex-col items-center justify-center text-center">
                <div className="text-2xl font-black text-slate-900">{completedNodesCount}/{totalNodesCount}</div>
                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Milestones</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

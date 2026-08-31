import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
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
  ArrowRight, AlertCircle, LayoutDashboard, Clock, Layers, TrendingUp, UserRound
} from 'lucide-react';
import { useChatContext } from '../context/ChatContext';
import RouteNav from '../components/RouteNav';

import { API_URL } from '../config';

// --- CUSTOM NODES ---

const ResourceNode = ({ data, selected }: { data: any, selected: any }) => {
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
      {data.route_note && (
        <div className="mb-3 rounded-md bg-slate-100 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          {data.route_note}
        </div>
      )}
      
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

const goalOptions = [
  {
    value: 'Production RAG Engineer',
    label: 'Production RAG Engineer',
    timeline: '~18 weeks',
    pace: '8 hrs/wk',
    skills: {
      n4: 'Vector Databases (Pinecone)',
      n5: 'Embeddings & Transformers',
      n6: 'Vector Search Algorithms',
      n7: 'RAG Pipeline Architecture',
      n8: 'Docker & Kubernetes',
      n9: 'Evaluation Metrics',
      n10: 'Advanced Agents',
      n11: 'Prompt Design Patterns',
      n12: 'Observability & Tracing',
      n13: 'Portfolio RAG App',
    },
  },
  {
    value: 'Frontend Engineer',
    label: 'Frontend Engineer',
    timeline: '~14 weeks',
    pace: '6 hrs/wk',
    skills: {
      n4: 'React State Management',
      n5: 'Responsive UI Systems',
      n6: 'TypeScript Patterns',
      n7: 'Frontend Architecture',
      n8: 'Testing & Accessibility',
      n9: 'Performance Optimization',
      n10: 'Design System Delivery',
      n11: 'Component API Design',
      n12: 'Monitoring Web Vitals',
      n13: 'Portfolio Frontend App',
    },
  },
  {
    value: 'Data Analyst',
    label: 'Data Analyst',
    timeline: '~12 weeks',
    pace: '5 hrs/wk',
    skills: {
      n4: 'SQL Joins & Aggregations',
      n5: 'Dashboard Storytelling',
      n6: 'Exploratory Analysis',
      n7: 'Business Metrics Design',
      n8: 'Spreadsheet Automation',
      n9: 'Statistics for Decisions',
      n10: 'Executive Reporting',
      n11: 'Data Cleaning Patterns',
      n12: 'Data Quality Checks',
      n13: 'Analytics Portfolio Case Study',
    },
  },
  {
    value: 'Cloud DevOps Engineer',
    label: 'Cloud DevOps Engineer',
    timeline: '~20 weeks',
    pace: '8 hrs/wk',
    skills: {
      n4: 'CI/CD Pipelines',
      n5: 'Linux & Networking',
      n6: 'Infrastructure as Code',
      n7: 'Cloud Architecture',
      n8: 'Kubernetes Operations',
      n9: 'Monitoring & Incident Response',
      n10: 'Security Hardening',
      n11: 'Release Automation',
      n12: 'Cost & Reliability Reviews',
      n13: 'Production Deployment Project',
    },
  },
];

const getGoalOption = (targetGoal: string) => (
  goalOptions.find(goal => goal.value === targetGoal) || goalOptions[0]
);

const routeModeDetails = {
  FAST: {
    title: 'FAST TRACK',
    desc: 'Shortest practical sequence. Skips parallel theory branches and keeps only the must-learn chain.',
    sidebarReason: 'Fast Track keeps the shortest useful chain from your current position to the target. It hides optional branches so you can focus on the next few decisions.',
    speed: 2.5,
  },
  BALANCED: {
    title: 'BALANCED',
    desc: 'Recommended path. Keeps core theory, practice, and the most useful specialization branch.',
    sidebarReason: 'Balanced keeps the main route plus enough context to understand why each skill matters. This is the best default for steady progress.',
    speed: 3.5,
  },
  DEEP: {
    title: 'DEEP DIVE',
    desc: 'Expanded mastery route. Adds optional branches, validation skills, and portfolio work.',
    sidebarReason: 'Deep Dive shows the broadest route, including support skills and optional mastery checkpoints. Use it when you want stronger long-term coverage.',
    speed: 4.5,
  },
};

const routeNodeIds = {
  FAST: ['current', 'n5', 'n6', 'n7', 'n9', 'goal'],
  BALANCED: ['current', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n9', 'goal'],
  DEEP: ['current', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8', 'n9', 'n10', 'goal', 'n11', 'n12', 'n13'],
};

const routeLayouts = {
  FAST: {
    goal: { x: 420, y: -140 },
    n9: { x: 420, y: 60 },
    n7: { x: 420, y: 230 },
    n6: { x: 420, y: 400 },
    n5: { x: 420, y: 570 },
    current: { x: 420, y: 710 },
  },
  BALANCED: {
    goal: { x: 420, y: -140 },
    n9: { x: 420, y: 70 },
    n7: { x: 420, y: 250 },
    n6: { x: 420, y: 430 },
    n4: { x: 170, y: 610 },
    n5: { x: 670, y: 610 },
    current: { x: 660, y: 760 },
    n3: { x: 420, y: 800 },
    n1: { x: 170, y: 980 },
    n2: { x: 670, y: 980 },
  },
  DEEP: {
    goal: { x: 500, y: -160 },
    n8: { x: 110, y: 60 },
    n9: { x: 500, y: 60 },
    n10: { x: 890, y: 60 },
    n7: { x: 500, y: 250 },
    n11: { x: 170, y: 260 },
    n12: { x: 830, y: 260 },
    n6: { x: 500, y: 440 },
    n4: { x: 240, y: 640 },
    n5: { x: 760, y: 640 },
    n13: { x: 500, y: 790 },
    current: { x: 760, y: 820 },
    n3: { x: 500, y: 940 },
    n1: { x: 240, y: 1120 },
    n2: { x: 760, y: 1120 },
  },
};

const deepDiveNodes = [
  { id: 'n11', type: 'resource', position: { x: 170, y: 260 }, data: { status: 'locked', skill_name: 'Prompt Design Patterns', resources: [{ type: 'article' }], route_note: 'Optional mastery' } },
  { id: 'n12', type: 'resource', position: { x: 830, y: 260 }, data: { status: 'locked', skill_name: 'Observability & Tracing', resources: [{ type: 'project' }], route_note: 'Production skill' } },
  { id: 'n13', type: 'resource', position: { x: 500, y: 790 }, data: { status: 'next', skill_name: 'Portfolio RAG App', resources: [{ type: 'project' }, { type: 'video' }], route_note: 'Proof project' } },
];

const deepDiveEdges = [
  createEdge('n6', 'n11', 'Explore'),
  createEdge('n11', 'n7', 'Improves'),
  createEdge('n7', 'n12', 'Production'),
  createEdge('n12', 'goal', 'Supports'),
  createEdge('n3', 'n13', 'Build'),
  createEdge('n13', 'n6', 'Applies', true),
];

const createSequentialEdges = (visibleNodes: any[], mode: string) => {
  const ordered = visibleNodes
    .filter(node => node.id !== 'current')
    .sort((a, b) => b.position.y - a.position.y);

  return ordered.slice(0, -1).map((node, index) => {
    const next = ordered[index + 1];
    return createEdge(node.id, next.id, mode === 'FAST' ? 'Fast step' : 'Next step', true);
  });
};

const getFallbackNodeIds = (mode: string, sourceNodes: any[]) => {
  const goalIds = sourceNodes.filter(n => n.data?.status === 'goal').map(n => n.id);
  const currentIds = sourceNodes.filter(n => n.data?.status === 'current').map(n => n.id);
  const completedIds = sourceNodes.filter(n => n.data?.status === 'completed').map(n => n.id);
  const activeIds = sourceNodes.filter(n => ['next', 'in-progress'].includes(n.data?.status)).map(n => n.id);
  const lockedIds = sourceNodes.filter(n => n.data?.status === 'locked').map(n => n.id);

  if (mode === 'FAST') {
    return [...goalIds, ...currentIds, ...completedIds.slice(-1), ...activeIds.slice(0, 1), ...lockedIds.slice(0, 3)];
  }

  if (mode === 'BALANCED') {
    return [...goalIds, ...currentIds, ...completedIds, ...activeIds, ...lockedIds.slice(0, 4)];
  }

  return sourceNodes.map(n => n.id);
};

const buildRouteGraph = (mode: string, sourceNodes: any[], sourceEdges: any[], targetGoal = goalOptions[0].value): { nodes: any[]; edges: any[] } => {
  const goalOption = getGoalOption(targetGoal);
  const sourceById = new Map<string, any>(sourceNodes.map(node => [node.id, node]));
  const usesDemoGraph = routeNodeIds.BALANCED.every(id => sourceById.has(id));
  const baseNodes = mode === 'DEEP' && usesDemoGraph ? [...sourceNodes, ...deepDiveNodes] : sourceNodes;
  const availableById = new Map<string, any>(baseNodes.map(node => [node.id, node]));
  const wantedIds = usesDemoGraph ? routeNodeIds[mode] : getFallbackNodeIds(mode, baseNodes);
  const visibleIdSet = new Set<string>(wantedIds.filter(id => availableById.has(id)));
  const layout = routeLayouts[mode] || routeLayouts.BALANCED;

  const visibleNodes = Array.from(visibleIdSet).map((id, index) => {
    const node = availableById.get(id);
    const explicitPosition = layout[id];
    const position = explicitPosition || {
      x: 240 + (index % 3) * 280,
      y: Math.floor(index / 3) * 180,
    };

    return {
      ...node,
      position,
      data: {
        ...node.data,
        skill_name: node.data?.status === 'goal'
          ? targetGoal
          : goalOption.skills[id] || node.data?.skill_name,
        route_note: node.data?.route_note || (mode === 'FAST' ? 'Core path' : mode === 'BALANCED' ? 'Recommended' : 'Deep detail'),
      },
    };
  });

  const sourceEdgePool = mode === 'DEEP' && usesDemoGraph ? [...sourceEdges, ...deepDiveEdges] : sourceEdges;
  let visibleEdges = sourceEdgePool
    .filter(edge => visibleIdSet.has(edge.source) && visibleIdSet.has(edge.target))
    .map(edge => ({
      ...edge,
      animated: mode === 'FAST' || edge.animated,
      style: mode === 'FAST' || edge.animated ? activeEdgeStyle : defaultEdgeStyle,
      markerEnd: { type: MarkerType.ArrowClosed, color: mode === 'FAST' || edge.animated ? '#0284c7' : '#94a3b8' },
    }));

  if (visibleEdges.length === 0 && visibleNodes.length > 1) {
    visibleEdges = createSequentialEdges(visibleNodes, mode);
  }

  return { nodes: visibleNodes, edges: visibleEdges };
};

export default function InteractiveMap() {
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [nodeExplanation, setNodeExplanation] = useState<string | null>(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [activeRouteMode, setActiveRouteMode] = useState('BALANCED');
  const [activeView, setActiveView] = useState<'dashboard' | 'map'>('dashboard');
  const [loadingGraph, setLoadingGraph] = useState(true);
  const [graphData, setGraphData] = useState<any>(null);
  const [graphHistory, setGraphHistory] = useState<any[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const historyIndexRef = useRef(-1);

  // Real-time discovery state
  const [loadingResources, setLoadingResources] = useState(false);
  const [sidebarResources, setSidebarResources] = useState<any[]>([]);
  const [youtubeStatus, setYoutubeStatus] = useState<string | null>(null);
  const [strugglingSkills, setStrugglingSkills] = useState<number[]>([]);

  // Chat Overlay and Progress State
  const { messages, setMessages, profile, setProfile, completedSkills, markComplete, markIncomplete, chats, currentChatId, setCurrentChatId } = useChatContext();
  const [isChatOpen, setIsChatOpen] = useState(false);
  const latestSkillIdRef = useRef<number | null>(null);
  const [chatInput, setChatInput] = useState('');

  const nodeTypes = useMemo(() => ({ resource: ResourceNode }), []);
  const targetGoal = profile?.target_goal || graphData?.target?.name || goalOptions[0].value;
  const selectedGoal = getGoalOption(targetGoal);
  const routeGraph = useMemo(() => buildRouteGraph(activeRouteMode, nodes, edges, targetGoal), [activeRouteMode, nodes, edges, targetGoal]);
  const displayedNodes = routeGraph.nodes;
  const displayedEdges = routeGraph.edges;

  // Dynamic metrics derived from selected route
  const completedNodesCount = displayedNodes.filter(n => n.data?.status === 'completed').length;
  const totalNodesCount = Math.max(1, displayedNodes.filter(n => !['goal', 'current'].includes(n.data?.status)).length);
  const baseReadiness = Math.round((completedNodesCount / totalNodesCount) * 100) || 15;
  const knowledgeScore = Math.min(100, baseReadiness + (activeRouteMode === 'DEEP' ? 10 : 15));
  const practicalScore = Math.min(100, baseReadiness + (activeRouteMode === 'FAST' ? 15 : 5));
  const evaluationScore = Math.max(5, baseReadiness - (activeRouteMode === 'DEEP' ? 5 : 15));
  const deploymentScore = Math.max(5, baseReadiness - (activeRouteMode === 'DEEP' ? 10 : 20));
  const dynamicRoutes = Object.entries(routeModeDetails).map(([id, details]) => {
    const routeNodes = buildRouteGraph(id, nodes.length ? nodes : initialNodes, edges.length ? edges : initialEdges, targetGoal).nodes;
    const stops = Math.max(1, routeNodes.filter(n => !['goal', 'current'].includes(n.data?.status)).length);
    return {
      id,
      title: details.title,
      time: `${Math.round(stops * details.speed)} hrs`,
      stops,
      desc: details.desc,
    };
  });

  const fetchGraph = useCallback(async (isHistoryNavigation = false) => {
    setLoadingGraph(true);
    try {
      const token = localStorage.getItem('token') || '';
      const payload = {
        user_id: null,
        target_skill_name: profile?.target_goal || "Production RAG Engineer",
        current_skills: profile?.current_skills || ["Python"],
        completed_skill_ids: completedSkills,
        learner_level: "INTERMEDIATE"
      };
      const res = await fetch(`${API_URL}/api/path/generate`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        if (!data.nodes || data.nodes.length <= 1) {
          setNodes(initialNodes);
          setEdges(initialEdges);
        } else {
          setNodes(data.nodes);
          setEdges(data.edges);
          setGraphData(data);
          
          if (!isHistoryNavigation) {
             setGraphHistory(prev => {
                 const currentIdx = historyIndexRef.current;
                 const newHistory = [...prev.slice(0, currentIdx + 1), { nodes: data.nodes, edges: data.edges, data }];
                 if (newHistory.length > 20) newHistory.shift();
                 return newHistory;
             });
             setHistoryIndex(prev => {
                 const next = prev >= 19 ? 19 : prev + 1;
                 historyIndexRef.current = next;
                 return next;
             });
          }
        }
      } else {
        setNodes(initialNodes);
        setEdges(initialEdges);
      }
    } catch (err) {
      setNodes(initialNodes);
      setEdges(initialEdges);
    } finally {
      setLoadingGraph(false);
    }
  }, [profile, completedSkills]);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  useEffect(() => {
    if (selectedNode && !displayedNodes.some(node => node.id === selectedNode.id)) {
      setSelectedNode(null);
    }
  }, [displayedNodes, selectedNode]);

  const navigateHistory = (direction: any) => {
    const newIndex = historyIndex + direction;
    if (newIndex >= 0 && newIndex < graphHistory.length) {
        setHistoryIndex(newIndex);
        historyIndexRef.current = newIndex;
        const state = graphHistory[newIndex];
        setNodes(state.nodes);
        setEdges(state.edges);
        setGraphData(state.data);
    }
  };

  const onNodesChange = useCallback((changes: any) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes: any) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
  
  const [recommendations, setRecommendations] = useState<any>(null);

  const fetchResourcesForSkill = async (skillId: number, isStruggling: boolean) => {
    setLoadingResources(true);
    setSidebarResources([]);
    setYoutubeStatus(null);
    setRecommendations(null);
    try {
        const payload = {
            skill_id: skillId,
            learner_level: "INTERMEDIATE",
            goal: profile?.target_goal || "Production RAG Engineer",
            constraints: { budget: profile?.budget || "FREE" },
            is_struggling: isStruggling
        };

        const recPayload = {
            skill_id: skillId,
            learner_level: "INTERMEDIATE",
            goal: profile?.target_goal || "Production RAG Engineer",
            budget: profile?.budget || "FREE"
        };

        const [ytRes, recRes] = await Promise.all([
          fetch(`${API_URL}/api/resources/youtube/discover`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
          }),
          fetch(`${API_URL}/api/resources/recommendations`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(recPayload)
          })
        ]);
        
        if (latestSkillIdRef.current !== skillId) return;

        let fetchedYt = [];
        let fetchedRecs = null;

                if (ytRes.ok) {
            if (latestSkillIdRef.current !== skillId) return;
            const data = await ytRes.json();
            fetchedYt = data.resources || [];
            setYoutubeStatus(data.status || null);
        }
        
                if (recRes.ok) {
            if (latestSkillIdRef.current !== skillId) return;
            fetchedRecs = await recRes.json();
            setRecommendations(fetchedRecs);
            
            if (fetchedRecs?.project?.tutorial_search_intent) {
               const projectPayload = {
                  ...payload,
                  constraints: { ...payload.constraints, search_intent: fetchedRecs.project.tutorial_search_intent }
               };
               fetch(`${API_URL}/api/resources/youtube/discover`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(projectPayload)
               }).then(res => res.json()).then(data => {
                  if(data.resources) {
                     setSidebarResources(prev => [...prev, ...data.resources.map(r => ({...r, _is_project_tutorial: true}))]);
                  }
               }).catch(e => console.error("Project tutorial fetch failed", e));
            }
        }
        setSidebarResources(fetchedYt);
    } catch (err) {
        console.error("Discovery failed", err);
    } finally {
        setLoadingResources(false);
    }
  };

  const onNodeClick = useCallback(async (event: any, node: any) => {
    if (node.data.status === 'locked') return; 
    setSelectedNode(node);
    latestSkillIdRef.current = node.data.skill_id;
    
    if (!node.data.skill_id) {
        setSidebarResources([]);
        setRecommendations(null);
        setNodeExplanation(null);
        return;
    }
    
    setLoadingExplanation(true);
    setNodeExplanation(null);
    
    fetch(`${API_URL}/api/path/explain_node`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            skill_id: node.data.skill_id,
            target_goal: profile?.target_goal || "Production RAG Engineer"
        })
    })
    .then(res => res.json())
    .then(data => {
        setNodeExplanation(data.explanation);
    })
    .catch(() => {
        setNodeExplanation("This skill is part of your learning path toward the selected goal.");
    })
    .finally(() => {
        setLoadingExplanation(false);
    });
    
    // Check if skill is struggling from state
    // We capture state using the current value in dependency array.
    // However, onNodeClick is memoized, so we rely on the skill ID to fetch.
    // Instead of doing it here directly using outdated state, let's just use the helper.
    fetchResourcesForSkill(node.data.skill_id, strugglingSkills.includes(node.data.skill_id));
  }, [profile, strugglingSkills]);

  const handleChatSubmit = async (e: any) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatInput('');
    
    try {
      const token = localStorage.getItem("token") || "";
      const payload = {
        message: userMsg,
        target_goal: profile?.target_goal || "Production RAG Engineer",
        budget: profile?.budget || "FREE",
        time_commitment: profile?.time_commitment || "10 hours per week"
      };
      
      const res = await fetch(`${API_URL}/api/chat/coach`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { role: 'ai', content: data.reply }]);
        
        // Handle Map regeneration locally or trigger backend re-fetch
        if (data.requires_regeneration) {
            fetchGraph();
        }
      } else {
        setMessages(prev => [...prev, { role: 'ai', content: "Sorry, I encountered an error communicating with the server." }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: "Network error." }]);
    }
  };

  const handleRouteSelect = (mode: any) => {
    setActiveRouteMode(mode);
  };

  const handleGoalChange = (goalValue: string) => {
    const nextGoal = getGoalOption(goalValue);
    setSelectedNode(null);
    setActiveRouteMode('BALANCED');
    const matchingProfile = chats.find((chat: any) => chat.profile?.target_goal === goalValue);
    if (matchingProfile) {
      setCurrentChatId(matchingProfile.id);
      return;
    }

    setProfile({
      ...(profile || {}),
      target_goal: nextGoal.value,
      deadline: nextGoal.timeline,
      time_commitment: nextGoal.pace,
      current_skills: profile?.current_skills || ['Python'],
      budget: profile?.budget || 'FREE',
    });
  };

  const activeRouteDetails = routeModeDetails[activeRouteMode] || routeModeDetails.BALANCED;
  const currentNode = displayedNodes.find(n => n.data?.status === 'current');
  const nextNode = displayedNodes.find(n => n.data?.status === 'next') || displayedNodes.find(n => n.data?.status === 'in-progress') || displayedNodes[1] || displayedNodes[0];
  const dashboardProfiles = (chats || []).map((chat: any) => ({
    id: chat.id,
    label: chat.profile?.target_goal || chat.title || 'Untitled Profile',
    skills: chat.profile?.current_skills || [],
    completedCount: chat.completedSkills?.length || 0,
  }));
  const readinessStats = [
    { label: 'Knowledge', val: knowledgeScore, color: 'bg-emerald-500', stroke: '#10b981' },
    { label: 'Practical', val: practicalScore, color: 'bg-blue-500', stroke: '#3b82f6' },
    { label: 'Evaluation', val: evaluationScore, color: 'bg-amber-500', stroke: '#f59e0b' },
    { label: 'Deployment', val: deploymentScore, color: 'bg-red-500', stroke: '#ef4444' }
  ];
  const readinessTotal = readinessStats.reduce((sum, stat) => sum + stat.val, 0) || 1;
  const pieSegments = readinessStats.reduce((segments, stat) => {
    const previousOffset = segments.reduce((sum, segment) => sum + segment.percent, 0);
    const percent = (stat.val / readinessTotal) * 100;
    return [...segments, { ...stat, percent, offset: previousOffset }];
  }, [] as Array<typeof readinessStats[number] & { percent: number; offset: number }>);
  const completedHours = completedNodesCount * 3.5;
  const remainingStops = Math.max(0, totalNodesCount - completedNodesCount);

  const renderDashboardContent = (isStandalone = false) => (
    <div className={`${isStandalone ? 'h-full overflow-y-auto px-8 py-7' : 'flex flex-col h-full overflow-y-auto'}`}>
      {isStandalone && (
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-[11px] font-bold tracking-widest text-teal-700 uppercase mb-2">Learning Dashboard</div>
            <h2 className="text-3xl font-black text-slate-950 tracking-tight">Your progress workspace</h2>
            <p className="mt-2 text-sm text-slate-600">Readiness, context, and the next action for {targetGoal}.</p>
          </div>
          <button
            onClick={() => setActiveView('map')}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-slate-700 shadow-sm transition-all hover:border-teal-300 hover:text-teal-700 hover:shadow-md"
          >
            <MapIcon className="h-4 w-4" />
            Open Map
          </button>
        </div>
      )}

      {isStandalone && (
        <div className="mb-5 grid grid-cols-1 gap-3 lg:grid-cols-4">
          {[
            { label: 'Readiness', value: `${baseReadiness}%`, hint: 'Overall score', icon: TrendingUp, tone: 'text-emerald-600 bg-emerald-50 border-emerald-100' },
            { label: 'Completed', value: `${completedHours}h`, hint: 'Logged effort', icon: Clock, tone: 'text-blue-600 bg-blue-50 border-blue-100' },
            { label: 'Remaining', value: remainingStops, hint: 'Learning stops', icon: Layers, tone: 'text-amber-600 bg-amber-50 border-amber-100' },
            { label: 'Route', value: activeRouteDetails.title, hint: `${totalNodesCount} stops`, icon: Compass, tone: 'text-teal-600 bg-teal-50 border-teal-100' },
          ].map(({ label, value, hint, icon: Icon, tone }) => (
            <div key={label} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">{label}</div>
                <div className={`rounded-lg border p-2 ${tone}`}>
                  <Icon className="h-4 w-4" />
                </div>
              </div>
              <div className="truncate text-2xl font-black text-slate-950">{value}</div>
              <div className="mt-1 text-xs font-medium text-slate-500">{hint}</div>
            </div>
          ))}
        </div>
      )}

      <div className={isStandalone ? 'grid grid-cols-1 gap-5 xl:grid-cols-[1.05fr_0.95fr]' : ''}>
        <div className={isStandalone ? 'space-y-5' : ''}>
          {/* Target Card */}
          <div className={`${isStandalone ? 'rounded-lg border border-amber-100 bg-gradient-to-b from-amber-50 to-white shadow-sm' : 'border-b border-slate-100 bg-gradient-to-b from-amber-50 to-white'} p-6`}>
            <div className="text-[10px] font-bold tracking-widest text-amber-600 uppercase mb-2">TARGET DESTINATION</div>
            <div className="flex items-start gap-3 mb-4">
              <div className="mt-1"><Target className="w-5 h-5 text-amber-500" /></div>
              <div className="min-w-0 flex-1">
                <h2 className="text-xl font-bold text-slate-900 leading-tight">{targetGoal}</h2>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="text-slate-500">Timeline: <span className="text-slate-900 font-semibold">{profile?.deadline || selectedGoal.timeline}</span></div>
              <div className="text-slate-500">Pace: <span className="text-slate-900 font-semibold">{profile?.time_commitment || selectedGoal.pace}</span></div>
            </div>
          </div>

          {/* Readiness Card */}
          <div className={`${isStandalone ? 'rounded-lg border border-slate-200 bg-white shadow-sm' : 'border-b border-slate-100'} p-6`}>
            <div className="flex justify-between items-end mb-4">
              <div className="text-[10px] font-bold tracking-widest text-slate-500 uppercase">OVERALL READINESS</div>
              <div className="text-2xl font-bold text-slate-900">{baseReadiness}%</div>
            </div>

            <div className={isStandalone ? 'grid gap-6 md:grid-cols-[220px_1fr]' : ''}>
              {isStandalone && (
                <div className="flex flex-col items-center justify-center rounded-lg bg-slate-50 p-4">
                  <div className="relative h-44 w-44">
                    <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90">
                      <circle cx="60" cy="60" r="44" fill="none" stroke="#e2e8f0" strokeWidth="16" />
                      {pieSegments.map(segment => (
                        <circle
                          key={segment.label}
                          cx="60"
                          cy="60"
                          r="44"
                          fill="none"
                          stroke={segment.stroke}
                          strokeWidth="16"
                          strokeLinecap="round"
                          pathLength="100"
                          strokeDasharray={`${segment.percent} ${100 - segment.percent}`}
                          strokeDashoffset={-segment.offset}
                        />
                      ))}
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                      <div className="text-3xl font-black text-slate-950">{baseReadiness}%</div>
                      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Ready</div>
                    </div>
                  </div>
                  <div className="mt-4 grid w-full grid-cols-2 gap-2">
                    {readinessStats.map(stat => (
                      <div key={stat.label} className="flex items-center gap-2 text-[10px] font-bold text-slate-600">
                        <span className={`h-2 w-2 rounded-full ${stat.color}`} />
                        {stat.label}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-4">
                {readinessStats.map(stat => (
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
            </div>
              
            <div className="text-[10px] text-slate-400 leading-relaxed font-medium mt-4">
              Your strongest area is <span className="font-bold text-emerald-600">Knowledge</span>. Deployment is currently your biggest gap based on your current skills.
            </div>
          </div>
        </div>

        <div className={isStandalone ? 'space-y-5' : 'p-6'}>
          {isStandalone && (
            <>
              <div className="rounded-lg border border-teal-100 bg-teal-50 p-5 shadow-sm">
                <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-teal-700">
                  <Activity className="h-3.5 w-3.5" />
                  Current Context
                </div>
                <div className="text-sm font-bold text-slate-900">{currentNode?.data?.skill_name || 'You are here'}</div>
                <p className="mt-2 text-xs leading-relaxed text-slate-600">{activeRouteDetails.sidebarReason}</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                <div className="mb-4 flex items-center justify-between">
                  <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Route Health</div>
                  <div className="rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-black text-emerald-700">ON TRACK</div>
                </div>
                <div className="space-y-3">
                  {[
                    { label: 'Core concepts', value: Math.min(100, knowledgeScore + 4), color: 'bg-emerald-500' },
                    { label: 'Hands-on proof', value: practicalScore, color: 'bg-blue-500' },
                    { label: 'Production polish', value: deploymentScore, color: 'bg-red-500' },
                  ].map(item => (
                    <div key={item.label}>
                      <div className="mb-1 flex items-center justify-between text-xs font-bold text-slate-600">
                        <span>{item.label}</span>
                        <span>{item.value}%</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                        <div className={`h-full rounded-full ${item.color}`} style={{ width: `${item.value}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Next Best Action */}
          <div>
            <div className="text-[10px] font-bold tracking-widest text-blue-600 uppercase mb-3 flex items-center gap-2">
              <ArrowRight className="w-3 h-3" />
              NEXT UP
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 hover:border-blue-400 transition-colors cursor-pointer shadow-sm" onClick={() => {
              if (isStandalone) setActiveView('map');
              if (nextNode) setSelectedNode(nextNode);
            }}>
              <div className="font-bold text-slate-900 text-sm mb-1">{nextNode?.data?.skill_name || "Next Milestone"}</div>
              <p className="text-xs text-blue-700 leading-relaxed mb-4">
                This is the best next action for the {activeRouteDetails.title.toLowerCase()} route.
              </p>
              <div className="flex items-center justify-between mt-auto">
                <span className="text-[10px] font-bold text-slate-500 uppercase">{activeRouteMode}</span>
                <span className="text-blue-700">Continue Learning</span>
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
        <div className="p-3 border-b border-slate-100">
          <RouteNav compact />
        </div>
        <div className="p-4 border-b border-slate-100">
          <div className="mb-3 flex items-center justify-between">
            <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Profiles</div>
            <div className="text-[10px] font-bold text-teal-700">{dashboardProfiles.length}</div>
          </div>
          <div className="max-h-36 space-y-2 overflow-y-auto pr-1">
            {dashboardProfiles.map((item: any) => {
              const isActive = item.id === currentChatId;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setCurrentChatId(item.id)}
                  className={`w-full rounded-lg border p-2 text-left transition-all ${
                    isActive ? 'border-teal-200 bg-teal-50' : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <UserRound className={`h-4 w-4 ${isActive ? 'text-teal-700' : 'text-slate-400'}`} />
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-xs font-black text-slate-900">{item.label}</div>
                      <div className="truncate text-[10px] font-medium text-slate-500">{item.skills.join(', ') || 'No skills added'}</div>
                    </div>
                    <span className="rounded-full bg-white px-1.5 py-0.5 text-[9px] font-black text-teal-700">{item.completedCount}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
        <div className="p-4 border-b border-slate-100">
          <div className="grid grid-cols-2 rounded-xl border border-slate-200 bg-slate-100 p-1 shadow-inner">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
              { id: 'map', label: 'Map', icon: MapIcon },
            ].map(({ id, label, icon: Icon }) => {
              const isActive = activeView === id;
              return (
                <button
                  key={id}
                  onClick={() => setActiveView(id as 'dashboard' | 'map')}
                  className={`flex h-10 items-center justify-center gap-2 rounded-lg text-xs font-black transition-all duration-200 ${
                    isActive
                      ? 'bg-white text-teal-700 shadow-sm ring-1 ring-slate-200'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </button>
              );
            })}
          </div>
        </div>
        
        <div className="p-4 flex-1 overflow-y-auto">
          {activeView === 'map' ? (
          <>
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
            <p className="text-[11px] text-slate-600 leading-relaxed">{activeRouteDetails.sidebarReason}</p>
            <div className="mt-3 rounded-lg bg-white px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-blue-700">
              Showing {totalNodesCount} learning stops
            </div>
          </div>
          </>
          ) : (
            <div className="rounded-lg border border-teal-100 bg-teal-50 p-4">
              <div className="mb-2 flex items-center gap-2 text-xs font-bold text-teal-700">
                <LayoutDashboard className="h-4 w-4" />
                Dashboard Focus
              </div>
              <p className="text-[11px] leading-relaxed text-slate-600">
                Progress graphs, current context, and the next step are expanded in the main workspace.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* CENTER: Dashboard or React Flow Map (Flexible) */}
      <div className="flex-1 relative flex flex-col min-w-0">
        {activeView === 'dashboard' ? (
          renderDashboardContent(true)
        ) : (
        <>
        
        {/* Top Header Overlay */}
        <div className="absolute top-0 left-0 right-0 p-6 z-10 pointer-events-none flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight drop-shadow-sm">Your Learning Map</h2>
            <p className="text-sm text-slate-600 font-medium">Your personalized route to {targetGoal}</p>
          </div>
          <div className="pointer-events-auto bg-white border border-slate-200 rounded-lg p-1.5 flex gap-1 shadow-sm">
            <button disabled={historyIndex <= 0} onClick={() => navigateHistory(-1)} className={`px-3 py-1.5 text-xs font-bold rounded transition-colors ${historyIndex <= 0 ? 'text-slate-300' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}>←</button>
            <button disabled={historyIndex >= graphHistory.length - 1} onClick={() => navigateHistory(1)} className={`px-3 py-1.5 text-xs font-bold rounded transition-colors ${historyIndex >= graphHistory.length - 1 ? 'text-slate-300' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}>→</button>
            <div className="w-px bg-slate-200 my-1 mx-1" />
            <button className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-900 rounded transition-colors">Fit Map</button>
            <div className="w-px bg-slate-200 my-1 mx-1" />
            <button className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-900 rounded transition-colors">Reset</button>
          </div>
        </div>

        <ReactFlow
          key={activeRouteMode}
          nodes={displayedNodes}
          edges={displayedEdges}
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
                {messages.map((msg: any, idx: any) => (
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
                  <input type="text" value={chatInput} onChange={(e: any) => setChatInput(e.target.value)} placeholder="Modify path..." className="w-full pl-3 pr-10 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:border-teal-500 outline-none text-xs text-slate-900" />
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
        </>
        )}
      </div>

      {/* RIGHT SIDEBAR: 350px width */}
      {activeView === 'map' && (
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
                {loadingExplanation ? (
                  <div className="mb-6 space-y-2">
                    <div className="h-3 bg-slate-200 rounded animate-pulse w-full"></div>
                    <div className="h-3 bg-slate-200 rounded animate-pulse w-4/5"></div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-600 leading-relaxed mb-6">
                    {nodeExplanation || "This skill is part of your learning path toward the selected goal."}
                  </p>
                )}

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

                <h3 className="text-sm font-bold text-slate-900 mb-2 border-b pb-1">🎥 Learn</h3>
                
                {loadingResources ? (
                  <div className="flex flex-col items-center justify-center p-4 space-y-3">
                    <Loader2 className="w-6 h-6 text-teal-500 animate-spin" />
                    <div className="text-xs text-slate-500 font-medium animate-pulse">Loading verified recommendations...</div>
                  </div>
                ) : youtubeStatus === 'API_FAILED' && sidebarResources.length === 0 ? (
                  <div className="p-4 bg-slate-50 border border-slate-200 border-dashed rounded-xl text-center mb-6">
                    <div className="text-xs text-slate-500">Video recommendations are temporarily unavailable.</div>
                  </div>
                ) : sidebarResources.filter(r => !r._is_project_tutorial).length > 0 ? (
                  <div className="space-y-3 mb-6">
                    {sidebarResources.filter(r => !r._is_project_tutorial).map((res: any, i: any) => (
                      <div key={i} className="p-3 bg-white border border-slate-200 shadow-sm rounded-xl hover:border-red-300 transition-colors group">
                        <div className="flex gap-3 mb-2">
                          <div className="w-20 h-14 rounded overflow-hidden flex-shrink-0 bg-slate-100">
                            {res.thumbnail ? (
                              <img src={res.thumbnail} alt={res.title} className="w-full h-full object-cover" />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center"><PlaySquare className="w-6 h-6 text-slate-400" /></div>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex justify-between items-start gap-2">
                              <div className="text-xs font-bold text-slate-900 leading-tight mb-1 line-clamp-2" title={res.title}>{res.title}</div>
                              {res.match_percentage && <div className="text-[9px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded font-bold whitespace-nowrap flex-shrink-0">{res.match_percentage}% Match</div>}
                            </div>
                            <div className="text-[10px] text-slate-500 flex items-center gap-1.5 flex-wrap">
                              <span className="font-semibold text-slate-700">{res.channel || 'YouTube'}</span>
                              {res.language && <span className="bg-slate-100 px-1 rounded">{res.language.toUpperCase()}</span>}
                            </div>
                          </div>
                        </div>
                        <a href={res.url} target="_blank" rel="noreferrer" className="mt-2 w-full py-1.5 bg-red-50 hover:bg-red-100 text-red-600 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition-colors">
                          <PlaySquare className="w-3.5 h-3.5" /> Watch Tutorial
                        </a>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 bg-slate-50 border border-slate-200 border-dashed rounded-xl text-center mb-6">
                    <div className="text-xs text-slate-500">No verified tutorials available right now.</div>
                  </div>
                )}
                {/* COURSES SECTION */}
                {recommendations?.courses?.length > 0 && (
                   <div className="mb-6">
                      <h3 className="text-sm font-bold text-slate-900 mb-2 border-b pb-1">🎓 Courses</h3>
                      <div className="space-y-2">
                         {recommendations.courses.map((c: any, i: any) => (
                            <div key={i} className="p-3 border border-slate-200 rounded-lg bg-slate-50 flex flex-col gap-2 shadow-sm hover:border-indigo-200 transition-colors">
                               <div className="flex justify-between items-start">
                                  <div className="font-bold text-xs text-slate-800 leading-tight pr-2">{c.title}</div>
                                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                                    <div className="text-[9px] bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded font-bold whitespace-nowrap tracking-wide">{c.provider}</div>
                                    {c.match_percentage && <div className="text-[9px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded font-bold whitespace-nowrap">{c.match_percentage}% Match</div>}
                                  </div>
                               </div>
                               <div className="flex justify-between items-center text-[10px]">
                                  <div className="text-slate-500 font-medium flex items-center gap-1">
                                    <span className="text-amber-500 font-bold">★ {c.rating ? Number(c.rating).toFixed(1) : 'N/A'}</span>
                                    <span>({c.review_count || 0})</span>
                                  </div>
                                  <div className="font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">{c.cost_type === 'PAID' ? `${c.currency || '$'}${c.price || '...'}` : c.cost_type}</div>
                               </div>
                               <a href={c.url} target="_blank" rel="noreferrer" className="w-full py-1.5 bg-[#2D6A62] hover:bg-[#21524b] text-white text-xs font-bold rounded flex items-center justify-center transition-colors mt-1 shadow-sm">
                                  View Course
                               </a>
                            </div>
                         ))}
                      </div>
                   </div>
                )}

                {/* PRACTICE SECTION */}
                {recommendations?.practice?.length > 0 && (
                   <div className="mb-6">
                      <h3 className="text-sm font-bold text-slate-900 mb-2 border-b pb-1">💻 Practice</h3>
                      <div className="space-y-2">
                         {recommendations.practice.map((p: any, i: any) => (
                            <div key={i} className="p-3 border border-slate-200 rounded-lg bg-slate-50">
                               <div className="flex justify-between items-start mb-1">
                                  <div className="font-bold text-sm text-slate-800">{p.platform}</div>
                                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                                    <div className="text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold">{p.cost}</div>
                                    {p.match_percentage && <div className="text-[9px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded font-bold">{p.match_percentage}% Match</div>}
                                  </div>
                               </div>
                               <div className="text-xs text-slate-600 mb-2">{p.why}</div>
                               <a href={p.url} target="_blank" rel="noreferrer" className="w-full py-1.5 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 text-xs font-bold rounded-lg flex items-center justify-center gap-2">
                                  Practice Now
                               </a>
                            </div>
                         ))}
                      </div>
                   </div>
                )}

                {/* BUILD SECTION */}
                {recommendations?.project && (
                   <div className="mb-6">
                      <h3 className="text-sm font-bold text-slate-900 mb-2 border-b pb-1">🚀 Build a Project</h3>
                      <div className="p-3 border border-amber-200 bg-amber-50 rounded-lg mb-3">
                         <div className="font-bold text-amber-900 text-sm mb-1">{recommendations.project.title}</div>
                         <div className="text-xs text-amber-700 mb-2">{recommendations.project.description}</div>
                         <div className="flex gap-2 text-[10px] font-bold text-amber-600 uppercase">
                            <span className="bg-amber-100 px-1.5 py-0.5 rounded">{recommendations.project.difficulty}</span>
                            <span className="bg-amber-100 px-1.5 py-0.5 rounded">~{recommendations.project.estimated_hours} hrs</span>
                         </div>
                      </div>
                      
                      {/* Project Tutorials */}
                      {sidebarResources.filter(r => r._is_project_tutorial).map((res: any, i: any) => (
                          <div key={i} className="flex gap-3 mb-2 p-2 border border-slate-200 rounded hover:bg-slate-50">
                             <div className="flex-1 min-w-0">
                                <div className="text-xs font-bold text-slate-800 truncate" title={res.title}>{res.title}</div>
                                <div className="text-[10px] text-slate-500">{res.language?.toUpperCase() || 'EN'} Tutorial</div>
                             </div>
                             <a href={res.url} target="_blank" rel="noreferrer" className="px-3 py-1 bg-slate-800 text-white text-xs font-bold rounded hover:bg-slate-700 flex items-center justify-center">
                                Watch
                             </a>
                          </div>
                      ))}
                   </div>
                )}

                {/* READ SECTION */}
                {recommendations?.read?.length > 0 && (
                   <div className="mb-6">
                      <h3 className="text-sm font-bold text-slate-900 mb-2 border-b pb-1">📖 Read & Understand</h3>
                      <div className="space-y-2">
                         {recommendations.read.map((r: any, i: any) => (
                            <div key={i} className="flex justify-between items-center p-2.5 border border-slate-200 rounded-lg bg-slate-50">
                               <div>
                                  <div className="flex items-center gap-2">
                                    <div className="text-xs font-bold text-slate-800">{r.title}</div>
                                    {r.match_percentage && <div className="text-[9px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded font-bold whitespace-nowrap">{r.match_percentage}% Match</div>}
                                  </div>
                                  <div className="text-[10px] text-slate-500">{r.source}</div>
                               </div>
                               <a href={r.url} target="_blank" rel="noreferrer" className="px-3 py-1 bg-white border border-slate-300 text-slate-700 text-xs font-bold rounded hover:bg-slate-100">
                                  Read
                               </a>
                            </div>
                         ))}
                      </div>
                   </div>
                )}

                {/* PROGRESS SECTION */}
                <div className="mt-8 pt-4 border-t border-slate-200">
                   {completedSkills.includes(selectedNode.data.skill_id) ? (
                      <button onClick={async () => {
                         const token = localStorage.getItem('token');
                         if (token) {
                             await fetch(`${API_URL}/api/progress/${selectedNode.data.skill_id}/incomplete`, {
                                 method: 'POST',
                                 headers: { 'Authorization': `Bearer ${token}` }
                             });
                         }
                         markIncomplete(selectedNode.data.skill_id);
                         setSelectedNode(null);
                      }} className="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors flex items-center justify-center gap-2">
                         Mark as Incomplete
                      </button>
                   ) : (
                      <>
                        <button onClick={async () => {
                           const token = localStorage.getItem('token');
                           if (token) {
                               await fetch(`${API_URL}/api/progress/${selectedNode.data.skill_id}/complete`, {
                                   method: 'POST',
                                   headers: { 'Authorization': `Bearer ${token}` }
                               });
                           }
                           markComplete(selectedNode.data.skill_id);
                           setStrugglingSkills(prev => prev.filter(id => id !== selectedNode.data.skill_id));
                           setSelectedNode(null);
                        }} className="w-full py-2.5 bg-[#2D6A62] hover:bg-[#21524b] text-white font-bold rounded-xl shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 mb-2">
                           <CheckCircle className="w-5 h-5" /> Mark Complete
                        </button>
                        <button onClick={async () => {
                           const token = localStorage.getItem('token');
                           if (token) {
                               await fetch(`${API_URL}/api/progress/${selectedNode.data.skill_id}/struggling`, {
                                   method: 'POST',
                                   headers: { 'Authorization': `Bearer ${token}` }
                               });
                           }
                           if (!strugglingSkills.includes(selectedNode.data.skill_id)) {
                               setStrugglingSkills(prev => [...prev, selectedNode.data.skill_id]);
                               fetchResourcesForSkill(selectedNode.data.skill_id, true);
                           }
                        }} className={`w-full py-2.5 font-bold rounded-xl shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 ${strugglingSkills.includes(selectedNode.data.skill_id) ? 'bg-amber-500 text-white' : 'bg-white border border-amber-500 text-amber-600 hover:bg-amber-50'}`}>
                           <AlertCircle className="w-5 h-5" /> {strugglingSkills.includes(selectedNode.data.skill_id) ? "Struggling (Adapting...)" : "I'm Struggling"}
                        </button>
                      </>
                   )}
                </div>

              </div>
            </>
          )}
        </div>

        {/* Default Dashboard State */}
        {renderDashboardContent(false)}

      </div>
      )}
    </div>
  );
}

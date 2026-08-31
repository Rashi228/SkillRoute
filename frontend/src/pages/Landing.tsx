import { Link } from 'react-router-dom';
import { ArrowRight, Map, Compass, BrainCircuit, Target, Sparkles, User, Bot, BookOpen } from 'lucide-react';
import RouteNav from '../components/RouteNav';

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#F8FAFC] text-gray-900 font-sans selection:bg-teal-200">
      {/* Navigation */}
      <nav className="fixed w-full bg-white/90 backdrop-blur-md z-50 border-b border-gray-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex min-h-16 flex-col gap-3 py-3 md:flex-row md:items-center md:justify-between md:gap-4">
            <div className="flex items-center gap-2">
              <Compass className="w-8 h-8 text-teal-600" />
              <span className="font-extrabold text-xl tracking-tight text-slate-800">SkillRoute</span>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <RouteNav />
              <a href="#login" className="text-slate-600 hover:text-teal-600 px-3 py-2 font-bold transition-colors">Sign In</a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden bg-gradient-to-b from-teal-50/50 to-[#F8FAFC]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-12">
          {/* Left Hero Text */}
          <div className="md:w-1/2 text-left">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-100 text-teal-800 text-sm font-bold mb-8 shadow-sm">
              <Sparkles className="w-4 h-4" />
              <span>AI-Powered Learning Paths</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-8 text-slate-900 drop-shadow-sm">
              Google Maps for <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-600 to-emerald-500">Your Learning Journey</span>
            </h1>
            <p className="mt-6 text-xl text-slate-600 leading-relaxed mb-10 font-medium">
              Stop searching for courses. Tell us your goal, your skills, and your constraints. 
              We generate the perfect, personalized roadmap to get you there using verified resources.
            </p>
          </div>

          {/* Right Login Form */}
          <div id="login" className="md:w-1/2 w-full max-w-md mx-auto bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.08)] border border-slate-100 p-8 relative z-10">
            <h2 className="text-2xl font-black text-slate-900 mb-6 text-center">Welcome to SkillRoute</h2>
            <LandingLoginForm />
          </div>
        </div>
      </section>

      {/* Feature Layout (Green Theme) */}
      <section className="relative pt-32 pb-32 bg-[#2D6A62] text-white overflow-visible mt-20">
        {/* Curved Top Background */}
        <div className="absolute top-0 left-0 right-0 h-32 bg-[#F8FAFC] rounded-b-[50%] scale-x-[1.2] -translate-y-16 origin-top"></div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center mb-12 -mt-40 relative z-20">
            <h2 className="text-4xl font-black text-slate-900 mb-2">Our Top Features</h2>
            <p className="text-slate-500 font-medium">We provide the best tools for the best results.</p>
          </div>

          {/* Overlapping Cards */}
          <div className="flex flex-wrap justify-center gap-6 mb-24 relative z-20">
            {[
              { id: 1, title: 'AI Profiler', desc: 'Chat with our AI agent to set your goals.', icon: Bot },
              { id: 2, title: 'Verified Data', desc: 'Resources pulled from real APIs.', icon: Sparkles },
              { id: 3, title: 'Smart Routes', desc: 'Fast vs Deep learning paths.', icon: Map },
              { id: 4, title: 'Skill Passports', desc: 'Evidence-based tracking.', icon: Target },
            ].map((card) => (
              <div key={card.id} className="bg-[#EAF5F4] text-slate-900 p-6 rounded-2xl shadow-xl w-64 flex flex-col items-center border-t-4 border-[#2D6A62] hover:-translate-y-2 transition-transform cursor-pointer">
                 <div className="w-16 h-16 rounded-full bg-white mb-4 flex items-center justify-center shadow-inner">
                   <card.icon className="w-8 h-8 text-[#2D6A62]" />
                 </div>
                 <h3 className="font-bold text-lg text-[#11312C]">{card.title}</h3>
                 <p className="text-xs text-center text-slate-500 mt-2 font-medium">{card.desc}</p>
                 <div className="mt-4 w-full flex justify-between text-xs font-bold text-[#2D6A62]">
                   <span>Price</span>
                   <span>FREE</span>
                 </div>
              </div>
            ))}
          </div>

          {/* Middle Section */}
          <div className="flex flex-col md:flex-row items-center gap-16 mb-32">
             <div className="md:w-1/2 relative">
                <div className="aspect-[4/3] bg-slate-900 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden relative border-8 border-[#1A453F]">
                  {/* Mock Image Content */}
                  <div className="absolute inset-0 bg-gradient-to-tr from-[#1A453F] to-slate-800 flex flex-col items-center justify-center p-8 text-center">
                    <BrainCircuit className="w-24 h-24 text-teal-400 mb-4 opacity-80" />
                    <div className="w-3/4 h-4 bg-slate-700 rounded-full mb-3"></div>
                    <div className="w-1/2 h-4 bg-slate-700 rounded-full"></div>
                  </div>
                </div>
                <div className="absolute -bottom-8 -right-8 w-28 h-28 bg-white rounded-full flex flex-col items-center justify-center text-[#2D6A62] shadow-2xl border-4 border-[#EAF5F4]">
                  <span className="text-3xl font-black">100%</span>
                  <span className="text-[10px] font-bold uppercase tracking-wider">AI Powered</span>
                </div>
             </div>
             <div className="md:w-1/2">
               <h2 className="text-4xl md:text-5xl font-black mb-6 leading-tight">Welcome To <br/>SkillRoute Navigator</h2>
               <p className="text-teal-50/80 mb-8 leading-relaxed font-medium">
                 Stop taking random courses. Our hybrid recommendation engine analyzes your exact needs and generates a personalized, step-by-step learning map using verified resources from around the web.
               </p>
               <button className="bg-white text-[#2D6A62] font-bold py-3 px-8 rounded-lg shadow-lg hover:bg-teal-50 transition-colors">
                 About Us
               </button>
             </div>
          </div>

          {/* Bottom Section */}
          <div className="flex flex-col md:flex-row items-start gap-12 border-t border-teal-700/50 pt-16">
            <div className="md:w-1/3">
              <div className="text-teal-300 text-sm font-bold uppercase tracking-widest mb-2">Services</div>
              <h2 className="text-3xl md:text-4xl font-black mb-6 leading-tight">What We<br/>Provide To You</h2>
              <p className="text-teal-50/80 mb-8 leading-relaxed text-sm font-medium">
                SkillRoute bridges the gap between your current knowledge and your ultimate career goals with precision, offering tailored content for every learning style.
              </p>
              <button className="bg-white text-[#2D6A62] font-bold py-2.5 px-6 rounded-lg shadow-lg hover:bg-teal-50 transition-colors text-sm">
                 View More
               </button>
            </div>
            <div className="md:w-2/3 grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
               {[
                 { id: 1, title: 'Conversational UI', desc: 'No more boring forms. Just chat with our AI.' },
                 { id: 2, title: 'Verified Discovery', desc: 'Real YouTube videos pulled dynamically.' },
                 { id: 3, title: 'React Flow Maps', desc: 'Beautiful interactive visualization of your path.' },
                 { id: 4, title: 'Constraint Engine', desc: 'Filter by free, freemium, or paid resources.' },
               ].map((feature, i) => (
                 <div key={feature.id} className={`p-8 rounded-xl border border-teal-600/30 shadow-lg ${i === 0 ? 'bg-white text-slate-900' : 'bg-[#1A453F] text-white hover:bg-[#20524B] transition-colors'}`}>
                   <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold mb-6 text-sm ${i === 0 ? 'bg-[#2D6A62] text-white' : 'bg-teal-500/20 text-teal-300'}`}>
                     {feature.id}
                   </div>
                   <h3 className="font-bold text-lg mb-2">{feature.title}</h3>
                   <p className={`text-sm leading-relaxed ${i === 0 ? 'text-slate-500' : 'text-teal-100/60'}`}>
                     {feature.desc}
                   </p>
                 </div>
               ))}
            </div>
          </div>
        </div>
      </section>

      {/* Step-by-Step Instructions (Zig-Zag Timeline) */}
      <section className="py-24 bg-[#EAF2F4] relative overflow-hidden">
        {/* Background shapes */}
        <div className="absolute top-10 right-20 w-64 h-64 bg-teal-200/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-white/40 rounded-t-[100%]"></div>
        
        <div className="max-w-5xl mx-auto px-4 relative z-10">
          <div className="text-center mb-24">
            <h2 className="text-4xl font-black text-[#2f3d53] mb-6 tracking-tight">Step-by-Step Instructions</h2>
            <p className="text-[#6B7280] max-w-3xl mx-auto text-lg">
              To start using SkillRoute, simply follow this verified workflow to generate your ultimate learning map. Connect your goals to real skills and let our AI handle the rest.
            </p>
          </div>

          <div className="relative max-w-4xl mx-auto flex flex-col items-center gap-16 pb-16">
            
            {/* Desktop SVG Connecting Lines */}
            <div className="hidden md:block absolute inset-0 z-0 pointer-events-none -ml-4">
              <svg className="w-full h-full" viewBox="0 0 800 600" preserveAspectRatio="none">
                {/* Curve 1 to 2 */}
                <path d="M 400,50 C 650,50 650,180 400,180" fill="none" stroke="#94a3b8" strokeWidth="2" strokeDasharray="6,6" />
                {/* Curve 2 to 3 */}
                <path d="M 400,180 C 150,180 150,310 400,310" fill="none" stroke="#94a3b8" strokeWidth="2" strokeDasharray="6,6" />
                {/* Curve 3 to 4 */}
                <path d="M 400,310 C 650,310 650,440 400,440" fill="none" stroke="#94a3b8" strokeWidth="2" strokeDasharray="6,6" />
              </svg>
            </div>

            {/* Step 1 */}
            <div className="relative z-10 flex w-full justify-center md:justify-start md:pl-20">
               <TimelineStep number="1." icon={Bot} title="Chat Profiler" text="Talk to our AI Agent" link="Connect AI here" />
            </div>

            {/* Step 2 */}
            <div className="relative z-10 flex w-full justify-center md:justify-end md:pr-20">
               <TimelineStep number="2." icon={Target} title="Gap Analysis" text="Identify Missing Skills" />
            </div>

            {/* Step 3 */}
            <div className="relative z-10 flex w-full justify-center md:justify-start md:pl-20">
               <TimelineStep number="3." icon={Sparkles} title="Discovery Engine" text="Search Verified APIs" link="Download dataset here" />
            </div>

            {/* Step 4 */}
            <div className="relative z-10 flex w-full justify-center">
               <TimelineStep number="4." icon={Map} title="Configuration" text="Configure your map settings" isCenter={true} />
            </div>
            
            {/* Bottom 3 sub-items attached to Step 4 */}
            <div className="relative z-10 flex flex-wrap justify-center gap-6 md:gap-12 mt-2 w-full max-w-2xl">
               
               {/* Line 1 */}
               <div className="flex flex-col items-center">
                 <div className="w-[2px] h-12 bg-[#1DA4AE] mb-3"></div>
                 <div className="bg-[#1e293b] text-white p-3 rounded-2xl shadow-xl flex items-center gap-3 w-40 border border-slate-700">
                   <div className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center">
                     <Target className="text-teal-400 w-6 h-6" />
                   </div>
                   <span className="text-[11px] leading-tight font-medium text-slate-300">Set your Target<br/>Goals</span>
                 </div>
               </div>

               {/* Line 2 */}
               <div className="flex flex-col items-center">
                 <div className="w-[2px] h-12 bg-[#1DA4AE] mb-3"></div>
                 <div className="bg-[#1e293b] text-white p-3 rounded-2xl shadow-xl flex items-center gap-3 w-40 border border-slate-700">
                   <div className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center">
                     <Bot className="text-blue-400 w-6 h-6" />
                   </div>
                   <span className="text-[11px] leading-tight font-medium text-slate-300">Link your AI<br/>Coach</span>
                 </div>
               </div>

               {/* Line 3 */}
               <div className="flex flex-col items-center">
                 <div className="w-[2px] h-12 bg-[#1DA4AE] mb-3"></div>
                 <div className="bg-[#1e293b] text-white p-3 rounded-2xl shadow-xl flex items-center gap-3 w-40 border border-slate-700">
                   <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                     {/* Google 'G' fake icon */}
                     <span className="text-blue-600 font-black text-xl">G</span>
                   </div>
                   <span className="text-[11px] leading-tight font-medium text-slate-300">Link your Google<br/>Account</span>
                 </div>
               </div>

            </div>

          </div>
          
          <div className="mt-8 text-center relative z-20 pb-12">
            <p className="text-sm text-slate-500 mb-6 font-medium">You can find step-by-step instructions<br/>on how to configure SkillRoute here:</p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="px-6 py-2 border-2 border-orange-500 text-orange-600 font-bold rounded hover:bg-orange-50 transition-colors">Instructions</button>
              <button className="px-6 py-2 border-2 border-orange-500 text-orange-600 font-bold rounded hover:bg-orange-50 transition-colors">SkillRoute App</button>
              <button className="px-6 py-2 border-2 border-orange-500 text-orange-600 font-bold rounded hover:bg-orange-50 transition-colors">Documentation</button>
              <button className="px-6 py-2 border-2 border-orange-500 text-orange-600 font-bold rounded hover:bg-orange-50 transition-colors">Sources</button>
            </div>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12 text-center border-t border-slate-800">
        <div className="flex justify-center items-center gap-2 mb-4">
          <Compass className="w-6 h-6 text-teal-500" />
          <span className="font-bold text-lg text-slate-300">SkillRoute</span>
        </div>
        <p className="font-medium">© 2026 SkillRoute (HCLTech Prototype). All rights reserved.</p>
      </footer>
    </div>
  );
}

import { useState } from 'react';

import { API_URL } from '../config';

function LandingLoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleBypassLogin = () => {
    localStorage.setItem('token', 'dev-auth-bypass-token');
    localStorage.setItem('userEmail', 'dev@skillroute.local');
    localStorage.setItem('skillroute_access_granted', 'true');
    window.location.href = '/dashboard';
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${API_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.detail || "Invalid credentials.");
        return;
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('userEmail', email);
      localStorage.setItem('skillroute_access_granted', 'true');
      window.location.href = '/profiler';
    } catch (err) {
      setError("An error occurred during login. Please try again.");
    }
  };

  return (
    <>
      {error && <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm font-semibold rounded-xl border border-red-100">{error}</div>}
      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block text-sm font-bold text-slate-700 mb-1">Email</label>
          <input type="email" value={email} onChange={(e: any) => setEmail(e.target.value)} placeholder="admin@skillroute.com" className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all bg-slate-50" required />
        </div>
        <div>
          <label className="block text-sm font-bold text-slate-700 mb-1">Password</label>
          <input type="password" value={password} onChange={(e: any) => setPassword(e.target.value)} placeholder="Admin123!" className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none transition-all bg-slate-50" required />
        </div>
        <button type="submit" className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3.5 rounded-xl transition-all shadow-md hover:shadow-lg mt-2 flex items-center justify-center gap-2">
          Sign In & Start Journey <ArrowRight className="w-4 h-4" />
        </button>
      </form>
      <div className="my-5 flex items-center gap-3">
        <div className="h-px flex-1 bg-slate-200" />
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Temporary Access</span>
        <div className="h-px flex-1 bg-slate-200" />
      </div>
      <button
        type="button"
        onClick={handleBypassLogin}
        className="w-full border border-teal-200 bg-teal-50 hover:bg-teal-100 text-teal-800 font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2"
      >
        Bypass Login & Open Dashboard <ArrowRight className="w-4 h-4" />
      </button>
      <p className="text-center text-sm text-slate-500 mt-6 font-medium">
        Don't have an account? <Link to="/register" className="text-teal-600 font-bold hover:text-teal-700 hover:underline">Sign up for free</Link>
      </p>
    </>
  );
}

// Timeline Step Helper
function TimelineStep({ number, icon: Icon, title, text, link, isCenter = false }: any) {
  return (
    <div className="flex flex-col items-center">
      <div className="relative flex items-center bg-[#1DA4AE] rounded-xl shadow-lg h-16 w-80 max-w-[90vw]">
        {/* Left Number Box */}
        <div className={`h-full px-6 flex items-center justify-center bg-teal-600 rounded-l-xl text-white font-black text-xl`}>
          {number}
        </div>
        
        {/* Overlapping White Badge */}
        <div className="absolute left-14 w-20 h-20 bg-white rounded-xl shadow-[0_4px_15px_rgba(0,0,0,0.08)] flex flex-col items-center justify-center border border-slate-100 z-20 overflow-hidden group">
          <Icon className="w-8 h-8 text-[#2f3d53] group-hover:scale-110 transition-transform" />
          <span className="text-[9px] font-bold text-slate-400 mt-1 uppercase tracking-wider">{title.split(' ')[0]}</span>
        </div>
        
        {/* Right Text Box */}
        <div className="pl-24 pr-4 flex flex-col justify-center text-white h-full">
          <div className="font-semibold text-lg leading-none truncate w-full">{title}</div>
        </div>
      </div>
      
      {/* Optional Link underneath (like the original image) */}
      {link && (
        <a href="#" className={`mt-3 text-sm text-slate-500 underline decoration-slate-300 hover:text-teal-600 transition-colors ${isCenter ? 'text-center' : '-ml-20'}`}>
          {link}
        </a>
      )}
    </div>
  )
}

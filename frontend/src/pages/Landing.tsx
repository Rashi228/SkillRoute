import { Link } from 'react-router-dom';
import {
  ArrowRight, Map, Compass, BrainCircuit, Target,
  Sparkles, Bot, BookOpen,
} from 'lucide-react';
import RouteNav from '../components/RouteNav';
import Hero3DBackground from '../components/Hero3DBackground';
import { useState, useEffect, useRef } from 'react';
import { API_URL } from '../config';
import { motion, AnimatePresence } from 'framer-motion';


function useTypewriter(words: string[], speed = 80, pause = 1600) {
  const [typed, setTyped] = useState('');
  const [wordIdx, setWordIdx] = useState(0);
  const [deleting, setDeleting] = useState(false);
  useEffect(() => {
    const word = words[wordIdx];
    let timeout: ReturnType<typeof setTimeout>;
    if (!deleting && typed.length < word.length) {
      timeout = setTimeout(() => setTyped(word.slice(0, typed.length + 1)), speed);
    } else if (!deleting && typed.length === word.length) {
      timeout = setTimeout(() => setDeleting(true), pause);
    } else if (deleting && typed.length > 0) {
      timeout = setTimeout(() => setTyped(typed.slice(0, -1)), speed / 2);
    } else if (deleting && typed.length === 0) {
      setDeleting(false);
      setWordIdx((i) => (i + 1) % words.length);
    }
    return () => clearTimeout(timeout);
  }, [typed, deleting, wordIdx, words, speed, pause]);
  return typed;
}


function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 12);
    window.addEventListener('scroll', h, { passive: true });
    return () => window.removeEventListener('scroll', h);
  }, []);
  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 120, damping: 20 }}
      className={`fixed w-full z-50 transition-all duration-300 ${scrolled
          ? 'bg-white/80 backdrop-blur-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border-b border-slate-100/80'
          : 'bg-transparent border-b border-transparent'
        }`}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex justify-between items-center h-18 py-3">
          <div className="flex items-center gap-2.5 cursor-pointer group">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center shadow-md group-hover:scale-110 transition-transform">
              <Compass className="w-4 h-4 text-white" />
            </div>
            <span className="font-extrabold text-xl tracking-tight text-slate-800">SkillRoute</span>
          </div>

          <div className="hidden md:flex items-center gap-1">
            <RouteNav />
          </div>

          <div className="flex items-center gap-2">
            <a href="#login" className="px-4 py-2 text-sm font-bold text-slate-600 hover:text-teal-700 transition-colors">
              Sign In
            </a>
            <Link
              to="/register"
              className="flex items-center gap-2 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white px-5 py-2.5 rounded-full text-sm font-bold transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5"
            >
              Get Started <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </motion.nav>
  );
}



export default function Landing() {
  const typed = useTypewriter(['Machine Learning', 'Web Development', 'Data Science', 'Cloud & DevOps', 'UI/UX Design']);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-gray-900 font-sans selection:bg-teal-200">
      <Navbar />

      <section className="relative pt-28 pb-16 px-4 sm:px-6 lg:px-8 overflow-hidden bg-gradient-to-b from-teal-50/60 via-[#F8FAFC] to-[#F8FAFC]">
        <Hero3DBackground />

        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-teal-300/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-14 relative z-10">

          <motion.div
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, ease: 'easeOut' }}
            className="md:w-1/2 text-left"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-100 text-teal-800 text-sm font-bold mb-8 shadow-sm"
              style={{ animation: 'badge-float 3s ease-in-out infinite' }}
            >
              <Sparkles className="w-4 h-4" style={{ animation: 'spin-slow 5s linear infinite' }} />
              <span>AI-Powered Learning Paths</span>
            </motion.div>

            <h1 className="text-5xl md:text-[4.25rem] font-black mt-2 tracking-tight leading-[1.08] mb-4 text-slate-900">
              Your AI Navigator
              <br />
              <span
                className="text-transparent bg-clip-text"
                style={{
                  backgroundImage: 'linear-gradient(90deg,#0d9488,#10b981,#0ea5e9,#0d9488)',
                  backgroundSize: '200% auto',
                  animation: 'gradient-shift 4s linear infinite',
                }}
              >
                to Any Skill
              </span>
            </h1>

            {/* Typewriter */}
            <p className="text-lg font-bold text-slate-500 mt-3 mb-2 h-7">
              Master{' '}
              <span className="text-teal-600 border-r-2 border-teal-500 pr-0.5 animate-pulse">
                {typed}
              </span>
            </p>

            <p className="text-lg text-slate-500 leading-relaxed mb-8 font-medium max-w-md">
              Tell us your goal, skills, and constraints. We generate the perfect personalized roadmap using verified resources.
            </p>

            <div className="flex flex-wrap gap-3">
              <a
                href="#login"
                className="flex items-center gap-2 bg-slate-900 hover:bg-teal-700 text-white px-7 py-3.5 rounded-full font-bold transition-all shadow-md hover:shadow-xl hover:-translate-y-0.5 text-sm"
              >
                Start for Free <ArrowRight className="w-4 h-4" />
              </a>
              <a
                href="#features"
                className="flex items-center gap-2 border-2 border-slate-200 hover:border-teal-400 text-slate-700 hover:text-teal-700 px-6 py-3.5 rounded-full font-bold transition-all text-sm hover:bg-teal-50"
              >
                See Features
              </a>
            </div>


          </motion.div>

          {/* Right — Login Card */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.65, delay: 0.15, ease: 'easeOut' }}
            id="login"
            className="md:w-1/2 w-full max-w-md mx-auto bg-white/90 backdrop-blur-xl rounded-3xl border border-slate-100 p-8 relative z-10"
            style={{ boxShadow: '0 8px 40px rgba(13,148,136,0.10), 0 2px 8px rgba(0,0,0,0.06)' }}
            whileHover={{ y: -4, boxShadow: '0 20px 60px rgba(13,148,136,0.18)' }}
          >
            {/* Top gradient bar */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-teal-500 to-emerald-400 rounded-t-3xl" />
            <h2 className="text-2xl font-black text-slate-900 mb-1 text-center">Welcome to SkillRoute</h2>
            <p className="text-center text-slate-400 text-sm mb-6">Your AI-powered learning companion</p>
            <LandingLoginForm />
          </motion.div>

        </div>
      </section>

      {/* ─── Features ─── */}
      <section id="features" className="relative pt-32 pb-32 bg-[#2D6A62] text-white overflow-visible mt-20">
        <div className="absolute top-0 left-0 right-0 h-32 bg-[#F8FAFC] rounded-b-[50%] scale-x-[1.2] -translate-y-16 origin-top" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16 -mt-32 relative z-20"
          >
            <h2 className="text-4xl font-black text-slate-900">Our Top Features</h2>
            <p className="text-slate-500 font-medium">Everything you need to learn smarter, faster.</p>
          </motion.div>

          {/* Feature Cards */}
          <div className="flex flex-wrap justify-center gap-6 mb-32 relative z-20">
            {[
              { id: 1, title: 'AI Profiler', desc: 'Chat naturally with our AI to define goals, current skill level, and time constraints.', icon: Bot, gradient: 'from-teal-500 to-emerald-500' },
              { id: 2, title: 'Verified Data', desc: 'Every resource is pulled from live APIs — YouTube, Coursera, and more.', icon: Sparkles, gradient: 'from-sky-500 to-teal-500' },
              { id: 3, title: 'Smart Routes', desc: 'Choose between Fast Track and Deep Dive learning paths built for your pace.', icon: Map, gradient: 'from-emerald-500 to-green-500' },
              { id: 4, title: 'Skill Passports', desc: 'Track your progress with evidence-based milestones and completion badges.', icon: Target, gradient: 'from-teal-600 to-cyan-500' },
            ].map((card, idx) => (
              <motion.div
                key={card.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1, duration: 0.5 }}
                whileHover={{ y: -8, boxShadow: '0 16px 40px rgba(0,0,0,0.13)' }}
                className="bg-white text-slate-900 p-6 rounded-3xl shadow-[0_4px_24px_rgba(0,0,0,0.07)] w-64 flex flex-col items-start border border-slate-100 cursor-pointer group hover:border-teal-200 transition-all duration-300"
              >
                <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${card.gradient} mb-5 flex items-center justify-center shadow-md group-hover:scale-110 transition-transform`}>
                  <card.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-base text-slate-900 mb-2">{card.title}</h3>
                <p className="text-xs text-slate-500 leading-relaxed font-medium flex-1">{card.desc}</p>
                <div className="mt-5 flex items-center gap-1.5 text-teal-600 text-xs font-bold group-hover:gap-3 transition-all">
                  <span>Always Free</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </motion.div>
            ))}
          </div>

          {/* Middle — Brain visual + text */}
          <div className="flex flex-col md:flex-row items-center gap-16 mb-32">
            <motion.div
              initial={{ opacity: 0, scale: 0.92 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="md:w-1/2 relative"
            >
              <div className="aspect-[4/3] bg-slate-900 rounded-3xl overflow-hidden relative border-8 border-[#1A453F]" style={{ boxShadow: '0 20px 50px rgba(0,0,0,0.5)' }}>
                <div className="absolute inset-0 bg-gradient-to-tr from-[#0F2925] to-slate-800 flex flex-col items-center justify-center p-8 text-center overflow-hidden">
                  <motion.div
                    animate={{ scale: [1, 1.25, 1], opacity: [0.2, 0.5, 0.2] }}
                    transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
                    className="absolute w-72 h-72 bg-teal-500/20 rounded-full blur-3xl"
                  />
                  <BrainCircuit className="w-24 h-24 text-teal-400 mb-6 opacity-90 relative z-10" style={{ animation: 'pulse-slow 3s ease-in-out infinite' }} />
                  {[{ w: 'w-3/4', delay: 0 }, { w: 'w-1/2', delay: 0.4 }].map((bar, i) => (
                    <div key={i} className={`${bar.w} h-3 bg-slate-700/80 rounded-full relative z-10 overflow-hidden ${i === 0 ? 'mb-4' : ''}`}>
                      <motion.div
                        animate={{ x: ['-100%', '300%'] }}
                        transition={{ duration: 1.8 + bar.delay, repeat: Infinity, ease: 'linear', delay: bar.delay }}
                        className="w-2/5 h-full bg-teal-400/40 rounded-full"
                      />
                    </div>
                  ))}
                </div>
              </div>
              <motion.div
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4, type: 'spring' }}
                className="absolute -bottom-6 -right-6 w-24 h-24 bg-white rounded-2xl flex flex-col items-center justify-center text-[#2D6A62] border border-[#EAF5F4] z-20"
                style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.18)', animation: 'badge-float 4s ease-in-out infinite' }}
              >
                <span className="text-2xl font-black">100%</span>
                <span className="text-[9px] font-bold uppercase tracking-wider">AI Powered</span>
              </motion.div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="md:w-1/2"
            >
              <h2 className="text-4xl md:text-5xl font-black mb-5 leading-tight">Welcome To<br />SkillRoute Navigator</h2>
              <p className="text-teal-50/80 mb-8 leading-relaxed font-medium text-lg">
                Stop taking random courses. Our hybrid recommendation engine analyzes your exact needs
                and generates a personalized, step-by-step learning map using verified resources from around the web.
              </p>
              <button
                className="bg-white text-[#2D6A62] font-bold py-3.5 px-8 rounded-xl shadow-lg hover:bg-teal-50 transition-all hover:-translate-y-0.5"
              >
                Learn About Our Engine
              </button>
            </motion.div>
          </div>

          {/* Services Grid */}
          <div className="flex flex-col md:flex-row items-start gap-12 border-t border-teal-700/50 pt-16">
            <motion.div
              initial={{ opacity: 0, x: -24 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="md:w-1/3"
            >
              <div className="text-teal-300 text-xs font-bold uppercase tracking-widest mb-3">Services</div>
              <h2 className="text-3xl md:text-4xl font-black mb-5 leading-tight">What We<br />Provide To You</h2>
              <p className="text-teal-50/70 mb-8 leading-relaxed text-sm font-medium">
                SkillRoute bridges the gap between your current knowledge and your ultimate career goals with precision.
              </p>
              <button className="bg-white text-[#2D6A62] font-bold py-2.5 px-6 rounded-xl shadow-lg hover:bg-teal-50 transition-all hover:-translate-y-0.5 text-sm">
                View More
              </button>
            </motion.div>

            <div className="md:w-2/3 grid grid-cols-1 sm:grid-cols-2 gap-5 w-full">
              {[
                { id: 1, title: 'Conversational UI', desc: 'No more boring forms. Just chat with our AI.', icon: Bot },
                { id: 2, title: 'Verified Discovery', desc: 'Real YouTube videos pulled dynamically.', icon: BookOpen },
                { id: 3, title: 'React Flow Maps', desc: 'Beautiful interactive visualization of your path.', icon: Map },
                { id: 4, title: 'Constraint Engine', desc: 'Filter by free, freemium, or paid resources.', icon: Target },
              ].map((feature, i) => (
                <motion.div
                  key={feature.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  whileHover={{ scale: 1.03, y: -4 }}
                  className={`p-7 rounded-2xl border border-teal-600/30 shadow-md cursor-pointer ${i === 0 ? 'bg-white text-slate-900' : 'bg-[#1A453F] text-white hover:bg-[#20524B] transition-colors'}`}
                >
                  <div className={`w-9 h-9 rounded-xl flex items-center justify-center mb-5 ${i === 0 ? 'bg-teal-100 text-teal-700' : 'bg-teal-500/20 text-teal-300'}`}>
                    <feature.icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-lg mb-2">{feature.title}</h3>
                  <p className={`text-sm leading-relaxed ${i === 0 ? 'text-slate-500' : 'text-teal-100/60'}`}>{feature.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* ─── How it Works / Timeline ─── */}
      <section id="how-it-works" className="py-32 bg-[#EAF2F4] relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-teal-200/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 right-0 h-28 bg-white/40 rounded-t-[100%] pointer-events-none" />

        <div className="max-w-5xl mx-auto px-4 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-28"
          >
            <h2 className="text-4xl md:text-5xl font-black text-[#2f3d53] mb-4">How It Works</h2>
            <p className="text-[#6B7280] max-w-xl mx-auto text-base font-medium leading-relaxed">
              Follow these simple steps to generate your personalized learning roadmap in minutes.
            </p>
          </motion.div>

          <div className="relative max-w-4xl mx-auto flex flex-col items-center gap-20 pb-16">

            {/* Animated SVG curves */}
            <div className="hidden md:block absolute inset-0 z-0 pointer-events-none">
              <svg className="w-full h-full" viewBox="0 0 800 620" preserveAspectRatio="none">
                {[
                  { d: 'M 400,50 C 650,50 650,220 400,220', delay: 0 },
                  { d: 'M 400,220 C 150,220 150,390 400,390', delay: 0.5 },
                  { d: 'M 400,390 C 650,390 650,560 400,560', delay: 1 },
                ].map((path, i) => (
                  <motion.path
                    key={i}
                    d={path.d}
                    initial={{ pathLength: 0, opacity: 0 }}
                    whileInView={{ pathLength: 1, opacity: 1 }}
                    viewport={{ once: true, margin: '-80px' }}
                    transition={{ duration: 1.5, delay: path.delay, ease: 'easeInOut' }}
                    fill="none" stroke="#94a3b8" strokeWidth="2" strokeDasharray="7,7"
                  />
                ))}
              </svg>
            </div>

            {/* Steps */}
            {[
              { num: '1.', icon: Bot, title: 'Chat Profiler', text: 'Talk to our AI Agent', link: 'Connect AI here', pos: 'justify-start', pad: 'md:pl-20' },
              { num: '2.', icon: Target, title: 'Gap Analysis', text: 'Identify Missing Skills', link: null, pos: 'justify-end', pad: 'md:pr-20' },
              { num: '3.', icon: Sparkles, title: 'Discovery Engine', text: 'Search Verified APIs', link: 'Download dataset here', pos: 'justify-start', pad: 'md:pl-20' },
              { num: '4.', icon: Map, title: 'Configuration', text: 'Configure your map', isCenter: true, pos: 'justify-center', pad: '' },
            ].map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.92, y: 20 }}
                whileInView={{ opacity: 1, scale: 1, y: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ duration: 0.5, delay: i * 0.12 }}
                className={`relative z-10 flex w-full justify-center md:${step.pos} ${step.pad}`}
              >
                <TimelineStep number={step.num} icon={step.icon} title={step.title} text={step.text} link={step.link} isCenter={step.isCenter} />
              </motion.div>
            ))}

            {/* Sub-items */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="relative z-10 flex flex-wrap justify-center gap-6 md:gap-10 mt-2 w-full max-w-2xl"
            >
              {[
                { label: 'Set your Target Goals', Icon: Target, color: 'text-teal-400' },
                { label: 'Link your AI Coach', Icon: Bot, color: 'text-blue-400' },
                { label: 'Link Google Account', isGoogle: true },
              ].map((item, i) => (
                <div key={i} className="flex flex-col items-center group cursor-pointer">
                  <div className="w-px h-10 bg-[#1DA4AE] mb-3 group-hover:h-14 transition-all duration-300" />
                  <motion.div
                    whileHover={{ y: -4, boxShadow: '0 12px 32px rgba(0,0,0,0.3)' }}
                    className="bg-[#1e293b] text-white p-3 rounded-2xl shadow-xl flex items-center gap-3 w-44 border border-slate-700 group-hover:border-teal-500 transition-all"
                  >
                    <div className={`w-10 h-10 ${item.isGoogle ? 'bg-white' : 'bg-slate-800'} rounded-lg flex items-center justify-center flex-shrink-0`}>
                      {item.isGoogle
                        ? <span className="text-blue-600 font-black text-xl">G</span>
                        : item.Icon && <item.Icon className={`${item.color} w-5 h-5`} />}
                    </div>
                    <span className="text-[11px] leading-tight font-medium text-slate-300">{item.label}</span>
                  </motion.div>
                </div>
              ))}
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mt-16 text-center relative z-20 pb-12"
          >
            <p className="text-sm text-slate-500 mb-6 font-medium">Ready to dive deeper? Explore these resources:</p>
            <div className="flex flex-wrap justify-center gap-3">
              {['Instructions', 'SkillRoute App', 'Documentation', 'Sources'].map((label, i) => (
                <motion.button
                  key={label}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.07 }}
                  whileHover={{ y: -2 }}
                  className="px-5 py-2.5 border-2 border-orange-400 text-orange-600 text-sm font-bold rounded-xl hover:bg-orange-50 hover:shadow-md transition-all"
                >
                  {label}
                </motion.button>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer className="bg-slate-900 text-slate-400 py-14 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center">
              <Compass className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg text-slate-300">SkillRoute</span>
          </div>
          <p className="text-sm font-medium">© 2026 SkillRoute (HCLTech Prototype). All rights reserved.</p>
          <div className="flex gap-6 text-sm font-semibold">
            {['Privacy', 'Terms', 'Contact'].map(l => (
              <a key={l} href="#" className="hover:text-teal-400 transition-colors">{l}</a>
            ))}
          </div>
        </div>
      </footer>

      {/* Global keyframes */}
      <style>{`
        @keyframes badge-float  { 0%,100%{transform:translateY(0)}  50%{transform:translateY(-7px)} }
        @keyframes spin-slow    { to{transform:rotate(360deg)} }
        @keyframes gradient-shift { 0%{background-position:0% center} 100%{background-position:200% center} }
        @keyframes pulse-slow   { 0%,100%{opacity:.8;transform:scale(1)} 50%{opacity:1;transform:scale(1.04)} }
      `}</style>
    </div>
  );
}

/* ─────────────────────────────────────────
   Login Form
───────────────────────────────────────── */
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
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.detail || 'Invalid credentials.');
        return;
      }
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('userEmail', email);
      localStorage.setItem('skillroute_access_granted', 'true');
      window.location.href = '/profiler';
    } catch {
      setError('An error occurred during login. Please try again.');
    }
  };

  return (
    <>
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-4 p-3 bg-red-50 text-red-600 text-sm font-semibold rounded-xl border border-red-100"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block text-sm font-bold text-slate-700 mb-1.5">Email</label>
          <input
            type="email" value={email} onChange={(e: any) => setEmail(e.target.value)}
            placeholder="admin@skillroute.com"
            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-100 outline-none transition-all bg-slate-50/80 text-sm"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-bold text-slate-700 mb-1.5">Password</label>
          <input
            type="password" value={password} onChange={(e: any) => setPassword(e.target.value)}
            placeholder="Admin123!"
            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-100 outline-none transition-all bg-slate-50/80 text-sm"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white font-bold py-3.5 rounded-xl transition-all shadow-md hover:shadow-lg mt-2 flex items-center justify-center gap-2 group"
        >
          Sign In &amp; Start Journey <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>
      </form>

      <div className="my-5 flex items-center gap-3">
        <div className="h-px flex-1 bg-slate-200" />
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Temporary Access</span>
        <div className="h-px flex-1 bg-slate-200" />
      </div>

      <button
        type="button" onClick={handleBypassLogin}
        className="w-full border border-teal-200 bg-teal-50 hover:bg-teal-100 text-teal-800 font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2 group"
      >
        Bypass Login &amp; Open Dashboard <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
      </button>

      <p className="text-center text-sm text-slate-500 mt-5 font-medium">
        Don't have an account?{' '}
        <Link to="/register" className="text-teal-600 font-bold hover:text-teal-700 hover:underline">Sign up for free</Link>
      </p>
    </>
  );
}

/* ─────────────────────────────────────────
   Timeline Step
───────────────────────────────────────── */
function TimelineStep({ number, icon: Icon, title, text, link, isCenter = false }: any) {
  return (
    <div className="flex flex-col items-center group cursor-pointer">
      <motion.div
        whileHover={{ y: -4, boxShadow: '0 12px 32px rgba(29,164,174,0.35)' }}
        className="relative flex items-center bg-[#1DA4AE] rounded-2xl shadow-lg h-16 w-80 max-w-[90vw]"
      >
        <div className="h-full px-5 flex items-center justify-center bg-teal-600 rounded-l-2xl text-white font-black text-xl">
          {number}
        </div>
        <div className="absolute left-14 w-20 h-20 bg-white rounded-2xl shadow-[0_4px_15px_rgba(0,0,0,0.08)] flex flex-col items-center justify-center border border-slate-100 z-20">
          <Icon className="w-8 h-8 text-[#2f3d53] group-hover:scale-110 group-hover:text-teal-600 transition-all duration-300" />
          <span className="text-[9px] font-bold text-slate-400 mt-1 uppercase tracking-wider">{title.split(' ')[0]}</span>
        </div>
        <div className="pl-24 pr-4 flex flex-col justify-center text-white h-full">
          <div className="font-bold text-base leading-none">{title}</div>
          <div className="text-teal-100/70 text-xs mt-1">{text}</div>
        </div>
      </motion.div>
      {link && (
        <a href="#" className={`mt-3 text-sm font-medium text-slate-500 underline decoration-slate-300 hover:text-teal-600 transition-colors ${isCenter ? '' : '-ml-20'}`}>
          {link}
        </a>
      )}
    </div>
  );
}

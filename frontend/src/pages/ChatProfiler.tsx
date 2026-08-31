import { useEffect, useMemo, useState, type ReactNode } from 'react';
import {
  ArrowRight,
  CheckCircle,
  Clock,
  Compass,
  CopyPlus,
  ExternalLink,
  LayoutDashboard,
  PlaySquare,
  Plus,
  Save,
  BookOpen,
  Target,
  Trash2,
  ToggleLeft,
  ToggleRight,
  UserRound,
  WalletCards,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useChatContext } from '../context/ChatContext';
import RouteNav from '../components/RouteNav';

const profileTemplates = [
  {
    name: 'RAG Engineer',
    profile: {
      target_goal: 'Production RAG Engineer',
      current_skills: ['Python', 'Machine Learning Basics'],
      budget: 'FREE',
      time_commitment: '8 hrs/wk',
      deadline: '~18 weeks',
      learner_level: 'INTERMEDIATE',
    },
  },
  {
    name: 'Frontend Engineer',
    profile: {
      target_goal: 'Frontend Engineer',
      current_skills: ['HTML', 'CSS', 'JavaScript'],
      budget: 'FREE',
      time_commitment: '6 hrs/wk',
      deadline: '~14 weeks',
      learner_level: 'BEGINNER',
    },
  },
  {
    name: 'Data Analyst',
    profile: {
      target_goal: 'Data Analyst',
      current_skills: ['Spreadsheets', 'Basic SQL'],
      budget: 'LOW',
      time_commitment: '5 hrs/wk',
      deadline: '~12 weeks',
      learner_level: 'BEGINNER',
    },
  },
  {
    name: 'Cloud DevOps Engineer',
    profile: {
      target_goal: 'Cloud DevOps Engineer',
      current_skills: ['Linux Basics', 'Git', 'Networking'],
      budget: 'FREE',
      time_commitment: '8 hrs/wk',
      deadline: '~20 weeks',
      learner_level: 'INTERMEDIATE',
    },
  },
];

const emptyProfile = {
  target_goal: '',
  current_skills: [] as string[],
  budget: 'FREE',
  time_commitment: '',
  deadline: '',
  learner_level: 'INTERMEDIATE',
};

const getRecommendationFocus = (goal: string, currentSkills: string) => {
  const normalized = `${goal} ${currentSkills}`.toLowerCase();

  if (normalized.includes('frontend') || normalized.includes('react')) {
    return ['React State Management', 'Responsive UI Systems', 'TypeScript Patterns'];
  }

  if (normalized.includes('data analyst') || normalized.includes('sql') || normalized.includes('analytics')) {
    return ['SQL Joins & Aggregations', 'Dashboard Storytelling', 'Exploratory Analysis'];
  }

  if (normalized.includes('devops') || normalized.includes('cloud') || normalized.includes('kubernetes')) {
    return ['CI/CD Pipelines', 'Infrastructure as Code', 'Kubernetes Operations'];
  }

  return ['Vector Databases', 'Embeddings & Transformers', 'RAG Pipeline Architecture'];
};

const courseLinksBySkill: Record<string, string> = {
  'Vector Databases': 'https://www.coursera.org/learn/vector-databases-and-retrieval-data-engineering',
  'Embeddings & Transformers': 'https://www.coursera.org/learn/generative-ai-language-modeling-with-transformers',
  'RAG Pipeline Architecture': 'https://www.coursera.org/learn/retrieval-augmented-generation-rag',
  'React State Management': 'https://www.coursera.org/learn/react-basics',
  'Responsive UI Systems': 'https://www.coursera.org/learn/creating-responsive-websites-for-any-device',
  'TypeScript Patterns': 'https://www.coursera.org/learn/learn-typescript',
  'SQL Joins & Aggregations': 'https://www.coursera.org/specializations/sql-data-analysis-business-insights',
  'Dashboard Storytelling': 'https://www.coursera.org/learn/dlai-data-storytelling',
  'Exploratory Analysis': 'https://www.coursera.org/projects/exploratory-data-analysis-python-pandas/',
  'CI/CD Pipelines': 'https://www.coursera.org/specializations/devops-linux-docker-kubernetes-ci-cd-iac',
  'Infrastructure as Code': 'https://www.coursera.org/specializations/devops-linux-docker-kubernetes-ci-cd-iac',
  'Kubernetes Operations': 'https://www.coursera.org/specializations/devops-linux-docker-kubernetes-ci-cd-iac',
};

const buildCourseraCourseUrl = (skill: string, goal: string, levelLabel: string) => {
  const query = encodeURIComponent(`${skill} ${goal} ${levelLabel}`);
  return courseLinksBySkill[skill] || `https://www.coursera.org/search?query=${query}&productTypeDescription=Courses`;
};

const youtubeVideoIdsBySkill: Record<string, string> = {
  'Vector Databases': 'klTvEwg3oJ4',
  'Embeddings & Transformers': 'wjZofJX0v4M',
  'RAG Pipeline Architecture': 'T-D1OfcDW1M',
  'React State Management': 'bMknfKXIFA8',
  'Responsive UI Systems': 'srvUrASNj0s',
  'TypeScript Patterns': 'BwuLxPH8IDs',
  'SQL Joins & Aggregations': 'HXV3zeQKqGY',
  'Dashboard Storytelling': 'fSgEeI2Xpdc',
  'Exploratory Analysis': 'vmEHCJofslg',
  'CI/CD Pipelines': 'R8_veQiYBjI',
  'Infrastructure as Code': 'SLB_c_ayRMo',
  'Kubernetes Operations': 'X48VuDVv0do',
};

const buildPlayableYoutubeUrl = (skill: string) => {
  const videoId = youtubeVideoIdsBySkill[skill] || 'rfscVS0vtbw';
  return `https://www.youtube.com/watch?v=${videoId}&autoplay=1`;
};

const buildProfileRecommendations = (profile: {
  target_goal: string;
  current_skills: string;
  budget: string;
  learner_level: string;
}) => {
  const goal = profile.target_goal || 'Production RAG Engineer';
  const focusSkills = getRecommendationFocus(goal, profile.current_skills);
  const levelLabel = profile.learner_level === 'BEGINNER' ? 'beginner' : profile.learner_level === 'ADVANCED' ? 'advanced' : 'intermediate';
  const isFree = profile.budget === 'FREE';

  const youtube = focusSkills.map((skill, index) => {
    return {
      title: `${skill} tutorial for ${goal}`,
      source: index === 0 ? 'YouTube Learning' : index === 1 ? 'Project walkthrough' : 'Concept deep dive',
      match: 96 - index * 5,
      url: buildPlayableYoutubeUrl(skill),
    };
  });

  const courses = focusSkills.map((skill, index) => {
    return {
      title: `${skill}: ${levelLabel} course path`,
      provider: isFree ? 'Coursera audit' : 'Coursera',
      cost: isFree ? 'FREE' : profile.budget,
      match: 94 - index * 4,
      url: buildCourseraCourseUrl(skill, goal, levelLabel),
    };
  });

  return { focusSkills, youtube, courses };
};

export default function ChatProfiler() {
  const {
    profile,
    setProfile,
    setIsComplete,
    chats,
    currentChatId,
    setCurrentChatId,
    createNewChat,
    deleteChat,
    updateCurrentChatTitle,
    completedSkills,
  } = useChatContext();
  const navigate = useNavigate();
  const userEmail = localStorage.getItem('userEmail') || 'ADMIN@SKILLROUTE.COM';
  const currentProfile = profile || emptyProfile;

  const [form, setForm] = useState({
    title: 'Untitled Profile',
    target_goal: '',
    current_skills: '',
    budget: 'FREE',
    time_commitment: '',
    deadline: '',
    learner_level: 'INTERMEDIATE',
  });

  useEffect(() => {
    const activeChat = chats.find((chat: any) => chat.id === currentChatId);
    setForm({
      title: activeChat?.title || currentProfile.target_goal || 'Untitled Profile',
      target_goal: currentProfile.target_goal || '',
      current_skills: currentProfile.current_skills?.join(', ') || '',
      budget: currentProfile.budget || 'FREE',
      time_commitment: currentProfile.time_commitment || '',
      deadline: currentProfile.deadline || '',
      learner_level: currentProfile.learner_level || 'INTERMEDIATE',
    });
  }, [chats, currentChatId, currentProfile]);

  const profileCompletion = useMemo(() => {
    const fields = [
      currentProfile.target_goal,
      currentProfile.current_skills?.length,
      currentProfile.budget,
      currentProfile.time_commitment,
      currentProfile.deadline,
      currentProfile.learner_level,
    ];
    return Math.round((fields.filter(Boolean).length / fields.length) * 100);
  }, [currentProfile]);

  const draftRecommendations = useMemo(() => buildProfileRecommendations({
    target_goal: form.target_goal,
    current_skills: form.current_skills,
    budget: form.budget,
    learner_level: form.learner_level,
  }), [form]);

  const savedProfiles = chats.map((chat: any) => ({
    ...chat,
    label: chat.title || chat.profile?.target_goal || 'Untitled Profile',
    goal: chat.profile?.target_goal || 'Goal not set',
    skills: chat.profile?.current_skills || [],
    level: chat.profile?.learner_level || 'Not set',
    completedCount: chat.completedSkills?.length || 0,
  }));

  const handleSave = () => {
    const nextProfile = {
      target_goal: form.target_goal.trim(),
      current_skills: form.current_skills
        .split(',')
        .map(skill => skill.trim())
        .filter(Boolean),
      budget: form.budget,
      time_commitment: form.time_commitment.trim(),
      deadline: form.deadline.trim(),
      learner_level: form.learner_level,
    };

    const title = form.title.trim() || nextProfile.target_goal || 'Untitled Profile';
    updateCurrentChatTitle(title);
    setProfile(nextProfile);
    setIsComplete(Boolean(nextProfile.target_goal && nextProfile.current_skills.length));
  };

  const handleTemplate = (template: typeof profileTemplates[number]) => {
    setForm({
      title: template.name,
      target_goal: template.profile.target_goal,
      current_skills: template.profile.current_skills.join(', '),
      budget: template.profile.budget,
      time_commitment: template.profile.time_commitment,
      deadline: template.profile.deadline,
      learner_level: template.profile.learner_level,
    });
  };

  const handleDelete = (chatId: number) => {
    deleteChat(chatId);
  };

  const handleOpenDashboard = () => {
    handleSave();
    navigate('/dashboard');
  };

  return (
    <div className="h-screen overflow-hidden bg-slate-50 font-sans text-slate-700">
      <div className="flex h-full">
        <aside className="flex w-72 flex-shrink-0 flex-col border-r border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 p-5">
            <div className="mb-1 flex items-center gap-2">
              <div className="rounded-lg bg-teal-600 p-2 text-white">
                <Compass className="h-5 w-5" />
              </div>
              <div>
                <div className="text-lg font-black tracking-tight text-slate-950">SkillRoute</div>
                <div className="text-xs font-medium text-slate-500">Profile Studio</div>
              </div>
            </div>
          </div>

          <div className="border-b border-slate-100 p-3">
            <RouteNav compact />
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Learner Profiles</div>
                <div className="mt-1 text-[11px] font-semibold text-slate-500">{savedProfiles.length} saved - toggle active or delete</div>
              </div>
              <button
                type="button"
                onClick={createNewChat}
                className="rounded-lg border border-teal-100 bg-teal-50 p-2 text-teal-700 transition-colors hover:bg-teal-100"
                title="Create profile"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-2">
              {savedProfiles.map((chat: any) => {
                const isActive = chat.id === currentChatId;
                return (
                  <div
                    key={chat.id}
                    className={`group rounded-lg border p-3 transition-all ${
                      isActive ? 'border-teal-200 bg-teal-50 shadow-sm' : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() => setCurrentChatId(chat.id)}
                      className="w-full text-left"
                    >
                      <div className="flex items-start gap-3">
                        <div className={`rounded-lg p-2 ${isActive ? 'bg-white text-teal-700' : 'bg-slate-50 text-slate-500'}`}>
                          <UserRound className="h-4 w-4" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="truncate text-sm font-black text-slate-900">{chat.label}</div>
                          <div className="mt-1 truncate text-[11px] font-bold text-teal-700">{chat.goal}</div>
                          <div className="mt-1 truncate text-[11px] font-medium text-slate-500">{chat.skills.join(', ') || 'No skills added'}</div>
                        </div>
                      </div>
                    </button>
                    <div className="mt-3 flex items-center justify-between">
                      <span className="rounded-full bg-white px-2 py-1 text-[10px] font-bold uppercase text-slate-500">{chat.level}</span>
                      <span className="rounded-full bg-white px-2 py-1 text-[10px] font-bold uppercase text-teal-700">{chat.completedCount} done</span>
                    </div>
                    <div className="mt-3 grid grid-cols-[1fr_auto] gap-2">
                      <button
                        type="button"
                        onClick={() => setCurrentChatId(chat.id)}
                        className={`flex h-9 items-center justify-center gap-2 rounded-lg border text-xs font-black transition-all ${
                          isActive
                            ? 'border-teal-200 bg-white text-teal-700'
                            : 'border-slate-200 bg-slate-50 text-slate-600 hover:border-teal-200 hover:text-teal-700'
                        }`}
                      >
                        {isActive ? <ToggleRight className="h-4 w-4" /> : <ToggleLeft className="h-4 w-4" />}
                        {isActive ? 'Active' : 'Use Profile'}
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(chat.id)}
                        className="flex h-9 w-9 items-center justify-center rounded-lg border border-red-100 bg-red-50 text-red-600 transition-all hover:bg-red-100"
                        title="Delete profile"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="border-t border-slate-100 p-4">
            <div className="flex items-center gap-3 rounded-lg bg-slate-50 p-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-600 text-xs font-black text-white">ME</div>
              <div className="min-w-0">
                <div className="text-sm font-black text-slate-900">My Workspace</div>
                <div className="truncate text-[10px] font-bold uppercase text-slate-400">{userEmail}</div>
              </div>
            </div>
          </div>
        </aside>

        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-6xl px-8 py-7">
            <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="mb-2 flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-teal-700">
                  <Target className="h-4 w-4" />
                  Learner Profile
                </div>
                <h1 className="text-3xl font-black tracking-tight text-slate-950">Build the profile that powers your dashboard</h1>
                <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-600">
                  Select or create a profile, fill in the learning details, then open the dashboard to generate the route from this exact context.
                </p>
              </div>
              <button
                type="button"
                onClick={handleOpenDashboard}
                className="inline-flex items-center gap-2 rounded-lg bg-[#2D6A62] px-5 py-3 text-sm font-black text-white shadow-md transition-all hover:bg-[#21524b] hover:shadow-lg"
              >
                <LayoutDashboard className="h-4 w-4" />
                Open Dashboard
              </button>
            </div>

            <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.2fr_0.8fr]">
              <div className="space-y-5">
              <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-100 p-5">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h2 className="text-lg font-black text-slate-950">Profile Details</h2>
                      <p className="mt-1 text-xs font-medium text-slate-500">These fields sync directly with the dashboard route generator.</p>
                    </div>
                    <button
                      type="button"
                      onClick={handleSave}
                      className="inline-flex items-center gap-2 rounded-lg bg-teal-600 px-4 py-2 text-sm font-black text-white shadow-sm transition-colors hover:bg-teal-700"
                    >
                      <Save className="h-4 w-4" />
                      Save Profile
                    </button>
                  </div>
                </div>

                <div className="grid gap-5 p-5 md:grid-cols-2">
                  <Field label="Profile Name">
                    <input
                      value={form.title}
                      onChange={(e) => setForm(prev => ({ ...prev, title: e.target.value }))}
                      className="profile-input"
                      placeholder="My AI Engineer Plan"
                    />
                  </Field>
                  <Field label="Target Goal">
                    <input
                      value={form.target_goal}
                      onChange={(e) => setForm(prev => ({ ...prev, target_goal: e.target.value }))}
                      className="profile-input"
                      placeholder="Production RAG Engineer"
                    />
                  </Field>
                  <Field label="Current Skills">
                    <textarea
                      value={form.current_skills}
                      onChange={(e) => setForm(prev => ({ ...prev, current_skills: e.target.value }))}
                      className="profile-input min-h-28 resize-none"
                      placeholder="Python, SQL, React"
                    />
                  </Field>
                  <div className="grid gap-5">
                    <Field label="Learner Level">
                      <select
                        value={form.learner_level}
                        onChange={(e) => setForm(prev => ({ ...prev, learner_level: e.target.value }))}
                        className="profile-input"
                      >
                        <option value="BEGINNER">Beginner</option>
                        <option value="INTERMEDIATE">Intermediate</option>
                        <option value="ADVANCED">Advanced</option>
                      </select>
                    </Field>
                    <Field label="Budget">
                      <select
                        value={form.budget}
                        onChange={(e) => setForm(prev => ({ ...prev, budget: e.target.value }))}
                        className="profile-input"
                      >
                        <option value="FREE">Free</option>
                        <option value="LOW">Low</option>
                        <option value="FLEXIBLE">Flexible</option>
                        <option value="PAID">Paid</option>
                      </select>
                    </Field>
                  </div>
                  <Field label="Time Commitment">
                    <input
                      value={form.time_commitment}
                      onChange={(e) => setForm(prev => ({ ...prev, time_commitment: e.target.value }))}
                      className="profile-input"
                      placeholder="8 hrs/wk"
                    />
                  </Field>
                  <Field label="Deadline">
                    <input
                      value={form.deadline}
                      onChange={(e) => setForm(prev => ({ ...prev, deadline: e.target.value }))}
                      className="profile-input"
                      placeholder="~18 weeks"
                    />
                  </Field>
                </div>

                <div className="border-t border-slate-100 p-5">
                  <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                    <CopyPlus className="h-3.5 w-3.5" />
                    Quick Starts
                  </div>
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                    {profileTemplates.map(template => (
                      <button
                        key={template.name}
                        type="button"
                        onClick={() => handleTemplate(template)}
                        className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-left transition-all hover:border-teal-200 hover:bg-teal-50"
                      >
                        <div className="text-sm font-black text-slate-900">{template.name}</div>
                        <div className="mt-1 text-[11px] font-medium text-slate-500">{template.profile.time_commitment} - {template.profile.deadline}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </section>

              <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-100 p-5">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h2 className="text-lg font-black text-slate-950">Profile Recommendations</h2>
                      <p className="mt-1 text-xs font-medium text-slate-500">Live video and course suggestions generated from this profile before you open the map.</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {draftRecommendations.focusSkills.map(skill => (
                        <span key={skill} className="rounded-full bg-slate-100 px-3 py-1 text-[10px] font-bold uppercase tracking-wide text-slate-500">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="grid gap-5 p-5 lg:grid-cols-2">
                  <div>
                    <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-red-600">
                      <PlaySquare className="h-4 w-4" />
                      YouTube Recommender
                    </div>
                    <div className="space-y-3">
                      {draftRecommendations.youtube.map(video => (
                        <RecommendationCard
                          key={video.title}
                          title={video.title}
                          subtitle={video.source}
                          badge={`${video.match}% match`}
                          url={video.url}
                          accent="red"
                        />
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-blue-600">
                      <BookOpen className="h-4 w-4" />
                      Course Recommender
                    </div>
                    <div className="space-y-3">
                      {draftRecommendations.courses.map(course => (
                        <RecommendationCard
                          key={course.title}
                          title={course.title}
                          subtitle={`${course.provider} - ${course.cost}`}
                          badge={`${course.match}% match`}
                          url={course.url}
                          accent="blue"
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </section>
              </div>

              <aside className="space-y-5">
                <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
                  <div className="mb-4 flex items-center justify-between">
                    <div>
                      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Dashboard Sync</div>
                      <h2 className="mt-1 text-lg font-black text-slate-950">Active profile</h2>
                    </div>
                    <div className="relative h-16 w-16 rounded-full bg-slate-100">
                      <div
                        className="absolute inset-0 rounded-full"
                        style={{ background: `conic-gradient(#0d9488 ${profileCompletion * 3.6}deg, #e2e8f0 0deg)` }}
                      />
                      <div className="absolute inset-2 flex items-center justify-center rounded-full bg-white text-sm font-black text-slate-900">
                        {profileCompletion}%
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <SummaryField icon={Target} label="Goal" value={currentProfile.target_goal || 'Not set'} />
                    <SummaryField icon={UserRound} label="Skills" value={currentProfile.current_skills?.join(', ') || 'Not set'} />
                    <SummaryField icon={WalletCards} label="Budget" value={currentProfile.budget || 'Not set'} />
                    <SummaryField icon={Clock} label="Pace" value={currentProfile.time_commitment || 'Not set'} />
                  </div>
                </section>

                <section className="rounded-lg border border-teal-100 bg-teal-50 p-5 shadow-sm">
                  <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-teal-700">
                    <CheckCircle className="h-4 w-4" />
                    Current Route State
                  </div>
                  <div className="text-2xl font-black text-slate-950">{completedSkills.length} completed skills</div>
                  <p className="mt-2 text-xs leading-relaxed text-slate-600">
                    Progress stays attached to this profile. Switch profiles on the left to see a different dashboard context.
                  </p>
                  <button
                    type="button"
                    onClick={handleOpenDashboard}
                    className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-black text-teal-700 shadow-sm transition-all hover:bg-teal-100"
                  >
                    Generate route
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </section>
              </aside>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

const Field = ({ label, children }: { label: string; children: ReactNode }) => (
  <label className="block">
    <span className="mb-2 block text-[10px] font-bold uppercase tracking-widest text-slate-500">{label}</span>
    {children}
  </label>
);

const SummaryField = ({ icon: Icon, label, value }: { icon: any; label: string; value: string }) => (
  <div className="flex items-start gap-3 rounded-lg border border-slate-100 bg-slate-50 p-3">
    <div className="rounded-lg bg-white p-2 text-teal-700">
      <Icon className="h-4 w-4" />
    </div>
    <div className="min-w-0">
      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">{label}</div>
      <div className="mt-1 text-sm font-bold text-slate-900">{value}</div>
    </div>
  </div>
);

const RecommendationCard = ({
  title,
  subtitle,
  badge,
  url,
  accent,
}: {
  title: string;
  subtitle: string;
  badge: string;
  url: string;
  accent: 'red' | 'blue';
}) => {
  const accentClass = accent === 'red'
    ? 'bg-red-50 text-red-700 border-red-100 hover:border-red-200'
    : 'bg-blue-50 text-blue-700 border-blue-100 hover:border-blue-200';

  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className={`group flex items-start justify-between gap-4 rounded-lg border bg-white p-4 shadow-sm transition-all hover:shadow-md ${accentClass}`}
    >
      <div className="min-w-0">
        <div className="line-clamp-2 text-sm font-black text-slate-900">{title}</div>
        <div className="mt-1 text-xs font-semibold text-slate-500">{subtitle}</div>
        <div className="mt-3 inline-flex rounded-full bg-white px-2.5 py-1 text-[10px] font-black uppercase tracking-wide text-slate-500 shadow-sm">
          {badge}
        </div>
      </div>
      <ExternalLink className="mt-0.5 h-4 w-4 flex-shrink-0 transition-transform group-hover:translate-x-0.5" />
    </a>
  );
};

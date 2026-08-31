import React, { createContext, useContext, useState, useEffect } from 'react';

const ChatContext = createContext<any>(null);
const PROFILE_SEED_KEY = 'skillroute_default_profiles_seeded_v2';

const defaultProfiles = [
  {
    id: 101,
    title: 'RAG Engineer',
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
    id: 102,
    title: 'Frontend Engineer',
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
    id: 103,
    title: 'Data Analyst',
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
    id: 104,
    title: 'Cloud DevOps Engineer',
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

const buildDefaultChats = (defaultMessage: any) => (
  defaultProfiles.map(profile => ({
    ...profile,
    messages: [defaultMessage],
    isComplete: true,
    completedSkills: [],
  }))
);

const seedMissingDefaultProfiles = (chats: any[], defaultMessage: any) => {
  if (localStorage.getItem(PROFILE_SEED_KEY) === 'true') {
    return chats;
  }

  const nextChats = [...chats];
  const existingGoals = new Set(nextChats.map(chat => chat.profile?.target_goal || chat.title));
  buildDefaultChats(defaultMessage).forEach(profile => {
    if (!existingGoals.has(profile.profile.target_goal) && !existingGoals.has(profile.title)) {
      nextChats.push(profile);
    }
  });
  localStorage.setItem(PROFILE_SEED_KEY, 'true');
  return nextChats;
};

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
  const defaultMessage = { role: 'ai', content: "Hi! I'm your AI Learning Coach. To build your personalized learning map, tell me: what is your target goal?" };
  
  const [chats, setChats] = useState<any[]>(() => {
    const saved = localStorage.getItem('skillroute_chats');
    if (!saved) {
      localStorage.setItem(PROFILE_SEED_KEY, 'true');
      return buildDefaultChats(defaultMessage);
    }

    try {
      const savedChats = JSON.parse(saved);
      return savedChats.length > 0 ? seedMissingDefaultProfiles(savedChats, defaultMessage) : buildDefaultChats(defaultMessage);
    } catch {
      localStorage.setItem(PROFILE_SEED_KEY, 'true');
      return buildDefaultChats(defaultMessage);
    }
  });
  
  const [currentChatId, setCurrentChatId] = useState<number>(() => {
    const saved = localStorage.getItem('skillroute_current_chat_id');
    return saved ? parseInt(saved, 10) : 101;
  });

  useEffect(() => {
    localStorage.setItem('skillroute_chats', JSON.stringify(chats));
  }, [chats]);

  useEffect(() => {
    localStorage.setItem('skillroute_current_chat_id', currentChatId.toString());
  }, [currentChatId]);

  const currentChat = chats.find(c => c.id === currentChatId) || chats[0];

  useEffect(() => {
    if (chats.length > 0 && !chats.some(c => c.id === currentChatId)) {
      setCurrentChatId(chats[0].id);
    }
  }, [chats, currentChatId]);

  const setMessages = (newMessages: any) => {
    setChats(prevChats => prevChats.map(c => {
      if (c.id !== currentChatId) return c;
      const messagesArray = typeof newMessages === 'function' ? newMessages(c.messages) : newMessages;
      return { 
        ...c, 
        messages: messagesArray, 
        title: messagesArray.length > 1 ? messagesArray[1].content.substring(0, 30) + '...' : c.title 
      };
    }));
  };

  const setProfile = (newProfile: any) => {
    setChats(prevChats => prevChats.map(c => c.id === currentChatId ? { ...c, profile: newProfile } : c));
  };

  const setIsComplete = (complete: boolean) => {
    setChats(prevChats => prevChats.map(c => c.id === currentChatId ? { ...c, isComplete: complete } : c));
  };

  const createNewChat = () => {
    const newId = Date.now();
    setChats(prev => [...prev, { id: newId, title: 'Untitled Profile', messages: [defaultMessage], profile: null, isComplete: false, completedSkills: [] }]);
    setCurrentChatId(newId);
  };

  const deleteChat = (chatId: number) => {
    setChats(prevChats => {
      if (prevChats.length <= 1) {
        const resetChat = { id: Date.now(), title: 'Untitled Profile', messages: [defaultMessage], profile: null, isComplete: false, completedSkills: [] };
        setCurrentChatId(resetChat.id);
        return [resetChat];
      }

      const nextChats = prevChats.filter(c => c.id !== chatId);
      if (chatId === currentChatId) {
        setCurrentChatId(nextChats[0].id);
      }
      return nextChats;
    });
  };

  const updateCurrentChatTitle = (title: string) => {
    setChats(prevChats => prevChats.map(c => c.id === currentChatId ? { ...c, title } : c));
  };

  const markComplete = (skillId: number) => {
    setChats(prevChats => prevChats.map(c => {
      if (c.id === currentChatId) {
        const skills = c.completedSkills || [];
        if (!skills.includes(skillId)) {
          return { ...c, completedSkills: [...skills, skillId] };
        }
      }
      return c;
    }));
  };

  const markIncomplete = (skillId: number) => {
    setChats(prevChats => prevChats.map(c => {
      if (c.id === currentChatId) {
        const skills = c.completedSkills || [];
        return { ...c, completedSkills: skills.filter((id: number) => id !== skillId) };
      }
      return c;
    }));
  };

  return (
    <ChatContext.Provider value={{
      messages: currentChat.messages, setMessages,
      profile: currentChat.profile, setProfile,
      isComplete: currentChat.isComplete, setIsComplete,
      chats, currentChatId, setCurrentChatId, createNewChat, deleteChat, updateCurrentChatTitle,
      completedSkills: currentChat.completedSkills || [], markComplete, markIncomplete
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => useContext(ChatContext);

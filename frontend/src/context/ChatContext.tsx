import React, { createContext, useContext, useState, useEffect } from 'react';

const ChatContext = createContext<any>(null);

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
  const defaultMessage = { role: 'ai', content: "Hi! I'm your AI Learning Coach. To build your personalized learning map, tell me: what is your target goal?" };
  
  const [chats, setChats] = useState<any[]>(() => {
    const saved = localStorage.getItem('skillroute_chats');
    return saved ? JSON.parse(saved) : [{ id: 1, title: 'New Goal Discovery', messages: [defaultMessage], profile: null, isComplete: false }];
  });
  
  const [currentChatId, setCurrentChatId] = useState<number>(() => {
    const saved = localStorage.getItem('skillroute_current_chat_id');
    return saved ? parseInt(saved, 10) : 1;
  });

  useEffect(() => {
    localStorage.setItem('skillroute_chats', JSON.stringify(chats));
  }, [chats]);

  useEffect(() => {
    localStorage.setItem('skillroute_current_chat_id', currentChatId.toString());
  }, [currentChatId]);

  const currentChat = chats.find(c => c.id === currentChatId) || chats[0];

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
    setChats(prev => [...prev, { id: newId, title: 'New Goal Discovery', messages: [defaultMessage], profile: null, isComplete: false }]);
    setCurrentChatId(newId);
  };

  return (
    <ChatContext.Provider value={{
      messages: currentChat.messages, setMessages,
      profile: currentChat.profile, setProfile,
      isComplete: currentChat.isComplete, setIsComplete,
      chats, currentChatId, setCurrentChatId, createNewChat
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => useContext(ChatContext);

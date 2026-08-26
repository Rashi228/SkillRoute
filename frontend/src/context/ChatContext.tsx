import React, { createContext, useContext, useState } from 'react';

const ChatContext = createContext<any>(null);

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
  const [messages, setMessages] = useState([
    { role: 'ai', content: "Hi! I'm your AI Learning Coach. To build your personalized learning map, tell me: what is your target goal?" }
  ]);
  const [profile, setProfile] = useState<any>(null);
  const [isComplete, setIsComplete] = useState(false);

  return (
    <ChatContext.Provider value={{
      messages, setMessages,
      profile, setProfile,
      isComplete, setIsComplete
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => useContext(ChatContext);

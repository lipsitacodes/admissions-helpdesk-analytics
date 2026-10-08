import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { ChatArea } from "./ChatArea";
import { Composer } from "./Composer";
import { AuthModal } from "./AuthModal";

export function AppShell({
  theme,
  onToggleTheme,
  sidebarOpen,
  setSidebarOpen,
  onNewConversation,
  chats,
  activeChatId,
  onSelectChat,
  onDeleteChat,
  onSelectTopic,
  messages,
  isBusy,
  input,
  setInput,
  onSubmit,
  errorMessage,
  candidateName,
  setCandidateName,
  authOpen,
  setAuthOpen,
  citationEnabled,
  setCitationEnabled,
  onNavigateLanding,
  targetLanguage,
  setTargetLanguage,
  onLogout,
}) {
  const chatContainerRef = useRef(null);
  const prevMessagesCount = useRef(messages.length);

  useEffect(() => {
    if (chatContainerRef.current) {
      const wasEmpty = prevMessagesCount.current === 0;
      const isEmpty = messages.length === 0;
      if (wasEmpty !== isEmpty) {
        gsap.fromTo(
          chatContainerRef.current,
          { opacity: 0, y: 10 },
          { opacity: 1, y: 0, duration: 0.4, ease: "power2.out", clearProps: "all" }
        );
      }
    }
    prevMessagesCount.current = messages.length;
  }, [messages.length]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-light-bg dark:bg-dark-bg text-light-text dark:text-dark-text transition-colors duration-300">
      {/* Sidebar Rail / Navigation */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        onNewConversation={onNewConversation}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={onSelectChat}
        onDeleteChat={onDeleteChat}
        onSelectTopic={onSelectTopic}
        onOpenAuth={() => setAuthOpen(true)}
        candidateName={candidateName}
        onNavigateLanding={onNavigateLanding}
        onLogout={onLogout}
      />

      {/* Main Intelligent Workspace */}
      <div className="flex-1 flex flex-col h-full min-h-0 min-w-0 overflow-hidden relative">
        {/* Top Bar with Language Dropdown & Logo */}
        <TopBar
          onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
          sidebarOpen={sidebarOpen}
          theme={theme}
          onToggleTheme={onToggleTheme}
          onNewConversation={onNewConversation}
          candidateName={candidateName}
          onOpenAuth={() => setAuthOpen(true)}
          targetLanguage={targetLanguage}
          setTargetLanguage={setTargetLanguage}
          onNavigateLanding={onNavigateLanding}
          onLogout={onLogout}
        />

        {/* Chat Area & Composer: Clean empty state or active conversation with GSAP fade */}
        <div ref={chatContainerRef} className="flex-1 flex flex-col h-full min-h-0 min-w-0 overflow-hidden">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center px-4 py-8 overflow-y-auto">
              <div className="w-full max-w-3xl">
                <Composer
                  input={input}
                  setInput={setInput}
                  onSubmit={onSubmit}
                  isBusy={isBusy}
                  errorMessage={errorMessage}
                  citationEnabled={citationEnabled}
                  setCitationEnabled={setCitationEnabled}
                  targetLanguage={targetLanguage}
                  setTargetLanguage={setTargetLanguage}
                />
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col h-full min-h-0 overflow-hidden">
              <ChatArea
                messages={messages}
                isBusy={isBusy}
                onSelectPrompt={(prompt) => onSelectTopic(prompt)}
                candidateName={candidateName}
                theme={theme}
                citationEnabled={citationEnabled}
              />

              <Composer
                input={input}
                setInput={setInput}
                onSubmit={onSubmit}
                isBusy={isBusy}
                errorMessage={errorMessage}
                citationEnabled={citationEnabled}
                setCitationEnabled={setCitationEnabled}
                targetLanguage={targetLanguage}
                setTargetLanguage={setTargetLanguage}
              />
            </div>
          )}
        </div>
      </div>

      {/* Motivating Candidate Auth Modal (Reference Image 4) */}
      <AuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        candidateName={candidateName}
        onSaveCandidate={(name) => {
          setCandidateName(name);
          localStorage.setItem("campus_ai_candidate_name", name);
        }}
      />
    </div>
  );
}

export default AppShell;

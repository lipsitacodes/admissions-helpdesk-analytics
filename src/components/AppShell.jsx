import React from "react";
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
  selectedCampus,
  setSelectedCampus,
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
}) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-light-bg dark:bg-dark-bg text-light-text dark:text-dark-text transition-colors duration-300">
      {/* Sidebar Rail / Navigation */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        selectedCampus={selectedCampus}
        setSelectedCampus={setSelectedCampus}
        onNewConversation={onNewConversation}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={onSelectChat}
        onDeleteChat={onDeleteChat}
        onSelectTopic={onSelectTopic}
        onOpenAuth={() => setAuthOpen(true)}
        candidateName={candidateName}
        onNavigateLanding={onNavigateLanding}
      />

      {/* Main Intelligent Workspace */}
      <div className="flex-1 flex flex-col h-full min-h-0 min-w-0 overflow-hidden relative">
        {/* Top Bar matching Image 1 & 3 */}
        <TopBar
          onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
          sidebarOpen={sidebarOpen}
          theme={theme}
          onToggleTheme={onToggleTheme}
          onNewConversation={onNewConversation}
          candidateName={candidateName}
          onOpenAuth={() => setAuthOpen(true)}
        />

        {/* Conversation Stream & Hero */}
        <ChatArea
          messages={messages}
          isBusy={isBusy}
          onSelectPrompt={(prompt) => onSelectTopic(prompt)}
          candidateName={candidateName}
          theme={theme}
          citationEnabled={citationEnabled}
        />

        {/* Floating Neon-Aura Composer */}
        <Composer
          input={input}
          setInput={setInput}
          onSubmit={onSubmit}
          isBusy={isBusy}
          errorMessage={errorMessage}
          selectedCampus={selectedCampus}
          setSelectedCampus={setSelectedCampus}
          citationEnabled={citationEnabled}
          setCitationEnabled={setCitationEnabled}
        />
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

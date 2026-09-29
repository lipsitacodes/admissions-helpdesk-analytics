import React, { useState } from "react";
import {
  Plus,
  Menu,
  GraduationCap,
  IndianRupee,
  Award,
  Building2,
  FileText,
  BadgeCheck,
  FolderKanban,
  MessageSquare,
  PhoneCall,
  X,
  ChevronRight,
} from "lucide-react";
import { HugeiconsIcon } from "@hugeicons/react";
import { Delete02Icon } from "@hugeicons/core-free-icons";
import { CampusSelector } from "./CampusSelector";
import { OrbLogo } from "./OrbLogo";
import SwipeRow from "./SwipeRow";

const EXPLORE_TOPICS = [
  { label: "B.Tech CSE Fees", query: "What is the fee for B.Tech CSE?", icon: IndianRupee, badge: "Popular" },
  { label: "CUEE 2026 Process", query: "What is CUEE 2026 admission process?", icon: GraduationCap, badge: "Exam" },
  { label: "Amrit Kaal Scholarships", query: "What is the Amrit Kaal Scholarship for B.Tech?", icon: Award, badge: "Merit" },
  { label: "Hostel & Living", query: "What are the hostel facilities and fee structure?", icon: Building2, badge: null },
  { label: "Eligibility & Cutoffs", query: "What is the eligibility criteria for B.Tech engineering?", icon: BadgeCheck, badge: null },
  { label: "First Year Other Fees", query: "What is the first year other fee breakup?", icon: FileText, badge: "25k" },
];

const WORKSPACES = [
  { name: "School of Engineering", query: "Tell me about School of Engineering programs and fees" },
  { name: "School of Management", query: "What are MBA and BBA fees and admission process?" },
  { name: "School of Agriculture", query: "What is B.Sc Agriculture eligibility and fee structure?" },
  { name: "Allied Health Sciences", query: "What allied health programs and diplomas are available?" },
];

// Group chats by relative date label (ChatGPT-style)
function groupChatsByDate(chats) {
  const groups = { Today: [], Yesterday: [], "Previous 7 Days": [], "Previous 30 Days": [], Older: [] };
  if (!Array.isArray(chats)) return groups;

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today); yesterday.setDate(today.getDate() - 1);
  const sevenDaysAgo = new Date(today); sevenDaysAgo.setDate(today.getDate() - 7);
  const thirtyDaysAgo = new Date(today); thirtyDaysAgo.setDate(today.getDate() - 30);

  chats.forEach((chat) => {
    if (!chat || !chat.id) return;
    const d = new Date(chat.createdAt || Date.now());
    const day = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    if (day >= today) groups["Today"].push(chat);
    else if (day >= yesterday) groups["Yesterday"].push(chat);
    else if (day >= sevenDaysAgo) groups["Previous 7 Days"].push(chat);
    else if (day >= thirtyDaysAgo) groups["Previous 30 Days"].push(chat);
    else groups["Older"].push(chat);
  });

  return groups;
}

export function Sidebar({
  sidebarOpen,
  setSidebarOpen,
  onToggleSidebar,
  selectedCampus,
  setSelectedCampus,
  onNewConversation,
  chats = [],
  activeChatId,
  onSelectChat,
  onDeleteChat,
  onSelectTopic,
  onOpenAuth,
  candidateName,
  onNavigateLanding,
}) {
  const groupedChats = groupChatsByDate(chats);
  const hasHistory = chats.length > 0;

  // Detect dark mode for SwipeRow colors
  const isDark = document.documentElement.classList.contains("dark");
  const rowBg = isDark ? "#181818" : "#f4f4f5";
  const rowText = isDark ? "#ffffff" : "#000000";
  const drawerBg = isDark ? "#262626" : "#e4e4e7";

  return (
    <>
      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/80 backdrop-blur-sm lg:hidden transition-opacity"
          aria-hidden="true"
        />
      )}

      {/* Main Sidebar Navigation Panel */}
      <aside
        id="sidebar"
        className={`fixed lg:static top-0 bottom-0 left-0 z-50 flex flex-col justify-between border-r border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface transition-all duration-300 ease-in-out ${
          sidebarOpen ? "w-72 translate-x-0 opacity-100" : "-translate-x-full lg:translate-x-0 lg:w-0 lg:opacity-0 lg:overflow-hidden lg:border-r-0"
        }`}
      >
        {/* Header: Brand & New Chat */}
        <div className="p-4 border-b border-light-border dark:border-dark-border">
          <div className="flex items-center justify-between mb-4">
            <button
              type="button"
              onClick={onNavigateLanding}
              title="Return to Landing Page"
              className="orb-btn flex items-center gap-2.5 cursor-pointer transition-transform duration-150 text-left group hover:opacity-90"
            >
              <OrbLogo size="sm" animated={true} />
              <div>
                <h1 className="text-sm font-bold text-light-text dark:text-dark-text tracking-tight flex items-center gap-1.5 transition-colors" style={{ fontFamily: "'DM Serif Display', serif" }}>
                  <span>AskCampus</span>
                </h1>
                <p className="text-[11px] text-light-muted dark:text-dark-muted">
                  Admissions Intelligence
                </p>
              </div>
            </button>
            <button
              type="button"
              onClick={onToggleSidebar || (() => setSidebarOpen(false))}
              className="p-1.5 rounded-lg text-light-muted dark:text-dark-muted hover:text-light-text dark:hover:text-dark-text hover:bg-light-surface2 dark:hover:bg-dark-surface2 transition-colors"
              aria-label="Toggle sidebar"
              title="Toggle sidebar"
            >
              <Menu className="w-4 h-4 hidden lg:block" />
              <X className="w-5 h-5 lg:hidden" />
            </button>
          </div>

          {/* New Chat button */}
          <button
            type="button"
            onClick={() => { onNewConversation(); setSidebarOpen(false); }}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-light-surface2 dark:bg-dark-surface2 border border-light-border dark:border-dark-border hover:bg-light-border dark:hover:bg-dark-surface3 text-light-text dark:text-dark-text font-semibold text-xs shadow-sm active:scale-[0.99] transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Scrollable Navigation Items */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {/* Campus Selector */}
          <CampusSelector selectedCampus={selectedCampus} onSelectCampus={setSelectedCampus} />

          {/* ChatGPT-style Chat History with SwipeRow */}
          {hasHistory && (
            <div className="space-y-1">
              <div className="text-[11px] font-bold tracking-wider text-light-muted dark:text-dark-muted uppercase px-1 mb-2">
                History
              </div>
              {Object.entries(groupedChats).map(([label, items]) => {
                if (items.length === 0) return null;
                return (
                  <div key={label} className="mb-3">
                    <p className="text-[10px] font-semibold text-light-muted dark:text-dark-muted px-1 py-1 uppercase tracking-wider opacity-60">
                      {label}
                    </p>
                    <div className="space-y-1">
                      {items.map((chat) => {
                        const isActive = chat.id === activeChatId;
                        return (
                          <SwipeRow
                            key={chat.id}
                            label={chat.title}
                            height={36}
                            radius={10}
                            actionWidth={72}
                            direction="left"
                            rowColor={isActive ? "var(--history-row-active)" : "var(--history-row-bg)"}
                            textColor="var(--history-row-text)"
                            drawerColor="var(--history-drawer)"
                            actionColor="#ef4444"
                            commitAt={0.55}
                            collapseMs={220}
                            fullSwipe={true}
                            actions={[
                              {
                                id: "delete",
                                label: "Delete",
                                icon: <HugeiconsIcon icon={Delete02Icon} size={16} strokeWidth={2} />,
                              },
                            ]}
                            onCommit={() => onDeleteChat(chat.id)}
                            style={{ marginBottom: 2 }}
                            className={`transition-colors rounded-xl border ${
                              isActive
                                ? "border-light-borderLight dark:border-dark-borderLight shadow-sm"
                                : "border-transparent hover:border-light-border/40 dark:hover:border-dark-border/40"
                            }`}
                          >
                            <button
                              type="button"
                              onClick={() => onSelectChat(chat.id)}
                              className="flex-1 flex items-center gap-2 text-xs text-left min-w-0 bg-transparent border-0 cursor-pointer p-0 text-light-text dark:text-dark-text"
                              title={chat.title}
                            >
                              <MessageSquare
                                className={`w-3.5 h-3.5 shrink-0 text-light-text dark:text-dark-text ${
                                  isActive ? "opacity-100" : "opacity-50"
                                }`}
                              />
                              <span
                                className={`truncate text-light-text dark:text-dark-text ${
                                  isActive ? "font-semibold opacity-100" : "font-normal opacity-80"
                                }`}
                              >
                                {chat.title}
                              </span>
                            </button>
                          </SwipeRow>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Features / Quick Topics */}
          <div className="space-y-1.5">
            <div className="text-[11px] font-bold tracking-wider text-light-muted dark:text-dark-muted uppercase px-1">
              Features
            </div>
            <div className="space-y-0.5">
              {EXPLORE_TOPICS.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.label}
                    type="button"
                    onClick={() => { onSelectTopic(item.query); setSidebarOpen(false); }}
                    className="w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded-xl text-left text-light-text dark:text-dark-text hover:bg-light-surface2 dark:hover:bg-dark-surface2 transition-colors group"
                  >
                    <div className="flex items-center gap-2.5 truncate">
                      <Icon className="w-3.5 h-3.5 text-light-muted dark:text-dark-muted group-hover:text-light-text dark:group-hover:text-dark-text shrink-0" />
                      <span className="truncate">{item.label}</span>
                    </div>
                    {item.badge && (
                      <span className="text-[9px] px-1.5 py-0.2 rounded border border-light-border dark:border-dark-border text-light-muted dark:text-dark-muted font-mono">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Academic Workspaces */}
          <div className="space-y-1.5">
            <div className="text-[11px] font-bold tracking-wider text-light-muted dark:text-dark-muted uppercase px-1">
              Workspaces
            </div>
            <div className="space-y-0.5">
              {WORKSPACES.map((ws, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => { onSelectTopic(ws.query); setSidebarOpen(false); }}
                  className="w-full flex items-center justify-between px-3 py-1.5 text-xs text-light-muted dark:text-dark-muted hover:text-light-text dark:hover:text-dark-text hover:bg-light-surface2 dark:hover:bg-dark-surface2 rounded-lg text-left transition-colors"
                >
                  <div className="flex items-center gap-2 truncate">
                    <FolderKanban className="w-3.5 h-3.5 opacity-60 shrink-0" />
                    <span className="truncate">{ws.name}</span>
                  </div>
                  <ChevronRight className="w-3 h-3 opacity-40" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Helpdesk Card (Transparent seamless transition) */}
        <div className="p-4 border-t border-transparent bg-transparent">
          <div className="p-3.5 rounded-2xl glass-card border border-light-border/60 dark:border-dark-border/60 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-light-text dark:text-dark-text">Admissions Helpdesk</span>
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
            </div>
            <p className="text-[11px] text-light-muted dark:text-dark-muted leading-tight">
              Official candidate counseling & offline verification support.
            </p>
            <a
              href="tel:8260077222"
              className="w-full py-2 px-3 rounded-xl bg-light-surface dark:bg-dark-surface text-light-text dark:text-dark-text border border-light-border dark:border-dark-border hover:bg-light-surface2 dark:hover:bg-dark-surface2 font-semibold text-[11px] flex items-center justify-center gap-1.5 transition-all shadow-sm"
            >
              <PhoneCall className="w-3 h-3" />
              <span>Call: 8260077222</span>
            </a>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;

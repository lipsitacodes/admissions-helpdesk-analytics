import React, { useState, useEffect, useCallback } from "react";
import { AppShell } from "./components/AppShell";
import { LandingPage } from "./components/LandingPage";
import { SpeedLoader } from "./components/SpeedLoader";
import BlobCursor from "./components/BlobCursor";
import { auth } from "./firebase";
import { onAuthStateChanged, signOut, setPersistence, browserLocalPersistence } from "firebase/auth";

function formatTimestamp() {
  return new Intl.DateTimeFormat("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());
}

function cleanAnswerText(text) {
  if (!text) return "";
  const lines = String(text).trim().split(/\r?\n/);
  while (lines.length && !lines[0].trim()) lines.shift();
  while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
  if (lines[0]?.trim() === "Here is the information I found:") lines.shift();
  while (lines.length && !lines[0].trim()) lines.shift();
  if (
    lines[lines.length - 1]?.trim() ===
    "Please check the latest university prospectus for final details."
  ) {
    lines.pop();
  }
  while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
  return lines.join("\n");
}

// Build a user-scoped localStorage key
function userKey(base, uid) {
  const scope = uid || "guest";
  return `${base}_${scope}`;
}

function loadChats(uid) {
  try {
    // Try user-scoped key first, then fall back to legacy key for migration
    const scopedKey = userKey("campus_ai_chats", uid);
    let raw = JSON.parse(localStorage.getItem(scopedKey));
    if (!Array.isArray(raw)) {
      // First time for this user — check if there's legacy data to migrate
      if (!uid) {
        raw = JSON.parse(localStorage.getItem("campus_ai_chats"));
      }
    }
    if (Array.isArray(raw)) {
      return raw.filter(
        (c) => c && typeof c === "object" && c.id && Array.isArray(c.messages)
      );
    }
    return [];
  } catch {
    return [];
  }
}

export function App() {
  // Initial Hyper-Speed Website Loader
  const [appLoading, setAppLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAppLoading(false);
    }, 1800);
    return () => clearTimeout(timer);
  }, []);

  // View routing: 'landing' | 'chat' — persisted across refreshes
  const [currentView, setCurrentView] = useState(() => {
    return localStorage.getItem("campus_ai_view") || "landing";
  });

  // Theme state: dark default
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("campus_ai_theme") || "dark";
  });

  // Candidate Name state
  const [candidateName, setCandidateName] = useState(() => {
    return localStorage.getItem("campus_ai_candidate_name") || "Student";
  });

  // Auth Modal State
  const [authOpen, setAuthOpen] = useState(false);
  const [firebaseUser, setFirebaseUser] = useState(null);

  // Set auth persistence to stay logged in across reloads
  useEffect(() => {
    setPersistence(auth, browserLocalPersistence).catch((e) => console.error('Auth persistence error', e));
  }, []);

  // Listen for Firebase auth state changes (login, logout, page refresh)
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setFirebaseUser(user);
      if (user) {
        const displayName = user.displayName || user.email?.split("@")[0] || "Student";
        setCandidateName(displayName);
        localStorage.setItem("campus_ai_candidate_name", displayName);
      }
    });
    return () => unsubscribe();
  }, []);

  // Swap chat history when user changes (login / logout / switch account)
  useEffect(() => {
    const uid = firebaseUser?.uid || null;
    const loaded = loadChats(uid);
    setChats(loaded);
    // Restore active chat for this user
    const savedActive = localStorage.getItem(userKey("campus_ai_active_chat", uid));
    if (savedActive && loaded.find((c) => c.id === savedActive)) {
      setActiveChatId(savedActive);
      activeChatIdRef.current = savedActive;
      const found = loaded.find((c) => c.id === savedActive);
      setMessages(found ? found.messages : []);
    } else {
      setActiveChatId(null);
      activeChatIdRef.current = null;
      setMessages([]);
    }
    setInput("");
    setErrorMessage("");
  }, [firebaseUser]);

  // Handle logout from Firebase
  const handleLogout = async () => {
    try {
      await signOut(auth);
      setFirebaseUser(null);
      setCandidateName("Student");
      localStorage.setItem("campus_ai_candidate_name", "Student");
      setCurrentView("landing");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  // Citation switch state
  const [citationEnabled, setCitationEnabled] = useState(true);

  // Target language state: 'en' | 'or' | 'hi'
  const [targetLanguage, setTargetLanguage] = useState(() => {
    return localStorage.getItem("campus_ai_target_lang") || "en";
  });

  useEffect(() => {
    localStorage.setItem("campus_ai_target_lang", targetLanguage);
  }, [targetLanguage]);

  // Responsive sidebar open state (default open on desktop, toggled via hamburger)
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    if (typeof window !== "undefined") {
      return window.innerWidth >= 1024;
    }
    return true;
  });

  // Chat history (ChatGPT-style)
  // Each entry: { id, title, createdAt (ISO string), messages: [] }
  const [chats, setChats] = useState(loadChats);
  const [activeChatId, setActiveChatId] = useState(() => {
    // Only restore if we're returning to chat view
    const savedView = localStorage.getItem("campus_ai_view");
    if (savedView === "chat") {
      return localStorage.getItem("campus_ai_active_chat") || null;
    }
    return null;
  });
  const activeChatIdRef = React.useRef(null);

  // Active-conversation messages — restore from saved chat on init
  const [messages, setMessages] = useState(() => {
    const savedView = localStorage.getItem("campus_ai_view");
    const savedId = localStorage.getItem("campus_ai_active_chat");
    if (savedView === "chat" && savedId) {
      const allChats = loadChats();
      const found = allChats.find((c) => c.id === savedId);
      return found ? found.messages : [];
    }
    return [];
  });
  const [input, setInput] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Keep ref in sync with state + persist for refresh restore (user-scoped)
  React.useEffect(() => {
    activeChatIdRef.current = activeChatId;
    const key = userKey("campus_ai_active_chat", firebaseUser?.uid || null);
    if (activeChatId) {
      localStorage.setItem(key, activeChatId);
    } else {
      localStorage.removeItem(key);
    }
  }, [activeChatId, firebaseUser]);

  // Persist current view so refresh lands on the same page
  useEffect(() => {
    localStorage.setItem("campus_ai_view", currentView);
  }, [currentView]);

  // Sync theme to root html element
  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("campus_ai_theme", theme);
  }, [theme]);

  // Persist chats to localStorage whenever they change (user-scoped)
  useEffect(() => {
    const key = userKey("campus_ai_chats", firebaseUser?.uid || null);
    localStorage.setItem(key, JSON.stringify(chats));
  }, [chats, firebaseUser]);

  // Periodic health check heartbeat to keep backend connection warm and verified
  useEffect(() => {
    const pingHealth = () => {
      fetch("/health").catch(() => {});
    };
    pingHealth();
    const interval = setInterval(pingHealth, 6000);
    return () => clearInterval(interval);
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  // Send message to Flask API
  const handleSend = useCallback(
    async (overrideText) => {
      const queryText = (overrideText !== undefined ? overrideText : input).trim();
      if (!queryText || isBusy) return;

      setErrorMessage("");
      const userMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        text: queryText,
        timestamp: formatTimestamp(),
      };

      // Determine / create the active chat session
      let currentChatId = activeChatIdRef.current;

      if (!currentChatId) {
        // First message in a new conversation - create a named session
        currentChatId = `chat-${Date.now()}`;
        const title =
          queryText.length > 36 ? queryText.slice(0, 36).trimEnd() + "..." : queryText;
        const newChat = {
          id: currentChatId,
          title,
          createdAt: new Date().toISOString(),
          messages: [userMessage],
        };
        setActiveChatId(currentChatId);
        activeChatIdRef.current = currentChatId;
        setChats((prev) => [newChat, ...prev]);
      } else {
        // Append to existing session
        setChats((prev) =>
          prev.map((c) =>
            c.id === currentChatId
              ? { ...c, messages: [...c.messages, userMessage] }
              : c
          )
        );
      }

      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsBusy(true);

      try {
        const response = await fetch("/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: queryText,
            target_language: targetLanguage,
            session_id: currentChatId,
            candidate_name: candidateName,
          }),
        });

        const data = await response.json().catch(() => null);

        if (!response.ok || !data || typeof data !== "object") {
          throw new Error(
            data?.error || "The Admissions Helpdesk is currently unavailable."
          );
        }

        if (typeof data.answer !== "string" || !data.answer.trim()) {
          throw new Error("Received an empty response from helpdesk.");
        }

        const cleanedAnswer = cleanAnswerText(data.answer);

        const assistantMessage = {
          id: `asst-${Date.now()}`,
          role: "assistant",
          text: cleanedAnswer,
          timestamp: formatTimestamp(),
          data: {
            grounded: Boolean(data.grounded),
            escalated: Boolean(data.escalated),
            source_document: data.source_document,
            accuracy_percentage: data.accuracy_percentage !== undefined ? data.accuracy_percentage : (data.classifier_confidence ? Math.round(data.classifier_confidence * 100) : 92),
            response_time_sec: data.response_time_sec !== undefined ? data.response_time_sec : 0.28,
            predicted_intent: data.predicted_intent,
          },
        };

        setChats((prev) =>
          prev.map((c) =>
            c.id === currentChatId
              ? { ...c, messages: [...c.messages, assistantMessage] }
              : c
          )
        );
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        console.error("Admissions query failed:", err);
        setErrorMessage(
          err.message || "Failed to communicate with admissions service."
        );
        const fallbackMessage = {
          id: `err-${Date.now()}`,
          role: "assistant",
          text: "I apologize, but I am unable to connect to the Admissions Helpdesk at this moment. Please verify your connection or contact the admissions office at 8260077222.",
          timestamp: formatTimestamp(),
          data: {
            grounded: false,
            escalated: true,
          },
        };
        setChats((prev) =>
          prev.map((c) =>
            c.id === currentChatId
              ? { ...c, messages: [...c.messages, fallbackMessage] }
              : c
          )
        );
        setMessages((prev) => [...prev, fallbackMessage]);
      } finally {
        setIsBusy(false);
      }
    },
    [input, isBusy, targetLanguage]
  );

  // Launch from Landing Page: switch to chat view, optionally pre-fill prompt
  const handleLaunchChat = (initialPrompt = "") => {
    setCurrentView("chat");
    if (initialPrompt && initialPrompt.trim()) {
      // Small delay ensures the chat view is mounted before sending
      setTimeout(() => handleSend(initialPrompt.trim()), 80);
    }
  };

  // Start a brand-new blank conversation
  const handleNewConversation = () => {
    setActiveChatId(null);
    activeChatIdRef.current = null;
    setMessages([]);
    setInput("");
    setErrorMessage("");
    setSidebarOpen(false);
  };

  // Click a past session in the sidebar - restore its messages
  const handleSelectChat = (chatId) => {
    const chat = chats.find((c) => c.id === chatId);
    if (!chat) return;
    setActiveChatId(chat.id);
    activeChatIdRef.current = chat.id;
    setMessages(chat.messages);
    setInput("");
    setErrorMessage("");
    setSidebarOpen(false);
  };

  // Delete a single chat from history
  const handleDeleteChat = (chatId) => {
    setChats((prev) => prev.filter((c) => c.id !== chatId));
    if (activeChatIdRef.current === chatId) {
      setActiveChatId(null);
      activeChatIdRef.current = null;
      setMessages([]);
      setInput("");
      setErrorMessage("");
    }
  };

  return (
    <>
      {appLoading && (
        <SpeedLoader
          title="Loading FEESABILITY Intelligence"
          subtitle="Synchronizing with institutional admissions database"
          fullScreen={true}
          onDismiss={() => setAppLoading(false)}
        />
      )}
      {currentView === "landing" ? (
        <LandingPage
          onLaunchChat={handleLaunchChat}
          onSaveCandidate={(name) => {
            setCandidateName(name);
            localStorage.setItem("campus_ai_candidate_name", name);
          }}
          theme={theme}
          firebaseUser={firebaseUser}
          onLogout={handleLogout}
        />
      ) : (
        <AppShell
          theme={theme}
          onToggleTheme={toggleTheme}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          onNewConversation={handleNewConversation}
          chats={chats}
          activeChatId={activeChatId}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
          onSelectTopic={(q) => handleSend(q)}
          messages={messages}
          isBusy={isBusy}
          input={input}
          setInput={setInput}
          onSubmit={() => handleSend()}
          errorMessage={errorMessage}
          candidateName={candidateName}
          setCandidateName={setCandidateName}
          authOpen={authOpen}
          setAuthOpen={setAuthOpen}
          citationEnabled={citationEnabled}
          setCitationEnabled={setCitationEnabled}
          targetLanguage={targetLanguage}
          setTargetLanguage={setTargetLanguage}
          onNavigateLanding={() => setCurrentView("landing")}
          firebaseUser={firebaseUser}
          onLogout={handleLogout}
        />
      )}
    </>
  );
}

export default App;

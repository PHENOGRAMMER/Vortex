import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { useAuth } from "../context/AuthContextCore";
import { chatApi } from "../api";
import Navbar from "./Navbar";
import { useStreamingChat } from "../hooks/useStreamingChat";

const HISTORY_LIMIT = 8;
const HISTORY_TEXT_LIMIT = 3000;

const markdownComponents = {
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || "");
    const codeText = String(children).replace(/\n$/, "");
    return match ? (
      <div className="my-3 rounded-xl overflow-hidden border border-white/8 bg-[#0d0d1a]">
        <div className="flex items-center justify-between px-4 py-2 border-b border-white/5 bg-[#080810] text-xs text-neutral-400 font-mono">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-violet-500/80" />
            {match[1]}
          </span>
          <button
            type="button"
            onClick={() => navigator.clipboard.writeText(codeText)}
            className="flex items-center gap-1 text-neutral-500 hover:text-neutral-200 transition-colors cursor-pointer text-[11px]"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Copy
          </button>
        </div>
        <pre className="p-4 overflow-x-auto text-sm font-mono text-violet-300 leading-relaxed">
          <code {...props}>{children}</code>
        </pre>
      </div>
    ) : (
      <code className="bg-violet-500/10 border border-violet-500/20 px-1.5 py-0.5 rounded-md text-violet-300 font-mono text-[0.85em]" {...props}>
        {children}
      </code>
    );
  },
  table: ({ children }) => (
    <div className="overflow-x-auto my-4 border border-white/8 rounded-xl">
      <table className="min-w-full divide-y divide-white/8 text-sm text-left">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-white/5 text-neutral-300">{children}</thead>,
  th: ({ children }) => <th className="px-4 py-2.5 font-semibold text-xs uppercase tracking-wider">{children}</th>,
  td: ({ children }) => <td className="px-4 py-2.5 border-t border-white/5">{children}</td>,
  p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
  ul: ({ children }) => <ul className="list-disc pl-5 mb-2 space-y-1">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-5 mb-2 space-y-1">{children}</ol>,
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  h1: ({ children }) => <h1 className="text-xl font-bold mb-3 mt-4">{children}</h1>,
  h2: ({ children }) => <h2 className="text-lg font-semibold mb-2 mt-3">{children}</h2>,
  h3: ({ children }) => <h3 className="text-base font-semibold mb-2 mt-3">{children}</h3>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-violet-500 pl-4 my-3 text-neutral-400 italic">{children}</blockquote>
  ),
};

function buildSafeHistory(messages) {
  return messages
    .slice(-HISTORY_LIMIT)
    .map(({ role, content, meta }) => {
      if (meta?.task_type === "image") {
        return { role, content: "[Generated image omitted from history to keep the next request small.]" };
      }
      const text = String(content || "");
      return {
        role,
        content: text.length > HISTORY_TEXT_LIMIT ? `${text.slice(0, HISTORY_TEXT_LIMIT)}\n[Previous message truncated.]` : text,
      };
    });
}

export default function Chat() {
  const { token } = useAuth();
  const { stream, cancel, status, streaming } = useStreamingChat(token);
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [tokenUsage, setTokenUsage] = useState({ used: 0, limit: 24000, remaining: 24000 });
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [imageModel, setImageModel] = useState("black-forest-labs/FLUX.1-schnell");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const textareaRef = useRef(null);
  const bottomRef = useRef(null);


  const tokenPercent = Math.min(100, Math.round((tokenUsage.used / tokenUsage.limit) * 100));
  const tokenBarColor =
    tokenPercent >= 100 ? "bg-red-500" : tokenPercent >= 80 ? "bg-amber-400" : "bg-gradient-to-r from-violet-500 to-fuchsia-500";
  const activeSession = sessions.find((s) => s.id === sessionId);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: sending ? "auto" : "smooth", block: "end" });
  }, [messages, sending]);

  async function loadSession(sessionToLoad) {
    if (!token) return;

    try {
      const detail = await chatApi.session(sessionToLoad, token);
      setSessionId(detail.id);
      setMessages(detail.messages || []);
      setTokenUsage({
        used: detail.tokens_used,
        limit: detail.token_limit,
        remaining: Math.max(0, detail.token_limit - detail.tokens_used),
      });
      setError("");
    } catch (err) {
      setError(err.message || "Could not load that chat session.");
    }
  }

  async function handleNewChat() {
    if (!token) return;

    try {
      const session = await chatApi.createSession(token);
      setSessions((current) => [session, ...current.filter((item) => item.id !== session.id)]);
      setSessionId(session.id);
      setMessages([]);
      setTokenUsage({ used: 0, limit: session.token_limit, remaining: session.token_limit });
      setInput("");
      setError(null);
      textareaRef.current?.focus();
    } catch (err) {
      setError(err.message || "Could not create a new chat.");
    }
  }

  async function handleSend() {
    const prompt = input.trim();
    if (!prompt || sending || !token) return;

    const previousMessages = messages;

    setSending(true);
    setError(null);
    setInput("");
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: prompt,
      },
      {
        role: "assistant",
        content: "",
      },
    ]);

    try {
      let assistant = "";
      await stream(prompt, (token) => {
        assistant += token;
        setMessages((prev) => {
          const copy = [...prev];
          copy[copy.length - 1] = {
            ...copy[copy.length - 1],
            content: assistant
          };
          return copy;
        });
      });
    } catch (err) {
      setMessages(previousMessages);
      setInput(prompt);
      setError(err.message || "Failed to send message.");
    } finally {
      setSending(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function refreshSessions() {
      if (!token) {
        setSessions([]);
        setMessages([]);
        setSessionId(null);
        setTokenUsage({ used: 0, limit: 24000, remaining: 24000 });
        setError(null);
        return;
      }

      try {
        const sessionList = await chatApi.sessions(token);
        if (cancelled) return;

        setSessions(sessionList);

        if (!sessionId && sessionList.length > 0) {
          await loadSession(sessionList[0].id);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Could not load chat sessions.");
        }
      }
    }

    refreshSessions();

    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    /*
      Section shade guide (darkest → lightest):
        Navbar:          #0a0a12  (handled by Navbar.jsx)
        Sidebar:         #0e0e18  — slightly lighter than page bg so it "lifts"
        Chat toolbar:    #0b0b14  — thin dark strip for context info
        Messages area:   #080810  — true base, the widest zone
        Input bar:       #0e0e1c  — same as sidebar to "frame" the bottom
    */
    <div className="h-screen overflow-hidden bg-[#080810] text-neutral-100 flex flex-col">
      <Navbar />

      <div className="flex flex-1 overflow-hidden">

        {/* ── Sidebar ─────────────────────────────────── */}
        <aside
          className={`${sidebarOpen ? "w-64" : "w-0"} shrink-0 overflow-hidden transition-all duration-300 ease-in-out bg-[#0e0e18] border-r border-white/5 flex flex-col`}>
          {/* New chat button */}
          <div className="p-3 border-b border-white/5">
            <button
              type="button"
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 hover:bg-violet-500/10 hover:border-violet-500/30 px-3 py-2.5 text-sm font-medium text-neutral-200 transition-all">
            
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>
          </div>

          {/* Session list */}
          <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
            {sessions.length === 0 && (
              <p className="text-neutral-500 text-xs text-center mt-8 px-4">No chats yet. Start a new one!</p>
            )}
            {sessions.map((session) => (
              <button
                key={session.id}
                type="button"
                onClick={() => loadSession(session.id)}
                className={`w-full text-left rounded-lg px-3 py-2.5 text-sm truncate transition-all ${
                  session.id === sessionId
                    ? "bg-violet-500/15 text-violet-200 border border-violet-500/20"
                    : "text-neutral-400 hover:text-neutral-200 hover:bg-white/5"
                }`}
              >
                {session.title || "Untitled Chat"}
              </button>
            ))}
          </div>

          {/* Token usage */}
          <div className="p-4 border-t border-white/5 bg-[#080810]">
            <div className="mb-2 flex items-center justify-between text-[11px] text-neutral-500">
              <span className="font-medium truncate mr-2">{activeSession?.title || "Token usage"}</span>
              <span className="shrink-0 tabular-nums">
                {tokenUsage.used.toLocaleString()} / {tokenUsage.limit.toLocaleString()}
              </span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/8">
              <div
                className={`h-full rounded-full transition-all duration-500 ${tokenBarColor}`}
                style={{ width: `${tokenPercent}%` }}
              />
            </div>
          </div>
        </aside>

        {/* ── Main column ──────────────────────────────── */}
        <div className="flex-1 flex flex-col overflow-hidden min-w-0">

          {/* Chat toolbar — distinct darker band */}
          <div className="shrink-0 bg-[#0b0b14] border-b border-white/5 px-4 py-2.5 flex items-center gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-white/8 transition-all"
              title="Toggle sidebar"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <span className="text-sm text-neutral-400 font-medium truncate">
              {activeSession?.title || "New conversation"}
            </span>
          </div>

          {/* ── Messages area — base colour ─── */}
          <main className="flex-1 overflow-y-auto bg-[#080810] px-4 py-8">
            <div className="max-w-3xl mx-auto space-y-2">
              {tokenUsage.warning && (
                <div className="rounded-xl border border-amber-400/20 bg-amber-400/8 px-4 py-3 text-sm text-amber-200 mb-4">
                  ⚠️ {tokenUsage.warning}
                </div>
              )}

              {messages.length === 0 && (
                <div className="mt-24 text-center">
                  <div className="w-14 h-14 rounded-2xl bg-linear-to-br from-violet-500/20 to-fuchsia-500/20 border border-white/8 flex items-center justify-center text-2xl mx-auto mb-6">
                    ✨
                  </div>
                  <h1 className="text-3xl font-semibold tracking-tight text-white mb-3">
                    How can I help you today?
                  </h1>
                  <p className="text-neutral-500 text-base font-light">
                    Chat, write code, or generate stunning images seamlessly.
                  </p>
                </div>
              )}

              {messages.map((m, i) => (
                <div key={i} className={`flex gap-4 py-5 ${i < messages.length - 1 ? "border-b border-white/4" : ""}`}>
                  {/* Avatar */}
                  <div
                    className={`w-8 h-8 shrink-0 rounded-lg flex items-center justify-center text-xs font-bold border ${
                      m.role === "user"
                        ? "bg-white/8 border-white/10 text-neutral-300"
                        : "bg-linear-to-br from-violet-500/30 to-fuchsia-500/30 border-violet-500/20 text-violet-300"
                    }`}
                  >
                    {m.role === "user" ? "U" : "AI"}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0 pt-0.5 text-[0.94rem] leading-relaxed text-neutral-200">
                    {m.meta?.task_type === "image" ? (
                      <img
                        src={`data:image/png;base64,${m.content}`}
                        alt="Generated"
                        className="rounded-xl max-w-2xl w-full border border-white/8 shadow-2xl"
                      />
                    ) : (
                      <div className="space-y-1">
                        <ReactMarkdown components={markdownComponents}>{String(m.content ?? "")}</ReactMarkdown>
                      </div>
                    )}
                    {m.meta && (
                      <p className="text-[11px] text-neutral-600 mt-2 font-mono">
                        {m.meta.provider} · {m.meta.model} · {m.meta.latency_ms}ms
                      </p>
                    )}
                  </div>
                </div>
              ))}

              {/* Typing animation */}
              {sending && (
                <div className="flex gap-4 py-5">
                  <div className="w-8 h-8 shrink-0 rounded-lg flex items-center justify-center text-xs font-bold bg-linear-to-br from-violet-500/30 to-fuchsia-500/30 border border-violet-500/20 text-violet-300">
                    AI
                  </div>
                  <div className="flex items-center gap-1.5 pt-2.5">
                    <span className="w-2 h-2 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-2 h-2 rounded-full bg-fuchsia-500 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              )}

              {error && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/8 px-4 py-3 text-sm text-red-300 flex items-center justify-between gap-3">
                  <span>⚠️ {error}</span>
                  <button
                    type="button"
                    onClick={() => setError(null)}
                    className="shrink-0 rounded-lg border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-neutral-200 transition-colors hover:bg-white/10"
                  >
                    Retry
                  </button>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          </main>

          {/* ── Input bar — elevated shade to frame the bottom ── */}
          <div className="shrink-0 bg-[#0e0e1c] border-t border-white/5 px-4 pb-5 pt-3">
            <div className="max-w-3xl mx-auto">

              {/* Model selector */}
              <div className="flex items-center gap-2 text-xs text-neutral-500 px-1 mb-2.5">
                <span className="font-medium">Model:</span>
                <select
                  value={imageModel}
                  onChange={(e) => setImageModel(e.target.value)}
                  className="bg-transparent text-neutral-400 outline-none hover:text-neutral-200 cursor-pointer transition-colors"
                >
                  <option value="black-forest-labs/FLUX.1-schnell">FLUX.1 Schnell</option>
                  <option value="stabilityai/stable-diffusion-xl-base-1.0">SDXL Base</option>
                  <option value="ByteDance/Hyper-SD">Hyper-SD</option>
                </select>
              </div>

              {streaming && (
                <div className="flex items-center justify-between gap-3 rounded-xl border border-violet-500/20 bg-violet-500/8 px-3 py-2 text-sm text-violet-100 mb-3">
                  <div className="min-w-0">
                    <div className="font-medium">{status}</div>
                  </div>
                  <button
                    type="button"
                    onClick={cancel}
                    className="shrink-0 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-neutral-200 transition-colors hover:bg-white/10"
                  >
                    Stop Generation
                  </button>
                </div>
              )}

              {!streaming && status && (
                <div className="rounded-xl border border-white/8 bg-white/5 px-3 py-2 text-sm text-neutral-400 mb-3">
                  {status}
                </div>
              )}

              {/* Textarea row */}
              <form
                onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                className="flex items-end gap-3 bg-[#13132a] border border-white/8 p-2 rounded-2xl focus-within:border-violet-500/40 focus-within:ring-1 focus-within:ring-violet-500/15 transition-all shadow-xl"
              >
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
                  }}
                  placeholder="Message OmniGen..."
                  rows={1}
                  className="flex-1 min-h-11 max-h-48 resize-none bg-transparent text-white px-3 py-2.5 outline-none placeholder:text-neutral-600 text-sm leading-relaxed"
                />
                <button
                  type="submit"
                  disabled={sending || !input.trim()}
                  className="flex items-center justify-center rounded-xl bg-linear-to-br from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 disabled:from-neutral-800 disabled:to-neutral-800 disabled:text-neutral-600 text-white h-10 w-10 shrink-0 transition-all shadow-lg shadow-violet-500/20 disabled:shadow-none mb-0.5 mr-0.5"
                  aria-label="Send"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 ml-0.5">
                    <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
                  </svg>
                </button>
              </form>

              <p className="text-center text-[11px] text-neutral-700 mt-2">
                <kbd className="bg-white/5 border border-white/8 rounded px-1 py-0.5 font-mono">Enter</kbd> to send ·{" "}
                <kbd className="bg-white/5 border border-white/8 rounded px-1 py-0.5 font-mono">Shift+Enter</kbd> for newline
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

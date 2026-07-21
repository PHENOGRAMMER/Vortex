import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router-dom";
import { chatApi, documentApi, generateApi } from "../api";
import { useAuth } from "../context/AuthContextCore";
import Navbar from "./Navbar";

const IMAGE_KEYWORDS = ["draw", "generate an image", "picture of", "illustration", "logo", "photo of", "image of", "render a", "create an image", "generate image", "make an image", "make a picture"];
const isImagePrompt = (text) => IMAGE_KEYWORDS.some((keyword) => text.toLowerCase().includes(keyword));
const safeHistory = (messages) => messages.slice(-8).map(({ role, content, meta }) => ({ role, content: meta?.task_type === "image" ? "[Generated image omitted.]" : String(content || "").slice(0, 3000) }));

export default function Chat() {
  const { token } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState([]);
  const [uploadingDocument, setUploadingDocument] = useState(false);
  const [input, setInput] = useState("");
  const localImageEnabled = import.meta.env.VITE_ENABLE_LOCAL_IMAGE !== "false";
  const [imageModel, setImageModel] = useState(localImageEnabled ? "local" : "disabled");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);
  const uploadInputRef = useRef(null);

  const refreshSessions = async () => {
    const result = await chatApi.sessions(token);
    setSessions(result);
  };
  useEffect(() => {
    if (!token) return undefined;
    let active = true;
    chatApi.sessions(token)
      .then((sessionResult) => {
        if (!active) return;
        setSessions(sessionResult);
      })
      .catch(() => {});
    return () => { active = false; };
  }, [token]);

  async function refreshDocuments(id) {
    if (!id) {
      setDocuments([]); setSelectedDocumentIds([]);
      return;
    }
    const result = await documentApi.list(token, id);
    const sessionDocuments = result.documents || [];
    setDocuments(sessionDocuments);
    setSelectedDocumentIds(sessionDocuments.map((document) => document.id));
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  async function loadSession(id) {
    try {
      const detail = await chatApi.session(id, token);
      setSessionId(detail.id);
      setMessages(detail.messages || []);
      await refreshDocuments(detail.id);
      setError("");
    } catch (err) { setError(err.message); }
  }
  async function newChat() {
    const session = await chatApi.createSession(token);
    setSessionId(session.id); setMessages([]); setSessions((old) => [session, ...old]);
    await refreshDocuments(session.id);
    return session.id;
  }
  async function uploadDocuments(event) {
    const files = Array.from(event.target.files || []);
    event.target.value = "";
    if (!files.length || uploadingDocument) return;
    setUploadingDocument(true); setError("");
    try {
      const targetSessionId = sessionId || await newChat();
      await documentApi.uploadForSession(files, targetSessionId, token);
      await refreshDocuments(targetSessionId);
    } catch (err) { setError(err.message || "Document upload failed."); }
    finally { setUploadingDocument(false); }
  }
  function toggleDocument(id) {
    setSelectedDocumentIds((old) => old.includes(id) ? old.filter((item) => item !== id) : [...old, id]);
  }
  async function send() {
    const prompt = input.trim();
    if (!prompt || sending) return;
    const previous = messages;
    const image = isImagePrompt(prompt);
    setInput(""); setError(""); setSending(true);
    setMessages((old) => [...old, { role: "user", content: prompt }, { role: "assistant", content: image ? "__generating__" : "Thinking…" }]);
    try {
      const data = await generateApi.generate(prompt, safeHistory(previous), !image && selectedDocumentIds.length > 0, token, image ? imageModel : undefined, sessionId, selectedDocumentIds);
      setSessionId(data.session_id);
      await refreshSessions();
      setMessages((old) => [...old.slice(0, -1), { role: "assistant", content: data.content, meta: { task_type: data.task_type, provider: data.provider, model: data.model, sources: data.sources || [] } }]);
    } catch (err) {
      setMessages(previous); setInput(prompt); setError(err.message || "Generation failed.");
    } finally { setSending(false); }
  }

  return <div className="h-screen overflow-hidden bg-[#080810] text-neutral-100 flex flex-col">
    <Navbar />
    <div className="flex flex-1 min-h-0">
      <aside className="w-64 shrink-0 border-r border-white/10 bg-[#0e0e18] p-3 flex flex-col gap-3">
        <button onClick={newChat} className="rounded-xl bg-violet-600 hover:bg-violet-500 px-3 py-2 text-sm font-semibold">+ New chat</button>
        <div className="flex-1 overflow-auto space-y-1">{sessions.map((session) => <button key={session.id} onClick={() => loadSession(session.id)} className={`w-full text-left truncate rounded-lg px-3 py-2 text-sm ${session.id === sessionId ? "bg-violet-500/20 text-violet-200" : "text-neutral-400 hover:bg-white/5"}`}>{session.title}</button>)}</div>
        <div className="border-t border-white/10 pt-3">
          <div className="flex items-center justify-between mb-2"><span className="text-xs font-semibold text-neutral-300">This chat's documents</span><Link className="text-xs text-violet-300 hover:text-violet-200" to="/upload">Manage</Link></div>
          <p className="text-[11px] text-neutral-500 mb-2">Files uploaded here are available only in this chat.</p>
          <div className="max-h-40 overflow-auto space-y-1">{documents.map((doc) => <label key={doc.id} className="flex items-center gap-2 rounded-lg border border-violet-400/15 bg-violet-500/8 px-2 py-2 text-xs text-violet-100 cursor-pointer hover:bg-violet-500/15"><input className="accent-violet-500" type="checkbox" checked={selectedDocumentIds.includes(doc.id)} onChange={() => toggleDocument(doc.id)} /> <span className="truncate">{doc.filename}</span></label>)}</div>
          {!documents.length && <p className="text-xs text-neutral-600">No documents attached yet.</p>}
        </div>
      </aside>
      <main className="flex-1 min-w-0 flex flex-col">
        <section className="flex-1 overflow-auto px-5 py-8"><div className="max-w-5xl mx-auto space-y-5">
          {!messages.length && <div className="pt-24 text-center"><h1 className="text-3xl font-semibold">What can I help you create?</h1><p className="mt-3 text-neutral-500">Chat, search your documents, write code, or generate images.</p></div>}
          {messages.map((message, index) => <article key={index} className={`max-w-[88%] rounded-2xl border px-5 py-4 shadow-lg ${message.role === "user" ? "ml-auto border-white/10 bg-[#1b1b2a]" : "mr-auto border-violet-400/20 bg-gradient-to-br from-violet-500/14 to-fuchsia-500/8"}`}>
            <div className={`mb-3 flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider ${message.role === "user" ? "text-sky-200" : "text-violet-200"}`}><span className={`h-2 w-2 rounded-full ${message.role === "user" ? "bg-sky-400" : "bg-violet-400"}`} />{message.role === "user" ? "You" : "OmniGen"}</div>
            <div className="prose prose-invert max-w-none text-[15px] leading-7 text-neutral-100">{message.content === "__generating__" || message.content === "Thinking…" ? <span className="text-violet-200 animate-pulse">{message.content}</span> : message.meta?.task_type === "image" ? <img src={`data:image/png;base64,${message.content}`} alt="Generated from your prompt" className="w-full max-w-2xl rounded-xl border border-white/10 shadow-xl shadow-violet-950/30" /> : <ReactMarkdown>{String(message.content || "")}</ReactMarkdown>}</div>
            {message.meta?.sources?.length > 0 && <div className="mt-4 rounded-xl border border-violet-400/15 bg-black/20 px-3 py-2 text-xs text-violet-100"><span className="font-semibold text-violet-300">Grounded sources</span><span className="mx-2 text-violet-400/50">•</span>{message.meta.sources.map((source) => source.filename).filter((name, i, items) => items.indexOf(name) === i).join(", ")}</div>}
          </article>)}<div ref={bottomRef} />
        </div></section>
        <section className="border-t border-white/10 bg-[#0e0e18] p-4"><div className="max-w-5xl mx-auto">
          {selectedDocumentIds.length > 0 && <div className="mb-3 inline-flex rounded-full border border-violet-400/20 bg-violet-500/10 px-3 py-1 text-xs font-medium text-violet-200">RAG active · {selectedDocumentIds.length} attached document{selectedDocumentIds.length === 1 ? "" : "s"}</div>}
          <div className="flex gap-2"><input ref={uploadInputRef} type="file" multiple accept=".pdf,.docx,.txt,.md" className="hidden" onChange={uploadDocuments} /><button type="button" onClick={() => uploadInputRef.current?.click()} disabled={uploadingDocument || sending} title="Attach a document to this chat" className="rounded-xl border border-white/10 px-3 text-sm text-violet-200 disabled:opacity-40">{uploadingDocument ? "…" : "Attach"}</button><textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }} placeholder="Message OmniGen…" className="min-h-12 flex-1 resize-none rounded-xl border border-white/10 bg-[#151528] p-3 text-sm outline-none focus:border-violet-500" /><button onClick={send} disabled={sending || !input.trim()} className="rounded-xl bg-violet-600 px-5 text-sm font-semibold disabled:opacity-40">Send</button></div>
          <div className="mt-3 flex items-center gap-2 text-xs text-neutral-500">Image model <select value={imageModel} onChange={(e) => setImageModel(e.target.value)} className="rounded-lg border border-white/10 bg-[#151528] px-2 py-1 text-neutral-200 outline-none">{localImageEnabled ? <><option value="local">Local GPU · Stable Diffusion</option><option value="black-forest-labs/FLUX.1-Krea-dev">HF FLUX Krea · Credits required</option><option value="black-forest-labs/FLUX.1-dev">HF FLUX.1 Dev · Credits required</option><option value="ByteDance/Hyper-SD">HF Hyper-SD · Credits required</option></> : <option value="disabled">Hosted demo · Images are local-only</option>}</select></div>
          {error && <p className="mt-2 text-sm text-red-300">{error}</p>}
        </div></section>
      </main>
    </div>
  </div>;
}

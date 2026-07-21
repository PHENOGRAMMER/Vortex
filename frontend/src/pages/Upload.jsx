import { useState, useRef } from "react";
import { useAuth } from "../context/AuthContextCore";
import { API_BASE_URL } from "../api";
import Navbar from "./Navbar";

const ACCEPT = ".pdf,.docx,.txt,.md";
const MAX_MB = 20;
const UPLOAD_TIMEOUT_MS = 180_000;

export default function Upload() {
  const { token } = useAuth();
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState(null); // { type: "success"|"error", message }
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  function handleFileChange(e) {
    const selected = Array.from(e.target.files).filter((f) => {
      if (f.size > MAX_MB * 1024 * 1024) {
        setStatus({ type: "error", message: `${f.name} exceeds ${MAX_MB} MB limit.` });
        return false;
      }
      return true;
    });
    setFiles(selected);
    setStatus(null);
  }

  async function handleUpload() {
    if (!files.length) {
      setStatus({ type: "error", message: "Please select at least one file." });
      return;
    }

    setUploading(true);
    setStatus(null);

    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), UPLOAD_TIMEOUT_MS);

    try {
      const res = await fetch(`${API_BASE_URL}/api/rag/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
        signal: controller.signal,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || `Upload failed (${res.status})`);
      }

      const { uploaded, errors } = data;
      const lines = [`✅ Indexed ${uploaded} document${uploaded !== 1 ? "s" : ""} for RAG.`];
      if (errors?.length) lines.push(`⚠️ Skipped: ${errors.join("; ")}`);

      setStatus({ type: uploaded > 0 ? "success" : "error", message: lines.join(" ") });
      if (uploaded > 0) {
        setFiles([]);
        if (inputRef.current) inputRef.current.value = "";
      }
    } catch (err) {
      setStatus({
        type: "error",
        message: err.name === "AbortError"
          ? "Indexing timed out. Check Ollama and the embedding model, then try again."
          : err.message,
      });
    } finally {
      window.clearTimeout(timeout);
      setUploading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#080810] text-neutral-200 flex flex-col">
      <Navbar />

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-16">
        <div className="w-full max-w-lg">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="w-12 h-12 rounded-2xl bg-violet-500/15 border border-violet-500/20 flex items-center justify-center text-2xl mx-auto mb-4">
              📄
            </div>
            <h1 className="text-2xl font-semibold text-white mb-2">Upload Documents</h1>
            <p className="text-sm text-neutral-500">
              Upload PDF, DOCX, TXT, or Markdown files. They'll be indexed and available for
              context-aware RAG chat.
            </p>
          </div>

          {/* Drop zone */}
          <div
            className="rounded-2xl border-2 border-dashed border-white/10 bg-white/3 hover:border-violet-500/30 hover:bg-violet-500/5 transition-all p-10 flex flex-col items-center gap-4 cursor-pointer"
            onClick={() => inputRef.current?.click()}
          >
            <svg className="w-10 h-10 text-neutral-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
            <p className="text-sm text-neutral-500 text-center">
              Click to browse or drag &amp; drop files here
              <br />
              <span className="text-xs">.pdf · .docx · .txt · .md · max {MAX_MB} MB each</span>
            </p>
            <input
              ref={inputRef}
              type="file"
              multiple
              accept={ACCEPT}
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          {/* Selected files list */}
          {files.length > 0 && (
            <ul className="mt-4 space-y-2">
              {files.map((f, i) => (
                <li key={i} className="flex items-center justify-between rounded-xl border border-white/8 bg-white/3 px-4 py-2.5 text-sm">
                  <span className="text-neutral-300 truncate">{f.name}</span>
                  <span className="text-neutral-600 shrink-0 ml-4 text-xs">
                    {(f.size / 1024).toFixed(0)} KB
                  </span>
                </li>
              ))}
            </ul>
          )}

          {/* Upload button */}
          <button
            onClick={handleUpload}
            disabled={uploading || !files.length}
            className="mt-6 w-full py-3 rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 disabled:from-neutral-800 disabled:to-neutral-800 disabled:text-neutral-600 text-white font-semibold transition-all shadow-lg shadow-violet-500/20 disabled:shadow-none flex items-center justify-center gap-2"
          >
            {uploading ? (
              <>
                <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                Indexing…
              </>
            ) : (
              "Upload & Index"
            )}
          </button>

          {/* Status message */}
          {status && (
            <div
              className={`mt-5 rounded-xl border px-4 py-3 text-sm ${
                status.type === "error"
                  ? "border-red-500/20 bg-red-500/8 text-red-300"
                  : "border-emerald-500/20 bg-emerald-500/8 text-emerald-300"
              }`}
            >
              {status.message}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

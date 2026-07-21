import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContextCore";
import { chatApi } from "../api";
import Navbar from "./Navbar";

export default function Home() {
  const { user, token } = useAuth();
  const navigate = useNavigate();

  async function handleStartChat() {
    try {
      await chatApi.createSession(token);
    } catch {
      // ignore — if it fails we still navigate and Chat.jsx will handle state
    }
    navigate("/chat");
  }

  return (
    <div className="min-h-screen bg-[#0b0b16] text-white flex flex-col relative overflow-hidden">
      {/* Ambient glow mesh */}
      <div className="bg-mesh" />

      <Navbar />

      {user ? (
        /* ── Logged-in hero ─────────────────────────────── */
        <main className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20 relative z-10">
          {/* Welcome badge */}
          <div className="inline-flex items-center gap-2 px-5 py-2 rounded-full border border-violet-500/40 bg-violet-500/15 text-violet-200 text-xs font-semibold mb-8 mx-auto">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Welcome back, {user.email}
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-5 leading-tight max-w-3xl mx-auto">
            Ready to{" "}
            <span className="bg-gradient-to-r from-violet-300 via-fuchsia-300 to-indigo-400 bg-clip-text text-transparent">
              create something?
            </span>
          </h1>

          <p className="text-base md:text-lg text-neutral-400 max-w-lg mx-auto font-light mb-12 leading-relaxed">
            Jump into a fresh conversation, generate stunning images, or write
            code — your AI co-pilot is ready.
          </p>

          {/* Primary CTA */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20 w-full">
            <button
              onClick={handleStartChat}
              className="group inline-flex items-center gap-3 rounded-2xl bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white font-semibold px-10 py-4 transition-all text-base shadow-xl shadow-violet-600/30 hover:shadow-violet-500/40 hover:scale-[1.03] active:scale-[0.98] min-w-[220px] justify-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 group-hover:rotate-12 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Start New Chat
            </button>

            {user.is_admin && (
              <Link
                to="/admin"
                className="inline-flex items-center gap-2.5 rounded-2xl border-2 border-white/20 bg-white/8 hover:bg-white/14 hover:border-white/30 text-white font-semibold px-10 py-4 transition-all text-base hover:scale-[1.02] active:scale-[0.98] min-w-[200px] justify-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Admin Dashboard
              </Link>
            )}
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 w-full max-w-4xl mx-auto text-left">
            <div className="glass-glow p-7 rounded-2xl flex flex-col gap-4 cursor-pointer" onClick={handleStartChat}>
              <div className="h-12 w-12 rounded-xl bg-violet-500/15 border border-violet-500/30 flex items-center justify-center text-2xl">
                💬
              </div>
              <div>
                <h3 className="text-base font-semibold text-white mb-1.5">Cognitive Chat</h3>
                <p className="text-sm text-neutral-400 leading-relaxed">
                  Intelligent problem-solving, planning, and contextual coding sessions.
                </p>
              </div>
            </div>

            <div className="glass-glow p-7 rounded-2xl flex flex-col gap-4 cursor-pointer" onClick={handleStartChat}>
              <div className="h-12 w-12 rounded-xl bg-fuchsia-500/15 border border-fuchsia-500/30 flex items-center justify-center text-2xl">
                🎨
              </div>
              <div>
                <h3 className="text-base font-semibold text-white mb-1.5">Image Synthesis</h3>
                <p className="text-sm text-neutral-400 leading-relaxed">
                  Generate jaw-dropping artwork using FLUX.1 and Hyper-SD models.
                </p>
              </div>
            </div>

            <div className="glass-glow p-7 rounded-2xl flex flex-col gap-4">
              <div className="h-12 w-12 rounded-xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-2xl">
                ⚡
              </div>
              <div>
                <h3 className="text-base font-semibold text-white mb-1.5">Lightning Fast</h3>
                <p className="text-sm text-neutral-400 leading-relaxed">
                  Sub-second responses with token tracking and multi-model support.
                </p>
              </div>
            </div>
          </div>
        </main>
      ) : (
        /* ── Logged-out hero ────────────────────────────── */
        <main className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20 relative z-10">
          {/* Animated badge */}
          <div className="inline-flex items-center gap-2 px-5 py-2 rounded-full border border-violet-500/40 bg-violet-500/15 text-violet-200 text-xs font-semibold mb-8 animate-pulse mx-auto">
            <span>✨</span> Discover the Power of OmniGen v2
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-5 leading-tight max-w-4xl mx-auto">
            Next-Generation <br />
            <span className="bg-gradient-to-r from-violet-300 via-fuchsia-300 to-indigo-400 bg-clip-text text-transparent">
              AI Assistant Platform
            </span>
          </h1>

          {/* Sub-headline */}
          <p className="text-base md:text-lg text-neutral-400 max-w-xl mx-auto font-light mb-12 leading-relaxed">
            Unlock state-of-the-art chat assistance, lightning-fast code generation,
            and hyper-realistic image synthesis powered by FLUX &amp; Stable Diffusion.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20 w-full">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2.5 rounded-2xl bg-white hover:bg-neutral-100 text-black font-semibold px-10 py-4 transition-all text-base shadow-xl shadow-white/20 hover:scale-[1.03] active:scale-[0.98] min-w-[220px]"
            >
              🚀 Start building for free
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2.5 rounded-2xl border-2 border-white/25 bg-white/8 hover:bg-white/14 hover:border-white/35 text-white font-semibold px-10 py-4 transition-all text-base hover:scale-[1.02] active:scale-[0.98] min-w-[200px]"
            >
              Log in to account
            </Link>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 w-full max-w-4xl mx-auto text-left">
            <div className="glass-glow p-7 rounded-2xl flex flex-col gap-4">
              <div className="h-12 w-12 rounded-xl bg-violet-500/15 border border-violet-500/30 flex items-center justify-center text-2xl">
                💬
              </div>
              <div>
                <h3 className="text-base font-semibold text-white mb-1.5">Cognitive Chat</h3>
                <p className="text-sm text-neutral-400 leading-relaxed">
                  Engage in intelligent problem-solving, planning, and contextual coding sessions.
                </p>
              </div>
            </div>

            <div className="glass-glow p-7 rounded-2xl flex flex-col gap-4">
              <div className="h-12 w-12 rounded-xl bg-fuchsia-500/15 border border-fuchsia-500/30 flex items-center justify-center text-2xl">
                🎨
              </div>
              <div>
                <h3 className="text-base font-semibold text-white mb-1.5">Image Synthesis</h3>
                <p className="text-sm text-neutral-400 leading-relaxed">
                  Generate jaw-dropping artwork on the fly using FLUX.1 and Hyper-SD models.
                </p>
              </div>
            </div>

            <div className="glass-glow p-7 rounded-2xl flex flex-col gap-4">
              <div className="h-12 w-12 rounded-xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-2xl">
                📊
              </div>
              <div>
                <h3 className="text-base font-semibold text-white mb-1.5">Admin Dashboard</h3>
                <p className="text-sm text-neutral-400 leading-relaxed">
                  Monitor prompt tokens, requests by provider, latency stats, and audit logs.
                </p>
              </div>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}

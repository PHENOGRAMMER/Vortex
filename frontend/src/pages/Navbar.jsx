import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContextCore";

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const isLinkActive = (path) => location.pathname === path;

  return (
    <nav className="h-16 shrink-0 border-b border-white/5 bg-[#0a0a12] backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-50">
      {/* Brand logo */}
      <Link to="/" className="flex items-center gap-2 group">
        <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
          OmniGen
        </span>
      </Link>

      <div className="flex items-center gap-6 text-sm font-medium">
        {user && (
          <>
            <Link
              to="/chat"
              className={`transition-colors py-1 relative ${
                isLinkActive("/chat") ? "text-white" : "text-neutral-400 hover:text-white"
              }`}
            >
              Chat
              {isLinkActive("/chat") && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-violet-500 rounded-full" />
              )}
            </Link>
            <Link
              to="/upload"
              className={`transition-colors py-1 relative ${
                isLinkActive("/upload") ? "text-white" : "text-neutral-400 hover:text-white"
              }`}
            >
              Documents
              {isLinkActive("/upload") && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-violet-500 rounded-full" />
              )}
            </Link>
            {isAdmin && (
              <Link
                to="/admin"
                className={`transition-colors py-1 relative ${
                  isLinkActive("/admin") ? "text-white" : "text-neutral-400 hover:text-white"
                }`}
              >
                Admin Dashboard
                {isLinkActive("/admin") && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-violet-500 rounded-full" />
                )}
              </Link>
            )}
          </>
        )}

        {user ? (
          <div className="flex items-center gap-4">
            <span className="hidden md:inline-flex items-center gap-1.5 text-xs bg-white/6 border border-white/12 rounded-full px-4 py-1.5 text-neutral-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              {user.email}
            </span>
            <button
              onClick={handleLogout}
              className="rounded-xl bg-white/8 hover:bg-red-500/15 border border-white/12 hover:border-red-500/30 text-neutral-300 hover:text-red-300 px-5 py-2 transition-all text-sm font-semibold"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="text-neutral-300 hover:text-white transition-colors text-sm font-semibold px-4 py-2 rounded-xl hover:bg-white/8 border border-transparent hover:border-white/12"
            >
              Log in
            </Link>
            <Link
              to="/register"
              className="rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white px-5 py-2 transition-all text-sm font-semibold shadow-lg shadow-violet-600/25 hover:scale-[1.03] active:scale-[0.98]"
            >
              Sign up
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}

import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContextCore";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import AdminDashboard from "./pages/AdminDashboard";

function ProtectedRoute({ children, requireAdmin = false }) {
  const { token, isAdmin, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#080810] flex items-center justify-center">
        <div className="flex items-center gap-3 text-neutral-400 text-sm">
          <span className="w-5 h-5 rounded-full border-2 border-violet-500/50 border-t-violet-500 animate-spin" />
          Loading...
        </div>
      </div>
    );
  }
  if (!token) return <Navigate to="/login" replace />;
  if (requireAdmin && !isAdmin) return <Navigate to="/chat" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <Chat />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

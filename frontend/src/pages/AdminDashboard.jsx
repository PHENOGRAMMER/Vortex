import { useCallback, useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { useAuth } from "../context/AuthContextCore";
import { adminApi } from "../api";
import Navbar from "./Navbar";

const COLORS = ["#8b5cf6", "#ec4899", "#06b6d4", "#10b981", "#f59e0b"];

function toChartData(obj = {}) {
  return Object.entries(obj).map(([name, value]) => ({ name, value }));
}

function StatCard({ label, value, icon, color }) {
  return (
    <div className={`rounded-2xl border bg-neutral-900/40 p-5 backdrop-blur-sm relative overflow-hidden ${color?.border || "border-white/8"}`}>
      <div className={`absolute inset-0 opacity-5 ${color?.bg || ""}`} />
      <div className="relative">
        <div className={`inline-flex items-center justify-center w-9 h-9 rounded-xl mb-3 text-lg ${color?.icon || "bg-white/5"}`}>
          {icon}
        </div>
        <p className="text-neutral-400 text-xs font-medium mb-1">{label}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
      </div>
    </div>
  );
}

const customTooltipStyle = {
  background: "#0d0d14",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: "10px",
  boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
};

export default function AdminDashboard() {
  const { token } = useAuth();
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [logsTotal, setLogsTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState("");
  const limit = 20;

  const loadStats = useCallback(async () => {
    try {
      setStats(await adminApi.stats(token));
    } catch (err) {
      setError(err.message);
    }
  }, [token]);

  const loadLogs = useCallback(async (newOffset) => {
    try {
      const res = await adminApi.logs(token, { limit, offset: newOffset });
      setLogs(res.items);
      setLogsTotal(res.total);
      setOffset(newOffset);
    } catch (err) {
      setError(err.message);
    }
  }, [token]);

  useEffect(() => {
    Promise.resolve().then(() => {
      loadStats();
      loadLogs(0);
    });
  }, [loadStats, loadLogs]);

  if (error) {
    return (
      <div className="min-h-screen bg-[#080810] text-neutral-100">
        <Navbar />
        <div className="max-w-6xl mx-auto px-6 py-10">
          <div className="rounded-xl border border-red-500/20 bg-red-500/8 px-6 py-4 text-sm text-red-300">
            ⚠️ {error}
          </div>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="min-h-screen bg-[#080810] text-neutral-100">
        <Navbar />
        <div className="max-w-6xl mx-auto px-6 py-10 flex items-center gap-3 text-neutral-400 text-sm">
          <span className="w-4 h-4 rounded-full border-2 border-violet-500/50 border-t-violet-500 animate-spin" />
          Loading stats...
        </div>
      </div>
    );
  }

  const providerData = toChartData(stats.requests_by_provider);
  const taskData = toChartData(stats.requests_by_task_type);

  return (
    <div className="min-h-screen bg-[#080810] text-neutral-100">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
          <p className="text-neutral-500 text-sm mt-1">Monitor system performance and usage.</p>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            label="Total Requests"
            value={stats.total_requests}
            icon="📊"
            color={{ border: "border-violet-500/15", icon: "bg-violet-500/10", bg: "bg-violet-600" }}
          />
          <StatCard
            label="Error Rate"
            value={`${(stats.error_rate * 100).toFixed(1)}%`}
            icon="⚠️"
            color={{ border: "border-rose-500/15", icon: "bg-rose-500/10", bg: "bg-rose-600" }}
          />
          <StatCard
            label="Avg Latency"
            value={stats.avg_latency_ms ? `${stats.avg_latency_ms}ms` : "--"}
            icon="⚡"
            color={{ border: "border-amber-500/15", icon: "bg-amber-500/10", bg: "bg-amber-600" }}
          />
          <StatCard
            label="Total Users"
            value={stats.total_users}
            icon="👥"
            color={{ border: "border-teal-500/15", icon: "bg-teal-500/10", bg: "bg-teal-600" }}
          />
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="rounded-2xl border border-white/8 bg-neutral-900/40 p-5 backdrop-blur-sm">
            <h2 className="text-white font-semibold mb-1">Requests by Provider</h2>
            <p className="text-neutral-500 text-xs mb-5">Total requests grouped by AI provider</p>
            <ResponsiveContainer width="100%" height={230}>
              <BarChart data={providerData} barSize={28}>
                <XAxis dataKey="name" stroke="#4b5563" tick={{ fill: "#9ca3af", fontSize: 11 }} />
                <YAxis stroke="#4b5563" tick={{ fill: "#9ca3af", fontSize: 11 }} allowDecimals={false} />
                <Tooltip
                  contentStyle={customTooltipStyle}
                  labelStyle={{ color: "#e5e7eb" }}
                  itemStyle={{ color: "#c4b5fd" }}
                />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {providerData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="rounded-2xl border border-white/8 bg-neutral-900/40 p-5 backdrop-blur-sm">
            <h2 className="text-white font-semibold mb-1">Requests by Task Type</h2>
            <p className="text-neutral-500 text-xs mb-5">Distribution of chat, code, and image tasks</p>
            <ResponsiveContainer width="100%" height={230}>
              <PieChart>
                <Pie
                  data={taskData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={40}
                  paddingAngle={3}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {taskData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={customTooltipStyle}
                  labelStyle={{ color: "#e5e7eb" }}
                />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: "12px", color: "#9ca3af" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Logs Table */}
        <div className="rounded-2xl border border-white/8 bg-neutral-900/40 backdrop-blur-sm overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/6">
            <div>
              <h2 className="text-white font-semibold">Recent Logs</h2>
              <p className="text-neutral-500 text-xs mt-0.5">
                Showing {offset + 1}–{Math.min(offset + limit, logsTotal)} of {logsTotal} entries
              </p>
            </div>
            <div className="flex gap-2 text-sm">
              <button
                disabled={offset === 0}
                onClick={() => loadLogs(Math.max(0, offset - limit))}
                className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/8 text-neutral-300 text-xs font-medium disabled:opacity-30 hover:bg-white/10 transition-all"
              >
                ← Prev
              </button>
              <button
                disabled={offset + limit >= logsTotal}
                onClick={() => loadLogs(offset + limit)}
                className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/8 text-neutral-300 text-xs font-medium disabled:opacity-30 hover:bg-white/10 transition-all"
              >
                Next →
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="border-b border-white/5">
                <tr>
                  {["Time", "User", "Task", "Provider", "Status", "Latency", "Prompt"].map((h) => (
                    <th key={h} className="py-3 px-4 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => (
                  <tr
                    key={log.id}
                    className={`border-b border-white/4 hover:bg-white/3 transition-colors ${
                      i % 2 === 0 ? "bg-transparent" : "bg-white/[0.01]"
                    }`}
                  >
                    <td className="py-3 px-4 whitespace-nowrap text-neutral-400 text-xs font-mono">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-neutral-300 text-xs">{log.user_id}</td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1 rounded-md bg-white/5 border border-white/8 px-2 py-0.5 text-[11px] font-medium text-neutral-300">
                        {log.task_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-neutral-400 text-xs">{log.provider || "--"}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center gap-1.5 text-[11px] font-semibold ${
                          log.status === "success" ? "text-emerald-400" : "text-red-400"
                        }`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${log.status === "success" ? "bg-emerald-400" : "bg-red-400"}`} />
                        {log.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-neutral-400 text-xs font-mono">
                      {log.latency_ms ? `${log.latency_ms.toFixed(0)}ms` : "--"}
                    </td>
                    <td className="py-3 px-4 max-w-xs truncate text-neutral-400 text-xs">
                      {log.prompt_preview}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

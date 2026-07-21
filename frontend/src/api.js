const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export const API_BASE_URL = BASE_URL;

async function request(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail;
    const message =
      typeof detail === "object" && detail !== null
        ? detail.warning || detail.message || `Request failed (${res.status})`
        : detail || `Request failed (${res.status})`;
    const error = new Error(message);
    error.status = res.status;
    error.detail = detail;
    throw error;
  }
  return data;
}

export const authApi = {
  register: (email, password) =>
    request("/auth/register", { method: "POST", body: { email, password } }),
  login: (email, password) =>
    request("/auth/login", { method: "POST", body: { email, password } }),
  me: (token) => request("/auth/me", { token }),
};

export const generateApi = {
  generate: (prompt, history, hasContextDocs, token, imageModel, sessionId, documentIds) =>
    request("/api/generate", {
      method: "POST",
      body: {
        prompt,
        session_id: sessionId,
        history,
        has_context_docs: hasContextDocs,
        image_model: imageModel || undefined,
        document_ids: documentIds?.length ? documentIds : undefined,
      },
      token,
    }),
};

export const chatApi = {
  sessions: (token) => request("/api/sessions", { token }),
  createSession: (token) => request("/api/sessions", { method: "POST", token }),
  session: (id, token) => request(`/api/sessions/${id}`, { token }),
};

export const documentApi = {
  list: (token, sessionId) => request(`/api/documents${sessionId ? `?session_id=${sessionId}` : ""}`, { token }),
  uploadForSession: async (files, sessionId, token) => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("session_id", String(sessionId));
    const res = await fetch(`${BASE_URL}/api/rag/upload`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `Upload failed (${res.status})`);
    if (!data.uploaded) throw new Error(data.errors?.join("; ") || "Document was not indexed.");
    return data;
  },
  image: async (documentId, imageName, token) => {
    const res = await fetch(`${BASE_URL}/api/documents/${documentId}/images/${encodeURIComponent(imageName)}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Unable to load document image.");
    return URL.createObjectURL(await res.blob());
  },
  remove: (id, token) => request(`/api/documents/${id}`, { method: "DELETE", token }),
};

export const adminApi = {
  stats: (token) => request("/admin/stats", { token }),
  logs: (token, params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/admin/logs${qs ? `?${qs}` : ""}`, { token });
  },
  users: (token) => request("/admin/users", { token }),
};

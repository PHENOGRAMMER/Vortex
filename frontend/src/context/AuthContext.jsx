import { useState, useEffect } from "react";
import { authApi } from "../api";
import { AuthContext } from "./AuthContextCore";

const TOKEN_KEY = "omnigen_token";

function getInitialToken() {
  const params = new URLSearchParams(window.location.search);
  const queryToken = params.get("token");
  if (queryToken) {
    localStorage.setItem(TOKEN_KEY, queryToken);
    window.history.replaceState({}, "", window.location.pathname);
    return queryToken;
  }
  return localStorage.getItem(TOKEN_KEY);
}

const initialToken = getInitialToken();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(initialToken);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => !!initialToken);

  useEffect(() => {
    if (!token) return;

    let active = true;
    authApi
      .me(token)
      .then((me) => {
        if (active) setUser(me);
      })
      .catch(() => {
        if (!active) return;
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [token]);

  async function login(email, password) {
    const data = await authApi.login(email, password);
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setToken(data.access_token);
    const me = await authApi.me(data.access_token);
    setUser(me);
    return me;
  }

  async function register(email, password) {
    await authApi.register(email, password);
    return login(email, password);
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }

  const value = {
    token,
    user,
    loading,
    login,
    register,
    logout,
    isAdmin: !!user?.is_admin,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

import { createContext, useContext } from "react";

// Core authentication context used throughout the frontend.
export const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

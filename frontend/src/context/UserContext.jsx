import { createContext, useContext, useEffect, useState } from "react";
import apiClient from "../api/apiClient";

const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      setUser(null);
      setLoading(false);
      return null;
    }

    try {
      const response = await apiClient.get("/api/auth/me");

      setUser(response.data);

      return response.data;
    } catch (error) {
      console.error(error);

      setUser(null);

      localStorage.removeItem("token");
      localStorage.removeItem("token_type");
      localStorage.removeItem("email");

      return null;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  return (
    <UserContext.Provider
      value={{
        user,
        loading,
        setUser,
        refreshUser,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
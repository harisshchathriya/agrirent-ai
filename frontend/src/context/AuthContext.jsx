import { useEffect, useState } from "react";
import { AuthContext } from "./authContext";
import { getCurrentUser } from "../services/authService";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(
    localStorage.getItem("token")
  );
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(!!token);

  const login = (jwtToken) => {
    localStorage.setItem("token", jwtToken);
    setCurrentUser(null);
    setAuthLoading(true);
    setToken(jwtToken);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setCurrentUser(null);
    setAuthLoading(false);
  };

  useEffect(() => {
    let isMounted = true;

    async function loadUser() {
      if (!token) {
        setCurrentUser(null);
        setAuthLoading(false);
        return;
      }

      setAuthLoading(true);

      try {
        const user = await getCurrentUser();

        if (isMounted) {
          setCurrentUser(user);
        }
      } catch {
        if (isMounted) {
          logout();
        }
      } finally {
        if (isMounted) {
          setAuthLoading(false);
        }
      }
    }

    loadUser();

    return () => {
      isMounted = false;
    };
  }, [token]);

  const userRole = currentUser?.role || null;

  return (
    <AuthContext.Provider
      value={{
        token,
        currentUser,
        authLoading,
        login,
        logout,
        isAuthenticated: !!token,
        userRole,
        isOwner: userRole === "owner",
        isFarmer: userRole === "farmer",
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

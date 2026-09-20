import { useEffect, useState } from "react";
import { AuthContext } from "./authContext";
import { getCurrentUser } from "../services/authService";
import { TOKEN_STORAGE_KEY } from "../api/axios";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(
    localStorage.getItem(TOKEN_STORAGE_KEY)
  );
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(!!token);

  const login = async (jwtToken) => {
    if (!jwtToken || typeof jwtToken !== "string") {
      throw new Error("Login did not return a valid access token.");
    }

    localStorage.setItem(TOKEN_STORAGE_KEY, jwtToken);
    setCurrentUser(null);
    setAuthLoading(true);
    setToken(jwtToken);

    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
      return user;
    } catch (error) {
      logout();
      throw error;
    } finally {
      setAuthLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
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

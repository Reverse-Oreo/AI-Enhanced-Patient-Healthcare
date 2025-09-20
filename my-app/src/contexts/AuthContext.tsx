import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { AuthService } from 'services/auth';
import { UserProfile, Role } from 'types/auth';
import { LoadingSpinner } from 'components/common/LoadingSpinner';

interface AuthContextType {
  loading: boolean;                 // expose loading
  loggedIn: boolean;
  user: UserProfile | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;     // expose manual refresh
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// If backend doesn't return role exactly as 'patient' | 'clinician', normalize it here.
function normalizeUser(u: any): UserProfile {
  const role: Role =
    (u?.role as Role) ??
    (u?.isClinician ? 'clinician' : 'patient');
  return { ...u, role };
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [loading, setLoading] = useState(true);
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);

  const refresh = async () => {
    try {
      setLoading(true);
      // console.log("Document cookies:", document.cookie);

      const userData = await AuthService.getProfile();
      setUser(normalizeUser(userData));
      setLoggedIn(true);
    } catch {
      setUser(null);
      setLoggedIn(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const login = async () => {
    // call real login here
    await refresh();
  };

  const logout = async () => {
    try {
      await AuthService.logout();
    } catch (err) {
      console.error('Logout failed:', err);
    } finally {
      setUser(null);
      setLoggedIn(false);
    }
  };

  const value: AuthContextType = { loading, loggedIn, user, login, logout, refresh };

  if (loading) return <LoadingSpinner message="Checking session..." />;

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};

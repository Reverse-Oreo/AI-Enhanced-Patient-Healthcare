import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  useCallback,
  ReactNode,
} from 'react';
import { AuthService } from 'services/auth';
import type { UserProfile, Role } from 'types/auth';
import { LoadingSpinner } from 'components/common/LoadingSpinner';

type AuthContextType = {
  loading: boolean;
  loggedIn: boolean;
  user: UserProfile | null;
  userRole: Role | null;

  // preview role for header toggle when not logged in
  viewRole: Role;
  setViewRoleState: (r: Role) => void;

  login: () => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  hasRole: (role: Role) => boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const VIEW_ROLE_KEY = 'viewRole';

function normalizeUser(u: any): UserProfile | null {
  if (!u) return null;
  
  // Extract role from user data or use stored role
  const raw = (u.role || AuthService.getStoredRole() || 'patient') as Role;

  const role: Role =
    raw === 'patient' || raw === 'clinician' || raw === 'nurse' ? raw : 'patient';

  return { ...u, role };
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [userRole, setUserRole] = useState<Role | null>(null);

  // Preview role (used by header toggle when logged out)
  const [viewRole, setViewRole] = useState<Role>(() => {
    const saved = localStorage.getItem(VIEW_ROLE_KEY) as Role | null;
    return saved === 'patient' || saved === 'clinician' || saved === 'nurse'
      ? saved
      : 'patient';
  });

  const setViewRoleState = useCallback((r: Role) => {
    setViewRole(r);
    localStorage.setItem(VIEW_ROLE_KEY, r);
  }, []);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const me = await AuthService.getProfile();
      const normalizedUser = normalizeUser(me);
      
      setUser(normalizedUser);
      setUserRole(normalizedUser?.role || null);
      
      // Update stored role if different
      if (normalizedUser?.role && normalizedUser.role !== AuthService.getStoredRole()) {
        localStorage.setItem('userRole', normalizedUser.role);
      }
    } catch {
      setUser(null);
      setUserRole(null);
      localStorage.removeItem('userRole');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const login = useCallback(async () => {
    await refresh();
  }, [refresh]);

  const logout = useCallback(async () => {
    try {
      await AuthService.logout();
    } finally {
      setUser(null);
      setUserRole(null);
    }
  }, []);

  const hasRole = useCallback((role: Role): boolean => {
    return userRole === role;
  }, [userRole]);

  const loggedIn = !!user;

  const value: AuthContextType = useMemo(
    () => ({
      loading,
      loggedIn,
      user,
      userRole,
      viewRole,
      setViewRoleState,
      login,
      logout,
      refresh,
      hasRole,
    }),
    [loading, loggedIn, user, userRole, viewRole, setViewRoleState, login, logout, refresh, hasRole]
  );

  if (loading) return <LoadingSpinner message="Checking session..." />;

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
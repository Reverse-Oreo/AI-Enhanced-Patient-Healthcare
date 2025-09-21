import {
  UserProfile,
  AuthResponse,
  RegisterData,
  LoginData,
  UserUpdate,
  Role
} from '../types/auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || (() => {
  console.warn('⚠️ REACT_APP_API_URL not found, using localhost fallback');
  return 'http://localhost:8000';
})();

console.log('🔐 Auth Service using:', API_BASE_URL, process.env.REACT_APP_API_URL ? '(from env)' : '(fallback)');

export class AuthService {
  static async register(userData: RegisterData, role: Role): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register?role=${role}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      const data: AuthResponse = await response.json();
      
      localStorage.setItem('userRole', role);
      
      return data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  } 

  static async login(credentials: { email: string; password: string; role: string }) {
    const response = await fetch(`${API_BASE_URL}/auth/login?role=${credentials.role}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
      }),
      credentials: 'include'
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }
    
    const data = await response.json();
    
    // Store role from login response or use the provided role
    const userRole = (data.user?.role || credentials.role) as Role;
    localStorage.setItem('userRole', userRole);
    
    return data;
  }

  static async logout(): Promise<{ message: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Logout failed');
      }

      // Clear role from storage
      localStorage.removeItem('userRole');
      
      return await response.json();
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }
  
  static async getProfile() {
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: 'GET',
      credentials: 'include',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch profile');
    }
    
    return response.json();
  }

  static async updateProfile(profileData: any) {
    const response = await fetch(`${API_BASE_URL}/auth/update_profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(profileData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to update profile');
    }
    
    return response.json();
  }

  // Get user role from stored data
  static getStoredRole(): Role | null {
    const role = localStorage.getItem('userRole') as Role;
    return role && ['patient', 'clinician', 'nurse'].includes(role) ? role : null;
  }

  // Check if user has specific role
  static hasRole(requiredRole: Role): boolean {
    const userRole = this.getStoredRole();
    return userRole === requiredRole;
  }
}
"use client";

/**
 * Session management utilities for EHR Plan V3
 * Handles login, logout, and session validation
 */

const SESSION_TOKEN_KEY = 'ehr_session_token';
const USER_KEY = 'ehr_user';

export interface User {
  username: string;
  role: string;
  email?: string;
}

export interface Session {
  token: string;
  username: string;
  role: string;
  expires_at: string;
}

/**
 * Save session to localStorage
 */
export function saveSession(session: Session): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(SESSION_TOKEN_KEY, session.token);
    localStorage.setItem(USER_KEY, JSON.stringify({
      username: session.username,
      role: session.role,
    }));
  }
}

/**
 * Clear session from localStorage
 */
export function clearSession(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(SESSION_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * Get the session token
 */
export function getSessionToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return localStorage.getItem(SESSION_TOKEN_KEY);
}

/**
 * Get the current user
 */
export function getCurrentUser(): User | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const userStr = localStorage.getItem(USER_KEY);
  return userStr ? JSON.parse(userStr) : null;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getSessionToken();
}

/**
 * Check if user has admin role
 */
export function isAdmin(): boolean {
  const user = getCurrentUser();
  return user?.role === 'admin';
}

/**
 * Validate session with backend
 */
export async function validateSession(): Promise<User | null> {
  const token = getSessionToken();
  if (!token) {
    return null;
  }

  try {
    // Send token in Authorization header for GET request
    const response = await fetch('/api/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      clearSession();
      return null;
    }
    const data = await response.json();
    return {
      username: data.username,
      role: data.role,
      email: data.email,
    };
  } catch (err) {
    console.error('Session validation error:', err);
    clearSession();
    return null;
  }
}

/**
 * Login with username and password
 */
export async function login(username: string, password: string): Promise<Session | null> {
  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Login failed');
    }

    const data = await response.json();
    const session: Session = {
      token: data.token,
      username: data.username,
      role: data.role,
      expires_at: data.expires_at,
    };
    
    saveSession(session);
    return session;
  } catch (err) {
    console.error('Login error:', err);
    throw err;
  }
}

/**
 * Logout current user
 */
export async function logout(): Promise<void> {
  const token = getSessionToken();
  if (token) {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `token=${encodeURIComponent(token)}`,
      });
    } catch (err) {
      console.error('Logout error:', err);
    }
  }
  clearSession();
}

/**
 * Reset password
 */
export async function resetPassword(email: string): Promise<{message: string; new_password?: string} | null> {
  try {
    const response = await fetch('/api/reset-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `email=${encodeURIComponent(email)}`,
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Reset failed');
    }

    return await response.json();
  } catch (err) {
    console.error('Reset password error:', err);
    throw err;
  }
}

/**
 * Hook to use session in components
 */
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export function useSession(requiredRole?: string): {
  user: User | null;
  isLoading: boolean;
  error: string | null;
} {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    async function checkSession() {
      try {
        const currentUser = await validateSession();
        
        if (!currentUser) {
          if (requiredRole) {
            router.push('/login');
          }
          setUser(null);
        } else if (requiredRole && currentUser.role !== requiredRole) {
          setError('Unauthorized');
          router.push('/');
        } else {
          setUser(currentUser);
        }
      } catch (err) {
        setError('Session validation error');
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    checkSession();
  }, [requiredRole, router]);

  return { user, isLoading, error };
}

/**
 * Hook to check if user is admin
 */
export function useAdminAuth(): {
  isAdmin: boolean;
  isLoading: boolean;
  user: User | null;
} {
  const { user, isLoading } = useSession('admin');
  return { isAdmin: !!user, isLoading, user };
}

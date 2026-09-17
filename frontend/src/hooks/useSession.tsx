import { useCallback, useEffect, useState } from 'react';
import { api } from '@/services/api';
import type { Session } from '@/types';

export function useSession() {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const newSession = await api.createSession();
      setSession(newSession);
      return newSession;
    } catch (err) {
      setError('Failed to create session');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getSession = useCallback(async (sessionId: string) => {
    setLoading(true);
    setError(null);
    try {
      const sessionData = await api.getSession(sessionId);
      setSession(sessionData);
      return sessionData;
    } catch (err) {
      setError('Failed to load session');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearSession = useCallback(() => {
    setSession(null);
  }, []);

  // Auto-create session on mount
  useEffect(() => {
    if (!session) {
      createSession();
    }
  }, [createSession, session]);

  return {
    session,
    loading,
    error,
    createSession,
    getSession,
    clearSession,
  };
}
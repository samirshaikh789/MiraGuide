import { useCallback, useState } from 'react';
import { api, type AnalyzeResponse, type AIResponse, type DecisionResult } from '@/services/api';
import { useSession } from './useSession';
import { useVoice } from './useVoice';

export function useAnalyze() {
  const { session } = useSession();
  const { speak } = useVoice();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const clearResult = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  const analyzeImage = useCallback(async (
    file: File,
    options?: { question?: string; detailLevel?: 'brief' | 'standard' | 'detailed' }
  ) => {
    if (!session) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.analyzeImage(file, {
        sessionId: session.id,
        question: options?.question,
        detailLevel: options?.detailLevel,
      });
      setResult(response);
      if (response.ai_response.response_mode !== 'text') {
        speak(response.ai_response.summary);
      }
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session, speak]);

  const analyzeDocument = useCallback(async (
    file: File,
    options?: { simplifyLevel?: 'simple' | 'very-simple' | 'child' }
  ) => {
    if (!session) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.analyzeDocument(file, {
        sessionId: session.id,
        simplifyLevel: options?.simplifyLevel,
      });
      setResult(response);
      if (response.ai_response.response_mode !== 'text') {
        speak(response.ai_response.summary);
      }
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Document analysis failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session, speak]);

  const analyzeForm = useCallback(async (
    file: File,
    options?: { explainFields?: boolean }
  ) => {
    if (!session) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.analyzeForm(file, {
        sessionId: session.id,
        explainFields: options?.explainFields,
      });
      setResult(response);
      if (response.ai_response.response_mode !== 'text') {
        speak(response.ai_response.summary);
      }
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Form analysis failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session, speak]);

  const askQuestion = useCallback(async (question: string) => {
    if (!session) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.askQuestion(session.id, question);
      setResult(response);
      if (response.ai_response.response_mode !== 'text') {
        speak(response.ai_response.summary);
      }
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Question failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session, speak]);

  const simplifyText = useCallback(async (
    text: string,
    level: 'simple' | 'very-simple' | 'child' = 'simple'
  ) => {
    if (!session) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.simplifyText(text, level, session.id);
      setResult(response);
      if (response.ai_response.response_mode !== 'text') {
        speak(response.ai_response.summary);
      }
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Simplification failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session, speak]);

  const summarizeText = useCallback(async (text: string) => {
    if (!session) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.summarizeText(text, session.id);
      setResult(response);
      if (response.ai_response.response_mode !== 'text') {
        speak(response.ai_response.summary);
      }
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Summarization failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session, speak]);

  const chat = useCallback(async (message: string) => {
    if (!session) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.chat(message, session.id);
      setResult(response);
      if (response.ai_response.response_mode !== 'text') {
        speak(response.ai_response.summary);
      }
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Chat failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session, speak]);

  const transcribeAudio = useCallback(async (
    file: File,
    options?: { sessionId?: string; language?: string }
  ) => {
    if (!session) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.transcribeAudio(file, {
        sessionId: options?.sessionId || session.id,
        language: options?.language,
      });
      setResult(response);
      if (response.ai_response.response_mode !== 'text') {
        speak(response.ai_response.summary);
      }
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Transcription failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [session, speak]);

  return {
    loading,
    result,
    error,
    clearResult,
    analyzeImage,
    analyzeDocument,
    analyzeForm,
    askQuestion,
    simplifyText,
    summarizeText,
    chat,
    transcribeAudio,
  };
}
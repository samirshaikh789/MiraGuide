import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { speakText, stopSpeech } from '@/services/speech';

interface VoiceContextType {
  voiceEnabled: boolean;
  toggleVoice: () => void;
  speak: (text: string) => void;
  stop: () => void;
}

const VoiceContext = createContext<VoiceContextType | null>(null);

export function VoiceProvider({ children }: { children: ReactNode }) {
  const [voiceEnabled, setVoiceEnabled] = useState(false);

  const toggleVoice = useCallback(() => {
    setVoiceEnabled(prev => {
      const next = !prev;
      if (!next) stopSpeech();
      return next;
    });
  }, []);

  const speak = useCallback((text: string) => {
    if (voiceEnabled) {
      speakText(text);
    }
  }, [voiceEnabled]);

  const stop = useCallback(() => {
    stopSpeech();
  }, []);

  return (
    <VoiceContext.Provider value={{ voiceEnabled, toggleVoice, speak, stop }}>
      {children}
    </VoiceContext.Provider>
  );
}

export function useVoice() {
  const context = useContext(VoiceContext);
  if (!context) {
    throw new Error('useVoice must be used within a VoiceProvider');
  }
  return context;
}
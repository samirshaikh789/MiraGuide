import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { loadSettings, saveSettings, defaultSettings } from '@/services/storage';
import type { AccessibilitySettings } from '@/types';

interface SettingsContextType {
  settings: AccessibilitySettings;
  updateSettings: (changes: Partial<AccessibilitySettings>) => void;
}

const SettingsContext = createContext<SettingsContextType | null>(null);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<AccessibilitySettings>(() => loadSettings());

  useEffect(() => {
    saveSettings(settings);
    document.documentElement.style.fontSize = `${settings.fontScale * 100}%`;
  }, [settings]);

  const updateSettings = (changes: Partial<AccessibilitySettings>) => {
    setSettings(current => ({ ...current, ...changes }));
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSettings }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
}
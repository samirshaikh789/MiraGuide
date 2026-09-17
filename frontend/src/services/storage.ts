import type { AccessibilitySettings, Transcript } from '../types';

const SETTINGS_KEY = 'accessai-settings';
const PHRASES_KEY = 'accessai-phrases';
const TRANSCRIPTS_KEY = 'accessai-transcripts';

export const defaultSettings: AccessibilitySettings = {
  fontScale: 1,
  highContrast: false,
  darkMode: false,
  reduceMotion: false,
  largerButtons: false,
  autoRead: false,
  speechRate: 1,
  voiceNavigation: false,
  simplifiedInterface: false,
  language: 'en',
};

export function loadSettings(): AccessibilitySettings {
  try { return { ...defaultSettings, ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}') }; }
  catch { return defaultSettings; }
}
export function saveSettings(settings: AccessibilitySettings) { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings)); }
export function loadPhrases(): string[] {
  try { return JSON.parse(localStorage.getItem(PHRASES_KEY) || '[]'); } catch { return []; }
}
export function savePhrases(phrases: string[]) { localStorage.setItem(PHRASES_KEY, JSON.stringify(phrases)); }
export function saveTranscript(content: string): Transcript {
  const item = { id: crypto.randomUUID(), createdAt: new Date().toISOString(), content };
  const current: Transcript[] = JSON.parse(localStorage.getItem(TRANSCRIPTS_KEY) || '[]');
  localStorage.setItem(TRANSCRIPTS_KEY, JSON.stringify([item, ...current].slice(0, 10)));
  return item;
}

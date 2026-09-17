import { useCallback, useEffect, useRef, useState } from 'react';

interface SpeechRecognitionEventLike extends Event { results: { [index: number]: { [index: number]: { transcript: string } }; length: number }; }
interface RecognitionLike {
  continuous: boolean; interimResults: boolean; lang: string; start(): void; stop(): void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: Event) => void) | null;
  onend: (() => void) | null;
}
type RecognitionConstructor = new () => RecognitionLike;

function getRecognition(): RecognitionConstructor | undefined {
  const win = window as unknown as { SpeechRecognition?: RecognitionConstructor; webkitSpeechRecognition?: RecognitionConstructor };
  return win.SpeechRecognition || win.webkitSpeechRecognition;
}

export function useSpeechRecognition(onText: (text: string) => void, continuous = false) {
  const [listening, setListening] = useState(false);
  const [supported] = useState(() => Boolean(getRecognition()));
  const [error, setError] = useState('');
  const recognitionRef = useRef<RecognitionLike | null>(null);

  const stop = useCallback(() => recognitionRef.current?.stop(), []);
  const start = useCallback(() => {
    const Constructor = getRecognition();
    if (!Constructor) { setError('Speech recognition is not available in this browser. You can type instead.'); return; }
    setError('');
    const recognition = new Constructor();
    recognition.continuous = continuous; recognition.interimResults = false; recognition.lang = 'en-IN';
    recognition.onresult = (event) => {
      const text = Array.from({ length: event.results.length }, (_, i) => event.results[i][0].transcript).join(' ');
      onText(text);
    };
    recognition.onerror = () => setError('We could not access your microphone. You can try again or type instead.');
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
    recognition.start(); setListening(true);
  }, [continuous, onText]);

  useEffect(() => () => recognitionRef.current?.stop(), []);
  return { listening, supported, error, start, stop };
}

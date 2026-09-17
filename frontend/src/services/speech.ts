export function speakText(text: string, rate = 1) {
  if (!('speechSynthesis' in window)) return false;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = rate;
  window.speechSynthesis.speak(utterance);
  return true;
}
export function stopSpeech() { window.speechSynthesis?.cancel(); }
export function pauseSpeech() { window.speechSynthesis?.pause(); }
export function resumeSpeech() { window.speechSynthesis?.resume(); }

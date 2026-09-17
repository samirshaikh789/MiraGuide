import { Mic, MicOff, Volume2, Send, Loader2, RotateCcw, Check, Clipboard, Sparkles } from 'lucide-react';
import { useState, useCallback, useRef, useEffect, FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Switch } from '@/components/ui/switch';
import { useAnalyze } from '@/hooks/useAnalyze';
import { useVoice } from '@/hooks/useVoice';
import { cn } from '@/lib/utils';
import type { AIResponse } from '@/services/api';

export function VoicePage() {
  const { speak, stop, voiceEnabled, toggleVoice } = useVoice();
  const { loading, result, error, clearResult, chat, transcribeAudio } = useAnalyze();

  const [spoken, setSpoken] = useState('');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [transcribed, setTranscribed] = useState('');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [recording, setRecording] = useState(false);

  const aiResponse = result?.ai_response;

  const handleRecord = async () => {
    if (recording) {
      mediaRecorderRef.current?.stop();
      setRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (e) => {
          audioChunksRef.current.push(e.data);
        };

        mediaRecorderRef.current.onstop = async () => {
          const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const file = new File([blob], 'recording.webm', { type: 'audio/webm' });
          setAudioFile(file);
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorderRef.current.start();
        setRecording(true);
        setTranscribed('');
      } catch (err) {
        alert('Could not access microphone. Please enable microphone permissions.');
      }
    }
  };

  const handleTranscribe = async () => {
    if (!audioFile) return;
    const response = await transcribeAudio(audioFile);
    if (response) {
      setTranscribed(response.ai_response.summary);
      setSpoken(response.ai_response.summary);
      setAudioFile(null);
    }
  };

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    const text = spoken.trim() || transcribed.trim();
    if (!text) return;
    
    await chat(text);
    setSpoken('');
    setTranscribed('');
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAudioFile(file);
    }
  };

  const speakResult = () => {
    if (aiResponse?.summary) {
      speak(aiResponse.summary);
    }
  };

  const copyResult = async () => {
    if (aiResponse?.summary) {
      await navigator.clipboard.writeText(aiResponse.summary);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Voice Assistant</h1>
        <p className="mt-2 text-muted-foreground">
          Speak or type your question. Get responses read aloud.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input Panel */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Voice Input</CardTitle>
              <Switch
                checked={voiceEnabled}
                onCheckedChange={toggleVoice}
                aria-label="Enable voice output"
              />
            </div>
            <CardDescription>
              Record audio, upload a file, or type your message
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Microphone */}
            <div className="text-center">
              <Button
                onClick={handleRecord}
                disabled={loading}
                size="xl"
                variant={recording ? 'destructive' : 'default'}
                className="rounded-full h-20 w-20"
                aria-label={recording ? 'Stop recording' : 'Start recording'}
              >
                {recording ? (
                  <MicOff size={32} className="animate-pulse" />
                ) : (
                  <Mic size={32} />
                )}
              </Button>
              <p className="mt-3 text-sm text-muted-foreground">
                {recording ? 'Recording... Click to stop' : 'Click to start recording'}
              </p>
            </div>

            {/* Audio File Upload */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Or upload audio file</label>
              <input
                type="file"
                accept="audio/*"
                onChange={handleFileSelect}
                className="sr-only"
                id="audio-upload"
              />
              <Button variant="outline" onClick={() => document.getElementById('audio-upload')?.click()}>
                <Mic size={18} className="mr-2" />Choose audio file
              </Button>
              {audioFile && (
                <div className="flex items-center justify-between p-2 rounded bg-muted">
                  <span className="text-sm">{audioFile.name}</span>
                  <Button variant="ghost" size="sm" onClick={() => setAudioFile(null)}>
                    <RotateCcw size={14} />
                  </Button>
                </div>
              )}
            </div>

            {audioFile && !loading && (
              <Button onClick={handleTranscribe} className="w-full" size="lg">
                <Sparkles size={18} className="mr-2" />Transcribe Audio
              </Button>
            )}

            {/* Transcribed Text */}
            {transcribed && (
              <div className="space-y-2">
                <label className="text-sm font-medium">Transcribed Text</label>
                <Textarea
                  value={transcribed}
                  onChange={(e) => { setTranscribed(e.target.value); setSpoken(e.target.value); }}
                  rows={3}
                  placeholder="Transcribed text will appear here..."
                />
              </div>
            )}

            {/* Text Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Or type your message</label>
              <form onSubmit={handleSend}>
                <div className="flex gap-2">
                  <Textarea
                    value={spoken}
                    onChange={(e) => setSpoken(e.target.value)}
                    rows={3}
                    placeholder="Type your question or message..."
                  />
                  <Button type="submit" disabled={(!spoken.trim() && !transcribed.trim()) || loading} size="lg">
                    <Send size={18} className="mr-2" />Send
                  </Button>
                </div>
              </form>
            </div>
          </CardContent>
        </Card>

        {/* Response Panel */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Response</CardTitle>
              {aiResponse && (
                <div className="flex items-center gap-2">
                  <Badge variant={aiResponse.demo_mode ? 'secondary' : 'default'}>
                    {aiResponse.demo_mode ? 'Demo' : aiResponse.provider}
                  </Badge>
                  <Badge variant="outline">{Math.round(aiResponse.confidence * 100)}%</Badge>
                </div>
              )}
            </div>
            <CardDescription>
              {loading ? 'Processing...' : aiResponse ? 'Response received' : 'Send a message to get a response'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading && (
              <div className="space-y-4">
                <div className="h-4 bg-muted rounded animate-pulse" />
                <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
              </div>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {aiResponse && !loading && (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Badge variant={aiResponse.demo_mode ? 'secondary' : 'default'}>
                    {aiResponse.demo_mode ? 'Demo' : aiResponse.provider}
                  </Badge>
                  <Badge variant="outline">Confidence: {Math.round(aiResponse.confidence * 100)}%</Badge>
                </div>

                <div className="prose max-w-none">
                  <p className="whitespace-pre-wrap">{aiResponse.summary}</p>
                </div>

                {aiResponse.details.length > 0 && (
                  <div>
                    <h4 className="font-medium">Details</h4>
                    <ul className="mt-2 space-y-1 list-disc list-inside text-sm text-muted-foreground">
                      {aiResponse.details.map((detail, i) => (
                        <li key={i}>{detail}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {aiResponse.needs_clarification && aiResponse.clarification_question && (
                  <Alert variant="warning">
                    <AlertDescription>
                      <strong>Clarification:</strong> {aiResponse.clarification_question}
                    </AlertDescription>
                  </Alert>
                )}

                <div className="flex flex-wrap gap-2 pt-4 border-t">
                  <Button variant="outline" onClick={speakResult}>
                    <Volume2 size={18} className="mr-2" />Read Aloud
                  </Button>
                  <Button variant="outline" onClick={copyResult}>
                    <Check size={18} className="mr-2" />Copy
                  </Button>
                  <Button variant="outline" onClick={() => { setSpoken(''); clearResult(); }}>
                    <RotateCcw size={18} className="mr-2" />New Question
                  </Button>
                </div>
              </div>
            )}

            {!aiResponse && !loading && !error && (
              <div className="text-center py-12 text-muted-foreground">
                <Mic size={48} className="mx-auto mb-4 opacity-50" />
                <p>Record, upload, or type a message to get started</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
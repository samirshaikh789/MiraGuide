import { Send, Loader2, Sparkles, Bot, MessageSquare, Volume2, RotateCcw, Check, Clipboard, Trash2 } from 'lucide-react';
import { useState, useCallback, useRef, useEffect, FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Textarea } from '@/components/ui/textarea';
import { useAnalyze } from '@/hooks/useAnalyze';
import { useVoice } from '@/hooks/useVoice';
import { cn } from '@/lib/utils';
import type { AIResponse } from '@/services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  aiResponse?: AIResponse;
}

export function ChatPage() {
  const { speak } = useVoice();
  const { loading, result, error, clearResult, chat } = useAnalyze();

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hi! I'm MiraGuide, your accessibility assistant. How can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const aiResponse = result?.ai_response;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const text = input;
    setInput('');

    try {
      const response = await chat(text);
      if (response) {
        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.ai_response.summary,
          timestamp: new Date(),
          aiResponse: response.ai_response,
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (err) {
      // Error handled by hook
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: "Hi! I'm MiraGuide, your accessibility assistant. How can I help you today?",
        timestamp: new Date(),
      },
    ]);
    clearResult();
  };

  const copyMessage = async (text: string) => {
    await navigator.clipboard.writeText(text);
  };

  const speakMessage = (text: string) => {
    speak(text);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Chat Assistant</h1>
        <p className="mt-2 text-muted-foreground">
          Ask questions, get guidance, or just chat. I'm here to help with accessibility tasks.
        </p>
      </div>

      <Card className="flex flex-col h-[calc(100vh-300px)]">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Bot size={20} />
              </div>
              <div>
                <CardTitle className="text-lg">MiraGuide Assistant</CardTitle>
                <CardDescription>Ready to help with accessibility tasks</CardDescription>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={clearChat} aria-label="Clear chat">
              <Trash2 size={18} />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-4">
            <div className="space-y-6 pb-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-3',
                    message.role === 'user' && 'flex-row-reverse'
                  )}
                >
                  <div
                    className={cn(
                      'flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground'
                    )}
                  >
                    {message.role === 'user' ? (
                      <MessageSquare size={16} />
                    ) : (
                      <Bot size={16} />
                    )}
                  </div>
                  <div
                    className={cn(
                      'max-w-[70%] rounded-2xl px-4 py-2',
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground rounded-br-none'
                        : 'bg-muted rounded-bl-none'
                    )}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    {message.aiResponse && (
                      <div className="mt-2 flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => speakMessage(message.content)}
                        >
                          <Volume2 size={14} className="mr-1" />Read
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyMessage(message.content)}
                        >
                          <Check size={14} className="mr-1" />Copy
                        </Button>
                      </div>
                    )}
                    <p className="mt-1 text-xs text-muted-foreground">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
        </CardContent>

        <CardContent className="border-t p-4">
          <form onSubmit={handleSend} className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Shift+Enter for new line)"
              rows={1}
              className="flex-1 min-h-[44px] max-h-32 resize-none"
              disabled={loading}
            />
            <Button
              type="submit"
              disabled={!input.trim() || loading}
              size="lg"
              className="h-10"
            >
              {loading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send size={20} />
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
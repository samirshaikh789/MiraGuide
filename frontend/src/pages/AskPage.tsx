import { HelpCircle, Search, Volume2, RotateCcw, Loader2, Sparkles, MessageSquare, Image, FileText } from 'lucide-react';
import { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { useAnalyze } from '@/hooks/useAnalyze';
import { useSession } from '@/hooks/useSession';
import { useVoice } from '@/hooks/useVoice';
import { cn } from '@/lib/utils';
import type { AIResponse, Interaction } from '@/services/api';

export function AskPage() {
  const { session, loading: sessionLoading } = useSession();
  const { speak } = useVoice();
  const {
    loading,
    result,
    error,
    clearResult,
    askQuestion,
  } = useAnalyze();

  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<Array<{ question: string; response: AIResponse }>>([]);

  const handleAsk = async () => {
    if (!question.trim() || !session) return;
    const response = await askQuestion(question);
    if (response) {
      setHistory(prev => [...prev, { question, response: response.ai_response }]);
      setQuestion('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  const speakResult = (text: string) => {
    speak(text);
  };

  const aiResponse = result?.ai_response;

  // Build session context display
  const sessionContext = session?.context_data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Ask About What You See</h1>
        <p className="mt-2 text-muted-foreground">
          Ask follow-up questions about previously analyzed images or documents.
          Your questions use the session context for accurate answers.
        </p>
      </div>

      {/* Session Status */}
      <Card className="mb-4">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                <HelpCircle size={20} />
              </div>
              <div>
                <p className="font-medium">Active Session</p>
                <p className="text-sm text-muted-foreground">
                  {session ? `Session: ${session.id.slice(0, 8)}...` : 'No active session'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="outline">{session?.interactions?.length || 0} interactions</Badge>
              <Badge variant="outline">
                {sessionLoading ? 'Loading...' : 'Ready'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Session Context */}
      {sessionContext && (
        <Card className="mb-4">
          <CardHeader>
            <CardTitle>Session Context</CardTitle>
            <CardDescription>Previous analysis context available for follow-up questions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="p-4 rounded-lg bg-muted font-mono text-sm whitespace-pre-wrap max-h-48 overflow-y-auto">
              {sessionContext}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Question Input */}
      <Card className="mb-4">
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about the image/document... (e.g., 'What does the sign say?', 'How many steps?', 'What is the date?')"
                className="pl-10 w-full"
                disabled={loading || !session}
              />
            </div>
            <Button
              onClick={handleAsk}
              disabled={!question.trim() || loading || !session}
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Asking...
                </>
              ) : (
                <>
                  <Sparkles size={18} className="mr-2" />
                  Ask
                </>
              )}
            </Button>
          </div>
          {!session && (
            <p className="mt-2 text-sm text-muted-foreground">
              No active session. Go to <strong>See & Understand</strong>, <strong>Read & Explain</strong>, or <strong>Form Assist</strong> first to create a session with visual context.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Response */}
      <Card>
        <CardHeader>
          <CardTitle>Answer</CardTitle>
          <CardDescription>
            {aiResponse ? 'AI response with context' : 'Your answer will appear here'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading && (
            <div className="space-y-4">
              <div className="h-4 bg-muted rounded animate-pulse" />
              <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
              <div className="h-4 bg-muted rounded animate-pulse w-1/2" />
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

              {aiResponse.details.length > 0 ? (
                <div>
                  <h4 className="font-medium">Details</h4>
                  <ul className="mt-2 space-y-1 list-disc list-inside text-sm text-muted-foreground">
                    {aiResponse.details.map((detail, i) => (
                      <li key={i}>{detail}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {aiResponse.important_information.length > 0 ? (
                <div>
                  <h4 className="font-medium">Key Information</h4>
                  <div className="mt-2 space-y-2">
                    {aiResponse.important_information.map((info, i) => (
                      <div key={i} className="p-3 rounded-lg border bg-muted">
                        <div className="font-medium">{info.label}</div>
                        <div className="text-sm">{info.value}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}

              {aiResponse.needs_clarification && aiResponse.clarification_question && (
                <Alert variant="warning">
                  <AlertDescription>
                    <strong>Clarification:</strong> {aiResponse.clarification_question}
                  </AlertDescription>
                </Alert>
              )}

              <div className="flex gap-2 pt-4 border-t">
                <Button variant="outline" onClick={() => speakResult(aiResponse.summary)}>
                  <Volume2 size={18} className="mr-2" />Read Aloud
                </Button>
              </div>
            </div>
          )}

          {!aiResponse && !loading && !error && (
            <div className="text-center py-12 text-muted-foreground">
              <HelpCircle size={48} className="mx-auto mb-4 opacity-50" />
              <p>Ask a question about your previously analyzed content</p>
              <p className="text-sm mt-2">Requires an active session from See & Understand, Read & Explain, or Form Assist</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* History */}
      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Question History</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              <div className="space-y-4">
                {history.slice().reverse().map((item, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-start gap-3">
                      <Avatar>
                        <AvatarFallback>Q</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="font-medium">{item.question}</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 ml-10">
                      <Avatar>
                        <AvatarFallback>A</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">{item.response.summary}</p>
                      </div>
                    </div>
                    {index < history.length - 1 && <Separator />}
                  </div>
                ))}
            </div>
          </ScrollArea>
        </CardContent>
        </Card>
      )}

      {/* Suggested Questions */}
      <Card>
        <CardHeader>
          <CardTitle>Suggested Questions</CardTitle>
          <CardDescription>Common follow-up questions you can ask</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {[
              'What does this say?',
              'What is the most important information?',
              'Are there any dates or deadlines?',
              'What are the required fields?',
              'Can you explain this in simpler terms?',
              'What should I do next?',
            ].map((suggestion) => (
              <Button
                key={suggestion}
                variant="outline"
                onClick={() => { setQuestion(suggestion); handleAsk(); }}
                disabled={loading || !session}
                className="w-full justify-start"
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
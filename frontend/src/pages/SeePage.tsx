import { Camera, ImagePlus, Eye, Volume2, RotateCcw, Sparkles, Loader2, Check, Clipboard } from 'lucide-react';
import { useState, useRef, useEffect, useCallback, ChangeEvent } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Switch } from '@/components/ui/switch';
import { useAnalyze } from '@/hooks/useAnalyze';
import { useSession } from '@/hooks/useSession';
import { useVoice } from '@/hooks/useVoice';
import { fileIsImage, fileIsSmallEnough } from '@/utils';
import { cn } from '@/lib/utils';
import type { AIResponse } from '@/services/api';

const MAX_FILE_SIZE = 8 * 1024 * 1024;

export function SeePage() {
  const { session } = useSession();
  const { speak, stop } = useVoice();
  const {
    loading,
    result,
    error,
    clearResult,
    analyzeImage,
    askQuestion,
  } = useAnalyze();

  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [question, setQuestion] = useState('');
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [detailLevel, setDetailLevel] = useState<'brief' | 'standard' | 'detailed'>('standard');
  const [voiceOutput, setVoiceOutput] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    if (!fileIsImage(file)) {
      alert('Please choose an image file (JPG, PNG, WebP, GIF)');
      return;
    }
    if (!fileIsSmallEnough(file, MAX_FILE_SIZE)) {
      alert(`File too large. Maximum size is ${MAX_FILE_SIZE / (1024 * 1024)}MB`);
      return;
    }
    if (preview) URL.revokeObjectURL(preview);
    setImage(file);
    setPreview(URL.createObjectURL(file));
    clearResult();
  }, [preview, clearResult]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp'],
      'image/gif': ['.gif'],
    },
    maxSize: MAX_FILE_SIZE,
  });

  const handleFileSelect = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) onDrop([file]);
  };

  const startCamera = async () => {
    try {
      setCameraError('');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      });
      streamRef.current = stream;
      setCameraOn(true);
      setTimeout(() => {
        if (videoRef.current) videoRef.current.srcObject = stream;
      }, 0);
    } catch {
      setCameraError('Could not access camera. Please upload an image instead.');
    }
  };

  const capturePhoto = () => {
    const video = videoRef.current;
    if (!video) return;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
        onDrop([file]);
        stopCamera();
      }
    }, 'image/jpeg', 0.9);
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(track => track.stop());
    setCameraOn(false);
  };

  const handleAnalyze = async () => {
    if (!image) return;
    await analyzeImage(image, {
      question: question || undefined,
      detailLevel,
    });
  };

  const handleAskFollowUp = async () => {
    if (!question.trim() || !session) return;
    await askQuestion(question);
  };

  const speakResult = () => {
    if (result?.ai_response.summary) {
      speak(result.ai_response.summary);
    }
  };

  const copyResult = async () => {
    if (result?.ai_response.summary) {
      await navigator.clipboard.writeText(result.ai_response.summary);
    }
  };

  useEffect(() => {
    return () => {
      stopCamera();
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  const aiResponse = result?.ai_response;
  const decision = result?.decision;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">See & Understand</h1>
        <p className="mt-2 text-muted-foreground">
          Upload or capture an image to get an accessibility-focused description.
          Ask follow-up questions to learn more.
        </p>
      </div>

      {/* Privacy Notice */}
      <Alert variant="warning" className="mb-4">
        <AlertDescription>
          Your uploaded content is processed for this accessibility request only.
          Avoid uploading sensitive personal information unless necessary.
        </AlertDescription>
      </Alert>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input Panel */}
        <Card>
          <CardHeader>
            <CardTitle>Image Input</CardTitle>
            <CardDescription>
              Upload an image, take a photo, or drag and drop
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Upload Area */}
            <div
              {...getRootProps()}
              className={cn(
                'relative rounded-lg border-2 border-dashed p-8 text-center transition-colors',
                isDragActive
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/25 hover:border-primary/50'
              )}
            >
              <input {...getInputProps()} id="image-upload" type="file" accept="image/*" />
              {preview ? (
                <>
                  <img
                    src={preview}
                    alt="Selected for analysis"
                    className="mx-auto max-h-64 rounded-lg object-contain"
                  />
                  <div className="mt-4 flex gap-2 justify-center">
                    <Button variant="outline" onClick={() => document.getElementById('image-upload')?.click()}>
                      <ImagePlus size={18} className="mr-2" />Choose another
                    </Button>
                    <Button variant="outline" onClick={() => { setImage(null); setPreview(null); clearResult(); }}>
                      <RotateCcw size={18} className="mr-2" />Remove
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <ImagePlus size={48} className="mx-auto text-muted-foreground" />
                  <h3 className="mt-3 text-lg font-medium">Upload an image</h3>
                  <p className="text-sm text-muted-foreground">
                    JPG, PNG, WebP, or GIF. Maximum 8 MB.
                  </p>
                  <div className="mt-4 flex gap-2 justify-center">
                    <Button variant="outline" onClick={() => document.getElementById('image-upload')?.click()}>
                      <ImagePlus size={18} className="mr-2" />Choose file
                    </Button>
                    <Button variant="outline" onClick={startCamera} disabled={cameraOn}>
                      <Camera size={18} className="mr-2" />Use camera
                    </Button>
                  </div>
                </>
              )}
            </div>

            {/* Camera */}
            {cameraOn && (
              <div className="relative rounded-lg overflow-hidden bg-muted">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-64 object-cover"
                  aria-label="Camera preview"
                />
                <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/60 to-transparent">
                  <div className="flex gap-2 justify-center">
                    <Button variant="default" onClick={capturePhoto} className="w-full sm:w-auto">
                      <Camera size={18} className="mr-2" />Capture
                    </Button>
                    <Button variant="outline" onClick={stopCamera} className="w-full sm:w-auto">
                      Stop camera
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {cameraError && (
              <Alert variant="destructive">
                <AlertDescription>{cameraError}</AlertDescription>
              </Alert>
            )}

            {/* Options */}
            <div className="space-y-4 pt-2 border-t">
              <div>
                <label className="text-sm font-medium">Detail Level</label>
                <div className="mt-2 flex gap-2">
                  {(['brief', 'standard', 'detailed'] as const).map((level) => (
                    <Button
                      key={level}
                      variant={detailLevel === level ? 'default' : 'outline'}
                      onClick={() => setDetailLevel(level)}
                      className="flex-1"
                    >
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Voice Output</label>
                <Switch
                  checked={voiceOutput}
                  onCheckedChange={setVoiceOutput}
                  aria-label="Enable voice output"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button
                onClick={handleAnalyze}
                disabled={!image || loading}
                className="flex-1"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Eye size={18} className="mr-2" />
                    {question ? 'Analyze & Answer' : 'Analyze Image'}
                  </>
                )}
              </Button>
              {preview && !loading && (
                <Button variant="outline" onClick={() => { setImage(null); setPreview(null); clearResult(); }}>
                  <RotateCcw size={18} />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Result Panel */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Result</CardTitle>
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
              {loading ? 'Analyzing your image...' : aiResponse ? 'Analysis complete' : 'Upload an image to begin'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading && (
              <div className="space-y-4">
                <Progress value={50} className="h-2" />
                <p className="text-center text-sm text-muted-foreground">Understanding the content...</p>
              </div>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {aiResponse && !loading && (
              <div className="space-y-4">
                {/* Summary */}
                <div>
                  <h4 className="font-medium">Summary</h4>
                  <p className="mt-2 whitespace-pre-wrap">{aiResponse.summary}</p>
                </div>

                {/* Details */}
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

                {/* Important Information */}
                {aiResponse.important_information.length > 0 && (
                  <div>
                    <h4 className="font-medium">Important Information</h4>
                    <div className="mt-2 space-y-2">
                      {aiResponse.important_information.map((info, i) => (
                        <div
                          key={i}
                          className={cn(
                            'p-3 rounded-lg border',
                            info.priority <= 2 ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200' : 'bg-muted'
                          )}
                        >
                          <div className="font-medium">{info.label}</div>
                          <div className="text-sm text-muted-foreground">{info.value}</div>
                          <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                            <span>Priority: {info.priority}/5</span>
                            {info.source && <span>• Source: {info.source}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Entities */}
                {aiResponse.entities.length > 0 && (
                  <div>
                    <h4 className="font-medium">Detected Elements</h4>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {aiResponse.entities.map((entity, i) => (
                        <Badge key={i} variant="secondary">
                          {entity.label} ({Math.round(entity.confidence * 100)}%)
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Safety Note */}
                {aiResponse.safety_note && (
                  <Alert variant="destructive">
                    <AlertDescription>{aiResponse.safety_note}</AlertDescription>
                  </Alert>
                )}

                {/* Clarification */}
                {aiResponse.needs_clarification && aiResponse.clarification_question && (
                  <Alert variant="warning">
                    <AlertDescription>
                      <strong>Clarification needed:</strong> {aiResponse.clarification_question}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Follow-up Suggestions */}
                {aiResponse.follow_up_suggestions.length > 0 && (
                  <div>
                    <h4 className="font-medium">Suggested Follow-ups</h4>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {aiResponse.follow_up_suggestions.map((suggestion, i) => (
                        <Button
                          key={i}
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setQuestion(suggestion);
                            handleAskFollowUp();
                          }}
                        >
                          {suggestion}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex flex-wrap gap-2 pt-4 border-t">
                  <Button variant="outline" onClick={speakResult} disabled={voiceOutput}>
                    <Volume2 size={18} className="mr-2" />Read Aloud
                  </Button>
                  <Button variant="outline" onClick={copyResult}>
                    <Clipboard size={18} className="mr-2" />Copy
                  </Button>
                  <Button variant="outline" onClick={() => setQuestion('What else can you tell me?')}>
                    <Sparkles size={18} className="mr-2" />Ask More
                  </Button>
                </div>
              </div>
            )}

            {!aiResponse && !loading && !error && (
              <div className="text-center py-12 text-muted-foreground">
                <Eye size={48} className="mx-auto mb-4 opacity-50" />
                <p>Upload an image to get an accessibility-focused description</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Follow-up Question Section */}
      {(session && result) && (
        <Card>
          <CardHeader>
            <CardTitle>Ask a Follow-up Question</CardTitle>
            <CardDescription>
              Ask about specific details from the analyzed image
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., What does the sign say? How many steps are there?"
                className="flex-1"
                disabled={loading}
              />
              <Button onClick={handleAskFollowUp} disabled={!question.trim() || loading}>
                <Sparkles size={18} className="mr-2" />Ask
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              Your question will be answered using the image context from your session.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
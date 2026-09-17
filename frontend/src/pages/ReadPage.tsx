import { FileText, ImagePlus, ScanText, Volume2, RotateCcw, Sparkles, Loader2, Check, Clipboard, FileText as FileTextIcon } from 'lucide-react';
import { useState, useCallback, ChangeEvent } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Select, SelectItem } from '@/components/ui/select';
import { useAnalyze } from '@/hooks/useAnalyze';
import { useVoice } from '@/hooks/useVoice';
import { fileIsImage, fileIsSmallEnough } from '@/utils';
import { cn } from '@/lib/utils';
import type { AIResponse } from '@/services/api';

const MAX_FILE_SIZE = 8 * 1024 * 1024;

export function ReadPage() {
  const { speak } = useVoice();
  const {
    loading,
    result,
    error,
    clearResult,
    analyzeDocument,
    simplifyText,
    summarizeText,
  } = useAnalyze();

  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [simplifyLevel, setSimplifyLevel] = useState<'simple' | 'very-simple' | 'child'>('simple');

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

  const handleExtract = async () => {
    if (!image) return;
    await analyzeDocument(image, { simplifyLevel });
  };

  const handleSimplify = async () => {
    if (!result?.ai_response?.summary) return;
    await simplifyText(result.ai_response.summary, simplifyLevel);
  };

  const handleSummarize = async () => {
    if (!result?.ai_response?.summary) return;
    await summarizeText(result.ai_response.summary);
  };

  const speakResult = () => {
    if (result?.ai_response?.summary) {
      speak(result.ai_response.summary);
    }
  };

  const copyResult = async () => {
    if (result?.ai_response?.summary) {
      await navigator.clipboard.writeText(result.ai_response.summary);
    }
  };

  const aiResponse = result?.ai_response;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Read & Explain</h1>
        <p className="mt-2 text-muted-foreground">
          Turn a document, notice, sign, or label into accessible text.
          Get explanations, simplifications, and summaries.
        </p>
      </div>

      <Alert variant="warning" className="mb-4">
        <AlertDescription>
          Extracted text may contain errors. Always verify critical information against the original document.
        </AlertDescription>
      </Alert>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upload Panel */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Document</CardTitle>
            <CardDescription>
              Choose a clear photo of a document, sign, label, or notice
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              {...getRootProps()}
              className={cn(
                'relative rounded-lg border-2 border-dashed p-8 text-center transition-colors',
                isDragActive
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/25 hover:border-primary/50'
              )}
            >
              <input {...getInputProps()} id="doc-upload" type="file" accept="image/*" />
              {preview ? (
                <>
                  <img
                    src={preview}
                    alt="Selected document"
                    className="mx-auto max-h-64 rounded-lg object-contain"
                  />
                  <div className="mt-4 flex gap-2 justify-center">
                    <Button variant="outline" onClick={() => document.getElementById('doc-upload')?.click()}>
                      <ImagePlus size={18} className="mr-2" />Choose another
                    </Button>
                    <Button variant="outline" onClick={() => { setImage(null); setPreview(null); clearResult(); }}>
                      <RotateCcw size={18} className="mr-2" />Remove
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <FileTextIcon size={48} className="mx-auto text-muted-foreground" />
                  <h3 className="mt-3 text-lg font-medium">Upload a document image</h3>
                  <p className="text-sm text-muted-foreground">
                    Choose a clear photo of a sign, page, label, or notice.
                  </p>
                  <Button variant="outline" onClick={() => document.getElementById('doc-upload')?.click()}>
                    <ImagePlus size={18} className="mr-2" />Upload image
                  </Button>
                </>
              )}
            </div>

            <div className="space-y-3 pt-2 border-t">
              <div>
                <label className="text-sm font-medium">Simplification Level</label>
                <Select value={simplifyLevel} onChange={(v) => setSimplifyLevel(v as 'simple' | 'very-simple' | 'child')}>
                  <SelectItem value="simple">Simple - 6th grade level</SelectItem>
                  <SelectItem value="very-simple">Very Simple - 4th grade level</SelectItem>
                  <SelectItem value="child">Child-friendly - 10 year old level</SelectItem>
                </Select>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleExtract}
                disabled={!image || loading}
                className="flex-1"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Extracting...
                  </>
                ) : (
                  <>
                    <ScanText size={18} className="mr-2" />
                    Extract & Explain
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
              <CardTitle>Extracted Content</CardTitle>
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
              {loading ? 'Extracting and analyzing text...' : aiResponse ? 'Text extracted and analyzed' : 'Upload a document to begin'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading && (
              <div className="space-y-4">
                <Progress value={50} className="h-2" />
                <p className="text-center text-sm text-muted-foreground">Reading and understanding the document...</p>
              </div>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {aiResponse && !loading && (
              <Tabs defaultValue="extracted" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="extracted">Extracted Text</TabsTrigger>
                  <TabsTrigger value="simplified">Simplified</TabsTrigger>
                  <TabsTrigger value="summary">Summary</TabsTrigger>
                </TabsList>

                <TabsContent value="extracted" className="mt-4">
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium">Original Text</h4>
                      <div className="mt-2 p-4 rounded-lg bg-muted whitespace-pre-wrap font-mono text-sm max-h-96 overflow-y-auto">
                        {aiResponse.details[0] || aiResponse.summary}
                      </div>
                    </div>

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

                    <div className="flex flex-wrap gap-2 pt-4 border-t">
                      <Button variant="outline" onClick={speakResult}>
                        <Volume2 size={18} className="mr-2" />Read Aloud
                      </Button>
                      <Button variant="outline" onClick={copyResult}>
                        <Check size={18} className="mr-2" />Copy
                      </Button>
                      <Button variant="outline" onClick={handleSimplify} disabled={loading}>
                        <Sparkles size={18} className="mr-2" />Simplify
                      </Button>
                      <Button variant="outline" onClick={handleSummarize} disabled={loading}>
                        <FileText size={18} className="mr-2" />Summarize
                      </Button>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="simplified" className="mt-4">
                  <div className="space-y-4">
                    {aiResponse.intent === 'simplify' || aiResponse.details.some(d => d.includes('Simplified')) ? (
                      <div>
                        <div>
                          <h4 className="font-medium">Simplified Text</h4>
                          <p className="mt-2 whitespace-pre-wrap">{aiResponse.summary}</p>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" onClick={speakResult}>
                            <Volume2 size={18} className="mr-2" />Read Aloud
                          </Button>
                          <Button variant="outline" onClick={copyResult}>
                            <Check size={18} className="mr-2" />Copy
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <Sparkles size={48} className="mx-auto mb-4 opacity-50" />
                        <p>Select a simplification level and click "Extract & Explain" to get simplified text</p>
                        <p className="text-sm mt-2">Or click "Simplify" after extraction</p>
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="summary" className="mt-4">
                  <div className="space-y-4">
                    {aiResponse.intent === 'summarize' || aiResponse.details.length > 1 ? (
                      <div>
                        <div>
                          <h4 className="font-medium">Summary</h4>
                          <p className="mt-2">{aiResponse.summary}</p>
                        </div>
                        {aiResponse.details.length > 1 ? (
                          <div>
                            <h4 className="font-medium">Key Points</h4>
                            <ul className="mt-2 space-y-1 list-disc list-inside text-sm">
                              {aiResponse.details.slice(1).map((point, i) => (
                                <li key={i}>{point}</li>
                              ))}
                            </ul>
                          </div>
                        ) : null}
                        <div className="flex gap-2">
                          <Button variant="outline" onClick={speakResult}>
                            <Volume2 size={18} className="mr-2" />Read Aloud
                          </Button>
                          <Button variant="outline" onClick={copyResult}>
                            <Check size={18} className="mr-2" />Copy
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <FileText size={48} className="mx-auto mb-4 opacity-50" />
                        <p>Click "Summarize" after extraction to get a summary</p>
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            )}

            {!aiResponse && !loading && !error && (
              <div className="text-center py-12 text-muted-foreground">
                <FileTextIcon size={48} className="mx-auto mb-4 opacity-50" />
                <p>Upload a document to extract and understand its text</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
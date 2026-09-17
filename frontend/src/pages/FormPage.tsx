import { FileText, ImagePlus, ClipboardList, Volume2, RotateCcw, Loader2, AlertTriangle, Check, HelpCircle } from 'lucide-react';
import { useState, useCallback, ChangeEvent } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { useAnalyze } from '@/hooks/useAnalyze';
import { useVoice } from '@/hooks/useVoice';
import { fileIsImage, fileIsSmallEnough } from '@/utils';
import { cn } from '@/lib/utils';
import type { AIResponse } from '@/types';

const MAX_FILE_SIZE = 8 * 1024 * 1024;

export function FormPage() {
  const { speak } = useVoice();
  const {
    loading,
    result,
    error,
    clearResult,
    analyzeForm,
  } = useAnalyze();

  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [explainFields, setExplainFields] = useState(true);

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

  const handleAnalyze = async () => {
    if (!image) return;
    await analyzeForm(image, { explainFields });
  };

  const speakResult = () => {
    if (result?.ai_response?.summary) {
      speak(result.ai_response.summary);
    }
  };

  const aiResponse = result?.ai_response;
  const fields = aiResponse?.entities.filter(e => e.type === 'field') || [];
  const importantInfo = aiResponse?.important_information || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Form Assist</h1>
        <p className="mt-2 text-muted-foreground">
          Upload a form to identify fields, labels, and required information.
          Get step-by-step guidance for each field.
        </p>
      </div>

      <Alert variant="warning" className="mb-4">
        <AlertDescription>
          Field detection may not be 100% accurate. Always verify the form content yourself before submitting.
        </AlertDescription>
      </Alert>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upload Panel */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Form</CardTitle>
            <CardDescription>
              Choose a clear photo of a paper or digital form
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
              <input {...getInputProps()} id="form-upload" type="file" accept="image/*" />
              {preview ? (
                <>
                  <img
                    src={preview}
                    alt="Selected form"
                    className="mx-auto max-h-64 rounded-lg object-contain"
                  />
                  <div className="mt-4 flex gap-2 justify-center">
                    <Button variant="outline" onClick={() => document.getElementById('form-upload')?.click()}>
                      <ImagePlus size={18} className="mr-2" />Choose another
                    </Button>
                    <Button variant="outline" onClick={() => { setImage(null); setPreview(null); clearResult(); }}>
                      <RotateCcw size={18} className="mr-2" />Remove
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <FileText size={48} className="mx-auto text-muted-foreground" />
                  <h3 className="mt-3 text-lg font-medium">Upload a form image</h3>
                  <p className="text-sm text-muted-foreground">
                    Choose a clear photo of a form, application, or document with fields.
                  </p>
                  <Button variant="outline" onClick={() => document.getElementById('form-upload')?.click()}>
                    <ImagePlus size={18} className="mr-2" />Upload form
                  </Button>
                </>
              )}
            </div>

            <div className="space-y-3 pt-2 border-t">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Explain Each Field</label>
                <Switch
                  checked={explainFields}
                  onCheckedChange={setExplainFields}
                  aria-label="Explain each field in detail"
                />
              </div>
            </div>

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
                    Analyzing Form...
                  </>
                ) : (
                  <>
                    <ClipboardList size={18} className="mr-2" />
                    Analyze Form
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
              <CardTitle>Form Analysis</CardTitle>
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
              {loading ? 'Identifying fields and structure...' : aiResponse ? 'Form analyzed' : 'Upload a form to begin'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading && (
              <div className="space-y-4">
                <Progress value={50} className="h-2" />
                <p className="text-center text-sm text-muted-foreground">Analyzing form structure and fields...</p>
              </div>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {aiResponse && !loading && (
              <div className="space-y-6">
                {/* Summary */}
                <div>
                  <h3 className="font-semibold">Form Summary</h3>
                  <p className="mt-2">{aiResponse.summary}</p>
                </div>

                {/* Form Type Detection */}
                {importantInfo.length > 0 && (
                  <div>
                    <h3 className="font-semibold">Key Information</h3>
                    <div className="mt-2 space-y-2">
                      {importantInfo.map((info, i) => (
                        <div key={i} className="p-3 rounded-lg border bg-muted">
                          <div className="font-medium">{info.label}</div>
                          <div className="text-sm">{info.value}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Fields */}
                {fields.length > 0 && (
                  <div>
                    <h3 className="font-semibold flex items-center gap-2">
                      Detected Fields ({fields.length})
                      {aiResponse.needs_clarification && (
                        <Badge variant="secondary" className="ml-2">
                          <HelpCircle size={12} className="mr-1" />Review recommended
                        </Badge>
                      )}
                    </h3>
                    <div className="mt-3 space-y-2">
                      {fields.map((field, index) => (
                        <Accordion key={index} type="single" collapsible className="w-full">
                          <AccordionItem value={`field-${index}`}>
                            <AccordionTrigger className="w-full justify-start">
                              <div className="flex items-center gap-3">
                                <span className="flex h-8 w-8 items-center justify-center rounded bg-primary/10 text-primary font-bold">
                                  {index + 1}
                                </span>
                                <div className="flex-1">
                                  <div className="font-medium">{field.label || `Field ${index + 1}`}</div>
                                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <Badge variant="outline" className="text-xs">{field.type}</Badge>
                                    {field.value && <Badge variant="secondary" className="text-xs">Value: {field.value}</Badge>}
                                    <Badge variant={field.confidence > 0.8 ? 'default' : 'outline'} className="text-xs">
                                      {Math.round(field.confidence * 100)}% confident
                                    </Badge>
                                  </div>
                                </div>
                              </div>
                            </AccordionTrigger>
                            <AccordionContent>
                              <div className="space-y-2 pt-2">
                                <p className="text-sm">{aiResponse.summary}</p>
                                <div className="flex gap-2">
                                  <Button variant="outline" size="sm" onClick={() => speak(field.label || '')}>
                                    <Volume2 size={14} className="mr-1" />Read label
                                  </Button>
                                </div>
                              </div>
                            </AccordionContent>
                          </AccordionItem>
                        </Accordion>
                      ))}
                    </div>
                  </div>
                )}

                {/* Details */}
                {aiResponse.details.length > 0 && (
                  <div>
                    <h3 className="font-semibold">Analysis Details</h3>
                    <ul className="mt-2 space-y-1 list-disc list-inside text-sm text-muted-foreground">
                      {aiResponse.details.map((detail, i) => (
                        <li key={i}>{detail}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Safety/Confidence Warnings */}
                {aiResponse.safety_note && (
                  <Alert variant="destructive">
                    <AlertDescription>
                      <AlertTriangle size={14} className="mr-2" />
                      <strong>Safety Note:</strong> {aiResponse.safety_note}
                    </AlertDescription>
                  </Alert>
                )}

                {aiResponse.needs_clarification && aiResponse.clarification_question && (
                  <Alert variant="warning">
                    <AlertDescription>
                      <HelpCircle size={14} className="mr-2" />
                      <strong>Clarification Recommended:</strong> {aiResponse.clarification_question}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Actions */}
                <div className="flex flex-wrap gap-2 pt-4 border-t">
                  <Button variant="outline" onClick={speakResult}>
                    <Volume2 size={18} className="mr-2" />Read Summary Aloud
                  </Button>
                </div>
              </div>
            )}

            {!aiResponse && !loading && !error && (
              <div className="text-center py-12 text-muted-foreground">
                <ClipboardList size={48} className="mx-auto mb-4 opacity-50" />
                <p>Upload a form to identify fields and get guidance</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
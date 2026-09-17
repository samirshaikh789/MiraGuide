import { Type, Contrast, Moon, Sun, Move, MousePointer, Volume2, Languages, Accessibility, Shield, Info, Palette } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Select, SelectItem } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import { useSettings } from '@/hooks/useSettings';
import { cn } from '@/lib/utils';

export function SettingsPage() {
  const { settings, updateSettings } = useSettings();
  const [activeTab, setActiveTab] = useState<'visual' | 'audio' | 'interface' | 'advanced'>('visual');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Customize MiraGuide to work best for you. Settings are saved locally in your browser.
        </p>
      </div>

      <div className="flex gap-2 border-b">
        {[
          { id: 'visual', label: 'Visual', icon: Type },
          { id: 'audio', label: 'Audio', icon: Volume2 },
          { id: 'interface', label: 'Interface', icon: Move },
          { id: 'advanced', label: 'Advanced', icon: Accessibility },
        ].map((tab) => (
          <Button
            key={tab.id}
            variant={activeTab === tab.id ? 'default' : 'ghost'}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            className="gap-2"
          >
            <tab.icon size={18} />{tab.label}
          </Button>
        ))}
      </div>

      <Card>
        <CardContent className="pt-6">
          {/* Visual Settings */}
          {activeTab === 'visual' && (
            <div className="space-y-6">
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold">
                  <Type size={20} />Visual
                </h3>
                <p className="text-sm text-muted-foreground mt-1">Adjust display and text appearance</p>
              </div>

              <Separator />

              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <Label>Font Size</Label>
                      <p className="text-sm text-muted-foreground">Increase readability across the app</p>
                    </div>
                    <span className="font-mono text-lg">{Math.round(settings.fontScale * 100)}%</span>
                  </div>
                  <Slider
                    value={settings.fontScale}
                    onChange={(v) => updateSettings({ fontScale: v })}
                    min={0.85}
                    max={1.5}
                    step={0.05}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>High Contrast</Label>
                    <p className="text-sm text-muted-foreground">Use black, white, and strong borders</p>
                  </div>
                  <Switch
                    checked={settings.highContrast}
                    onCheckedChange={(v) => updateSettings({ highContrast: v })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Dark Mode</Label>
                    <p className="text-sm text-muted-foreground">Reduce bright background light</p>
                  </div>
                  <Switch
                    checked={settings.darkMode}
                    onCheckedChange={(v) => updateSettings({ darkMode: v })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Reduce Animations</Label>
                    <p className="text-sm text-muted-foreground">Minimize motion effects</p>
                  </div>
                  <Switch
                    checked={settings.reduceMotion}
                    onCheckedChange={(v) => updateSettings({ reduceMotion: v })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Larger Buttons</Label>
                    <p className="text-sm text-muted-foreground">Increase touch target sizes</p>
                  </div>
                  <Switch
                    checked={settings.largerButtons}
                    onCheckedChange={(v) => updateSettings({ largerButtons: v })}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Audio Settings */}
          {activeTab === 'audio' && (
            <div className="space-y-6">
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold">
                  <Volume2 size={20} />Audio
                </h3>
                <p className="text-sm text-muted-foreground mt-1">Configure speech and sound</p>
              </div>

              <Separator />

              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Auto Read Results</Label>
                    <p className="text-sm text-muted-foreground">Automatically speak analysis results</p>
                  </div>
                  <Switch
                    checked={settings.autoRead}
                    onCheckedChange={(v) => updateSettings({ autoRead: v })}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <Label>Speech Rate</Label>
                      <p className="text-sm text-muted-foreground">Adjust how fast text is spoken</p>
                    </div>
                    <span className="font-mono">{settings.speechRate.toFixed(1)}x</span>
                  </div>
                  <Slider
                    value={settings.speechRate}
                    onChange={(v) => updateSettings({ speechRate: v })}
                    min={0.5}
                    max={2}
                    step={0.1}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Voice Navigation</Label>
                    <p className="text-sm text-muted-foreground">Control the app with voice commands</p>
                  </div>
                  <Switch
                    checked={settings.voiceNavigation}
                    onCheckedChange={(v) => updateSettings({ voiceNavigation: v })}
                  />
                </div>

                <div>
                  <Label>Language</Label>
                  <Select value={settings.language} onChange={(v) => updateSettings({ language: v })}>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Spanish</SelectItem>
                    <SelectItem value="fr">French</SelectItem>
                    <SelectItem value="de">German</SelectItem>
                    <SelectItem value="zh">Chinese</SelectItem>
                    <SelectItem value="ja">Japanese</SelectItem>
                    <SelectItem value="hi">Hindi</SelectItem>
                  </Select>
                </div>
              </div>
            </div>
          )}

          {/* Interface Settings */}
          {activeTab === 'interface' && (
            <div className="space-y-6">
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold">
                  <Move size={20} />Interface
                </h3>
                <p className="text-sm text-muted-foreground mt-1">Interaction and navigation preferences</p>
              </div>

              <Separator />

              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Simplified Interface</Label>
                    <p className="text-sm text-muted-foreground">Reduce visual clutter and simplify layouts</p>
                  </div>
                  <Switch
                    checked={settings.simplifiedInterface}
                    onCheckedChange={(v) => updateSettings({ simplifiedInterface: v })}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Advanced Settings */}
          {activeTab === 'advanced' && (
            <div className="space-y-6">
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold">
                  <Accessibility size={20} />Advanced
                </h3>
                <p className="text-sm text-muted-foreground mt-1">Data and privacy settings</p>
              </div>

              <Separator />

              <div className="space-y-4">
                <div className="p-4 rounded-lg border bg-muted">
                  <h4 className="font-medium">Data Storage</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    All settings and session data are stored locally in your browser.
                    No data is sent to external servers unless you use AI features.
                  </p>
                </div>

                <div className="p-4 rounded-lg border bg-muted">
                  <h4 className="font-medium">Demo Mode</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Currently running in demo mode with simulated AI responses.
                    Configure API keys in the backend to enable real AI processing.
                  </p>
                </div>

                <div className="p-4 rounded-lg border bg-muted">
                  <h4 className="font-medium">Privacy</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Uploaded images and audio are processed temporarily and not stored permanently.
                    See our privacy policy for details.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
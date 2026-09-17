import { Sparkles, Eye, FileText, LayoutDashboard, MessageSquare, HelpCircle, Volume2 } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const features = [
  {
    path: '/see',
    title: 'See & Understand',
    description: 'Upload or capture an image to get an accessibility-focused description of your surroundings.',
    icon: Eye,
    color: 'bg-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
  },
  {
    path: '/read',
    title: 'Read & Explain',
    description: 'Extract text from documents, signs, and labels. Get explanations and simplifications.',
    icon: FileText,
    color: 'bg-green-500',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
  },
  {
    path: '/form',
    title: 'Form Assist',
    description: 'Analyze forms to identify fields, labels, and required information. Get step-by-step guidance.',
    icon: LayoutDashboard,
    color: 'bg-purple-500',
    bgColor: 'bg-purple-50 dark:bg-purple-900/20',
  },
  {
    path: '/ask',
    title: 'Ask About What You See',
    description: 'Ask follow-up questions about previously analyzed images or documents using session context.',
    icon: HelpCircle,
    color: 'bg-orange-500',
    bgColor: 'bg-orange-50 dark:bg-orange-900/20',
  },
  {
    path: '/voice',
    title: 'Voice Assistant',
    description: 'Speak your questions or listen to responses. Full voice input and output support.',
    icon: Volume2,
    color: 'bg-red-500',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
  },
  {
    path: '/chat',
    title: 'Chat Assistant',
    description: 'General conversation with the AI assistant for guidance and feature discovery.',
    icon: MessageSquare,
    color: 'bg-teal-500',
    bgColor: 'bg-teal-50 dark:bg-teal-900/20',
  },
] as const;

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">How can I help you today?</h1>
        <p className="mt-2 text-muted-foreground">
          Choose one simple action. You can change display, sound, or interaction settings anytime.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3" role="list" aria-label="Accessibility tools">
        {features.map((feature) => (
          <Card
            key={feature.path}
            className={cn(
              'relative overflow-hidden transition-all hover:shadow-lg',
              'group'
            )}
            role="listitem"
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className={cn(
                  'flex h-12 w-12 items-center justify-center rounded-lg',
                  feature.bgColor,
                  feature.color
                )}>
                  <feature.icon size={24} className="text-white" />
                </div>
                <NavLink
                  to={feature.path}
                  className="absolute inset-0 z-10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  aria-label={feature.title}
                />
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-semibold">{feature.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{feature.description}</p>
              </div>
              <div className="mt-6 flex items-center justify-between">
                <Button
                  variant="outline"
                  asChild
                  className="w-full sm:w-auto"
                >
                  <NavLink to={feature.path}>Open tool</NavLink>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
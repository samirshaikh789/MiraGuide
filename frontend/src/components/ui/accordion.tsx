import * as React from 'react';
import * as AccordionPrimitives from '@radix-ui/react-accordion';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

const Accordion = AccordionPrimitives.Root;

const AccordionItem = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitives.Item>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitives.Item>
>(({ className, ...props }, ref) => (
  <AccordionPrimitives.Item
    ref={ref}
    className={cn('border-b', className)}
    {...props}
  />
));
AccordionItem.displayName = 'AccordionItem';

const AccordionTrigger = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitives.Trigger>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitives.Trigger>
>(({ className, children, ...props }, ref) => (
  <AccordionPrimitives.Header>
    <AccordionPrimitives.Trigger
      ref={ref}
      className={cn(
        'flex flex-1 items-center justify-between py-4 font-medium transition-all hover:underline [&[data-state=open]>svg]:rotate-180',
        className
      )}
      {...props}
    >
      {children}
      <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200" />
    </AccordionPrimitives.Trigger>
  </AccordionPrimitives.Header>
));
AccordionTrigger.displayName = AccordionPrimitives.Trigger.displayName;

const AccordionContent = React.forwardRef<
  React.ElementRef<typeof AccordionPrimitives.Content>,
  React.ComponentPropsWithoutRef<typeof AccordionPrimitives.Content>
>(({ className, children, ...props }, ref) => (
  <AccordionPrimitives.Content
    ref={ref}
    className={cn('overflow-hidden text-sm transition-all data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down', className)}
    {...props}
  >
    <div className="pt-0 pb-4">{children}</div>
  </AccordionPrimitives.Content>
));
AccordionContent.displayName = AccordionPrimitives.Content.displayName;

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent };
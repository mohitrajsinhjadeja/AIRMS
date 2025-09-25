import * as React from 'react';

declare module '@/components/ui/tabs' {
  export const Tabs: React.ForwardRefExoticComponent<{
    defaultValue: string;
    className?: string;
    children?: React.ReactNode;
  } & React.RefAttributes<HTMLDivElement>>;

  export const TabsList: React.ForwardRefExoticComponent<{
    className?: string;
    children?: React.ReactNode;
  } & React.RefAttributes<HTMLDivElement>>;

  export const TabsTrigger: React.ForwardRefExoticComponent<{
    value: string;
    className?: string;
    children?: React.ReactNode;
  } & React.RefAttributes<HTMLButtonElement>>;

  export const TabsContent: React.ForwardRefExoticComponent<{
    value: string;
    className?: string;
    children?: React.ReactNode;
  } & React.RefAttributes<HTMLDivElement>>;
}
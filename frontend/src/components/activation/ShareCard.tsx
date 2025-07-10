'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface ShareCardProps {
  onReset: () => void;
  userId: string;
}

export default function ShareCard({ onReset, userId }: ShareCardProps) {

  useEffect(() => {
    const logShareStep = async () => {
       try {
        await fetch('/api/activation/log-event', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId, step_name: 'share_step_reached' }),
        });
        console.log("Event 'share_step_reached' registered.");
      } catch (error) {
        console.error("Failed in registering event...", error);
      }
    };

    logShareStep();
  }, [userId]);

  const handleCopyLink = () => {
    navigator.clipboard.writeText('https://joinbrim.ai/results/123xyz');
    alert('Link copiado para a área de transferência!');
  };

  return (
    <Card>
      <CardHeader className="items-center text-center">
        <div className="p-3 bg-green-100 rounded-full">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
        </div>
        <CardTitle className="mt-4">Results Ready to Share</CardTitle>
        <CardDescription>Copy the link below to share these insights with your team.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex space-x-2">
          <Input readOnly value="https://joinbrim.ai/results/123xyz" />
          <Button onClick={handleCopyLink}>Copy Link</Button>
        </div>
      </CardContent>
      <CardFooter>
        <Button variant="outline" onClick={onReset} className="w-full">
          Analyze Another File
        </Button>
      </CardFooter>
    </Card>
  );
}
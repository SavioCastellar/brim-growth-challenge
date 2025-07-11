'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface ShareCardProps {
  analysisResult: string;
  onRestart: () => void;
  userId: string;
}

export default function ShareCard({ analysisResult, onRestart, userId }: ShareCardProps) {

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
    navigator.clipboard.writeText(analysisResult);
    alert('Link copied to clipboard! You can now share it with others.');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card className="border-2 border-[#153333]/20">
        <CardHeader className="text-center bg-[#C4A51A]/10">
          <CardTitle className="text-2xl font-bold text-[#153333]">
            🎉 Analysis Complete!
          </CardTitle>
          <p className="text-gray-600 mt-2">
            Your file has been successfully analyzed. What would you like to do next?
          </p>
        </CardHeader>
        <CardContent className="p-8">
          <div className="space-y-6">
            {/* Action Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button
                onClick={handleCopyLink}
                className="bg-[#153333] hover:bg-[#153333]/90 text-white py-6 text-lg font-semibold rounded-lg transition-all duration-200 hover:shadow-lg"
              >
                <span className="mr-2">📤</span>
                Share Analysis
              </Button>

              <Button
                onClick={onRestart}
                variant="outline"
                className="border-2 border-[#153333] text-[#153333] hover:bg-[#153333] hover:text-white py-6 text-lg font-semibold rounded-lg transition-all duration-200 hover:shadow-lg"
              >
                <span className="mr-2">🔄</span>
                Analyze Another File
              </Button>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-3 gap-4 mt-8 p-6 bg-[#C4A51A]/10 rounded-lg">
              <div className="text-center">
                <p className="text-2xl font-bold text-[#153333]">1</p>
                <p className="text-sm text-gray-600">File Analyzed</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-[#153333]">94%</p>
                <p className="text-sm text-gray-600">Accuracy</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-[#153333]">3s</p>
                <p className="text-sm text-gray-600">Process Time</p>
              </div>
            </div>

            {/* Additional Options */}
            <div className="text-center pt-4 border-t">
              <p className="text-sm text-gray-600 mb-4">
                Need more advanced analysis features?
              </p>
              <Button
                variant="ghost"
                className="text-[#153333] hover:bg-[#153333]/10"
              >
                Explore Premium Features
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
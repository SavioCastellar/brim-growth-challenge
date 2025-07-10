'use client';

import React, { useEffect, useState } from 'react';
import { Progress } from '@/components/ui/progress';

interface ProcessingResult {
  title: string;
  insights: string[];
}

interface ProcessingSpinnerProps {
  onProcessingComplete: (result: ProcessingResult) => void;
}

export default function ProcessingSpinner({ onProcessingComplete }: ProcessingSpinnerProps) {
  const [progress, setProgress] = useState(13);

  useEffect(() => {
    const timer = setTimeout(() => setProgress(80), 500);

    const processingTimer = setTimeout(() => {
      const mockResult: ProcessingResult = {
        title: "AI Analysis Results",
        insights: [
          "We identified 3 invoices at risk of duplicate payment.",
          "Your SaaS software expense is 15% higher than industry average.",
          "The approval workflow can be automated to save 8 hours/week.",
        ],
      };

      onProcessingComplete(mockResult);

    }, 2500);

    return () => {
      clearTimeout(timer);
      clearTimeout(processingTimer);
    };
  }, [onProcessingComplete]);

  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <p className="text-lg font-semibold mb-4">Analyzing your data...</p>
      <p className="text-sm text-gray-500 mb-6">Our AI is processing your file to extract insights and identify potential issues.</p>
      <Progress value={progress} className="w-[60%]" />
    </div>
  );
}
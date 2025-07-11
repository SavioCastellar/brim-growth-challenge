'use client';

import React, { useEffect } from 'react';
import { Card, CardContent } from '../ui/card';
interface ProcessingSpinnerProps {
  file: File | null;
  onAnalysisComplete: (result: string) => void;
}

export default function ProcessingSpinner({ file, onAnalysisComplete }: ProcessingSpinnerProps) {
  useEffect(() => {
    // Simulate AI analysis with a delay
    const timer = setTimeout(() => {
      const mockAnalysis = generateMockAnalysis(file);
      onAnalysisComplete(mockAnalysis);
    }, 3000);

    return () => clearTimeout(timer);
  }, [file, onAnalysisComplete]);

  const generateMockAnalysis = (file: File | null): string => {
    if (!file) return "No file provided for analysis.";

    const fileType = file.name.toLowerCase().endsWith('.pdf') ? 'PDF' : 'CSV';

    if (fileType === 'PDF') {
      return `Document Analysis Complete:

📄 Document Type: ${fileType}
📊 Key Insights:
• Document contains structured information across multiple sections
• Identified important data patterns and relationships
• Text quality is excellent with clear formatting
• Recommended for further processing and data extraction

🎯 Confidence Score: 94%
⚡ Processing Time: 2.8 seconds

💡 Recommendations:
- Consider OCR processing for enhanced text extraction
- Document appears to contain valuable business intelligence
- Suitable for automated workflow integration`;
    } else {
      return `Data Analysis Complete:

📊 Dataset Type: ${fileType}
📈 Key Statistics:
• Analyzed data structure and quality
• Identified trends and patterns in the dataset
• Data integrity score: 98%
• Suitable for machine learning applications

🎯 Confidence Score: 96%
⚡ Processing Time: 2.3 seconds

💡 Insights:
- Clean dataset with minimal missing values
- Strong correlations detected between key variables
- Recommended for predictive modeling
- Ready for visualization and dashboard creation`;
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardContent className="p-8 text-center">
          <div className="mb-6">
            <div className="animate-pulse-slow">
              <div className="w-16 h-16 bg-[#153333] rounded-full mx-auto mb-4 flex items-center justify-center">
                <svg className="w-8 h-8 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
            </div>

            <h3 className="text-2xl font-bold text-[#2B2B2B] mb-2">
              AI Analysis in Progress
            </h3>

            <p className="text-gray-600 mb-6">
              {file ? `Analyzing ${file.name}...` : "Processing your file..."}
            </p>

            <div className="space-y-3">
              <div className="flex items-center justify-center space-x-2">
                <div className="w-2 h-2 bg-[#153333] rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-[#153333] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-[#153333] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>

              <div className="text-sm text-gray-500 space-y-1">
                <p>🔍 Scanning file structure...</p>
                <p>🧠 Running AI analysis...</p>
                <p>📊 Generating insights...</p>
              </div>
            </div>
          </div>

          <div className="bg-[#C4A51A]/20 p-4 rounded-lg">
            <p className="text-sm text-[#153333] font-medium">
              This may take a few moments depending on file size and complexity
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
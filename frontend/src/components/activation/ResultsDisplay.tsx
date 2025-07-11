'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface ResultsDisplayProps {
    file: File | null;
    analysisResult: string;
    onNext: () => void;
    userId: string;
}

export default function ResultsDisplay({ file, analysisResult, onNext, userId }: ResultsDisplayProps) {

    useEffect(() => {
        const logResultViewed = async () => {
            try {
                await fetch('/api/activation/log-event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        step_name: 'result_viewed',
                    }),
                });
                console.log("Event 'result_viewed' registered.");
            } catch (error) {
                console.error("Fail to register event:", error);
            }
        };

        logResultViewed();
    }, [userId]);

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Analysis Results Card */}
            <Card className="border-[#153333]/20">
                <CardHeader className="bg-[#153333]/5">
                    <CardTitle className="text-xl font-bold text-[#153333] flex items-center gap-2">
                        <span>🤖</span>
                        AI Analysis Results
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                    <div className="bg-white rounded-lg p-6 border">
                        <pre className="whitespace-pre-wrap text-[#2B2B2B] leading-relaxed font-medium">
                            {analysisResult}
                        </pre>
                    </div>
                </CardContent>
            </Card>

            {/* File Preview Card */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg font-semibold text-[#2B2B2B] flex items-center gap-2">
                        <span>📄</span>
                        File Preview
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                    {file && (
                        <div className="bg-gray-50 rounded-lg p-6 border-2 border-dashed border-gray-200">
                            <div className="flex items-center space-x-4">
                                <div className="w-12 h-12 bg-[#153333] rounded-lg flex items-center justify-center">
                                    <span className="text-white font-bold text-lg">
                                        {file.name.split('.').pop()?.toUpperCase()}
                                    </span>
                                </div>
                                <div className="flex-1">
                                    <h3 className="font-semibold text-[#2B2B2B]">{file.name}</h3>
                                    <p className="text-sm text-gray-600">
                                        Size: {(file.size / 1024 / 1024).toFixed(2)} MB
                                    </p>
                                    <p className="text-sm text-gray-600">
                                        Type: {file.type || 'Unknown'}
                                    </p>
                                </div>
                            </div>

                            <div className="mt-4 p-4 bg-white rounded border">
                                <p className="text-sm text-gray-600 text-center">
                                    {file.name.toLowerCase().endsWith('.pdf')
                                        ? '📄 PDF document ready for processing'
                                        : '📊 CSV data file successfully uploaded'}
                                </p>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Next Button */}
            <div className="text-center">
                <Button
                    onClick={onNext}
                    className="bg-[#153333] hover:bg-[#153333]/90 text-white px-8 py-3 text-lg"
                >
                    Continue to Share Options
                </Button>
            </div>
        </div>
    );
};
'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface ProcessingResult {
    title: string;
    insights: string[];
}

interface ResultsDisplayProps {
    result: ProcessingResult | null;
    fileName?: string;
    onShare: () => void;
    userId: string;
}

export default function ResultsDisplay({ result, fileName, onShare, userId }: ResultsDisplayProps) {

    useEffect(() => {
        const logResultViewed = async () => {
            try {
                await fetch('/api/activation/log-event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        step_name: 'result_viewed',
                        metadata: { insights_count: result?.insights.length || 0 }
                    }),
                });
                console.log("Event 'result_viewed' registered.");
            } catch (error) {
                console.error("Fail to register event:", error);
            }
        };

        logResultViewed();
    }, [result, userId]);

    if (!result) {
        return <p>Loading results...</p>;
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>{result.title}</CardTitle>
                {fileName && <CardDescription>Results for: {fileName}</CardDescription>}
            </CardHeader>
            <CardContent>
                <ul className="space-y-2 list-disc pl-5">
                    {result.insights.map((insight, index) => (
                        <li key={index} className="text-gray-700">{insight}</li>
                    ))}
                </ul>
            </CardContent>
            <CardFooter>
                <Button onClick={onShare} className="w-full">
                    Share Results
                </Button>
            </CardFooter>
        </Card>
    );
}
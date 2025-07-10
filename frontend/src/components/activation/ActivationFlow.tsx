'use client';

import React, { useState } from 'react';
import FileUpload from './FileUpload';
import ProcessingSpinner from './ProcessingSpinner';
import ResultsDisplay from './ResultsDisplay';
import ShareCard from './ShareCard';

interface ProcessingResult {
    title: string;
    insights: string[];
}

const generateUserId = () => `user_${Math.random().toString(36).substring(2, 11)}`

export default function ActivationFlow() {
    const [step, setStep] = useState<number>(1);
    const [file, setFile] = useState<File | null>(null);

    const [userId] = useState<string>(() => generateUserId());

    const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null);

    const handleFileSelect = (selectedFile: File) => {
        setFile(selectedFile);
        console.log("File selected:", selectedFile.name);
        setStep(2);
    };

    const handleProcessingComplete = (result: ProcessingResult) => {
        setProcessingResult(result);
        setStep(3);
    };

    const handleShare = () => {
        console.log("Share action!");
        setStep(4);
    };

    const handleReset = () => {
        setStep(1);
        setFile(null);
        setProcessingResult(null);
    };

    const renderCurrentStep = () => {
        switch (step) {
            case 1:
                return <FileUpload onFileSelect={handleFileSelect} userId={userId} />;
            case 2:
                return <ProcessingSpinner onProcessingComplete={handleProcessingComplete} />;
            case 3:
                return <ResultsDisplay result={processingResult} fileName={file?.name} onShare={handleShare} userId={userId}/>;
            case 4:
                return <ShareCard onReset={handleReset} userId={userId}/>;
            default:
                return <FileUpload onFileSelect={handleFileSelect} userId={userId}/>;
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto mt-8">
            {renderCurrentStep()}
        </div>
    );
}
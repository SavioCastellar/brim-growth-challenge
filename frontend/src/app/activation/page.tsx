'use client';

import { useState } from "react";
import FileUpload from "@/components/activation/FileUpload";
import ProgressIndicator from "@/components/activation/ProgressIndicator";
import ProcessingSpinner from "@/components/activation/ProcessingSpinner";
import ResultsDisplay from "@/components/activation/ResultsDisplay";
import ShareCard from "@/components/activation/ShareCard";
import Image from "next/image";

const generateUserId = () => `user_${Math.random().toString(36).substring(2, 11)}`

const Index = () => {
    const [currentStep, setCurrentStep] = useState<number>(1);
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [analysisResult, setAnalysisResult] = useState<string>("");

    const [userId] = useState<string>(() => generateUserId());

    const handleFileUpload = (file: File) => {
        setUploadedFile(file);
        setCurrentStep(2);
    };

    const handleAnalysisComplete = (result: string) => {
        setAnalysisResult(result);
        setCurrentStep(3);
    };

    const handleNextStep = () => {
        setCurrentStep(currentStep + 1);
    };

    const handleRestart = () => {
        setCurrentStep(1);
        setUploadedFile(null);
        setAnalysisResult("");
    };

    return (
        <div className="min-h-screen bg-[#F4EFE1]">
            <div className="py-6 pl-12">
                <Image src="/brim.svg" alt="Logo" width={100} height={20} />
            </div>
            <div className="container mx-auto px-4 pb-8 max-w-4xl">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-[#2B2B2B] mb-2">
                        AI File Analyzer
                    </h1>
                    <p className="text-lg text-[#2B2B2B]/70">
                        Upload your files and let AI provide intelligent analysis
                    </p>
                </div>

                <ProgressIndicator currentStep={currentStep} />

                <div className="mt-8 animate-fade-in">
                    {currentStep === 1 && (
                        <FileUpload onFileUpload={handleFileUpload} userId={userId} />
                    )}
                    {currentStep === 2 && (
                        <ProcessingSpinner
                            file={uploadedFile}
                            onAnalysisComplete={handleAnalysisComplete}
                        />
                    )}
                    {currentStep === 3 && (
                        <ResultsDisplay
                            file={uploadedFile}
                            analysisResult={analysisResult}
                            onNext={handleNextStep}
                            userId={userId}
                            />
                        )}
                    {currentStep === 4 && (
                        <ShareCard
                            analysisResult={analysisResult}
                            onRestart={handleRestart}
                            userId={userId}
                        />
                    )}
                </div>
            </div>
        </div>
    );
};

export default Index;
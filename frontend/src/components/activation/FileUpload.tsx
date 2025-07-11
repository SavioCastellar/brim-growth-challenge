'use client';

import { useState, useRef } from "react";
import { Card, CardContent } from "../ui/card";
import { Button } from "../ui/button";

interface FileUploadProps {
    onFileUpload: (file: File) => void;
    userId: string;
}

export default function FileUpload({ onFileUpload, userId }: FileUploadProps) {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    const fileInputRef = useRef<HTMLInputElement>(null);

    const allowedTypes = ['.csv', '.pdf'];
    const allowedMimeTypes = ['text/csv', 'application/pdf'];

    const validateFile = (file: File): boolean => {
        const isValidType = allowedMimeTypes.includes(file.type) ||
            allowedTypes.some(type => file.name.toLowerCase().endsWith(type));

        if (!isValidType) {
            setError("Please upload only CSV or PDF files.");
            return false;
        }

        setError("");
        return true;
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0];
            if (validateFile(file)) {
                setSelectedFile(file);
            }
        }
    };

    const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            if (validateFile(file)) {
                setIsUploading(true);
                try {
                    await fetch('/api/activation/log-event', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: userId,
                            step_name: 'file_upload',
                            metadata: {
                                file_name: file.name,
                                file_size: file.size,
                                file_type: file.type,
                            },
                        }),
                    });
                    setIsUploading(false);
                    setSelectedFile(file);

                } catch (e) {
                    setError(`${e} It was not possible to register the upload event. Try again.`);
                    setIsUploading(false);
                }
            }
        }
    };

    const handleButtonClick = () => {
        fileInputRef.current?.click();
    };

    const handleNext = () => {
        if (selectedFile) {
            onFileUpload(selectedFile);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <Card className="border-2 border-dashed border-gray-300 hover:border-[#153333] transition-colors duration-300">
                <CardContent className="p-8">
                    <div
                        className={`text-center cursor-pointer transition-all duration-300 ${dragActive ? 'scale-105' : ''
                            }`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <div className="mb-6">
                            <svg
                                className="mx-auto h-16 w-16 text-gray-400 mb-4"
                                stroke="currentColor"
                                fill="none"
                                viewBox="0 0 48 48"
                            >
                                <path
                                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                                    strokeWidth={2}
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                            </svg>

                            <h3 className="text-xl font-semibold text-[#2B2B2B] mb-2">
                                {selectedFile ? "File Selected!" : "Upload Your File"}
                            </h3>

                            {selectedFile ? (
                                <div className="bg-[#C4A51A]/20 p-4 rounded-lg mb-4">
                                    <p className="text-[#153333] font-medium">{selectedFile.name}</p>
                                    <p className="text-sm text-gray-600">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                                </div>
                            ) : (
                                <p className="text-gray-600 mb-4">
                                    Drag and drop your file here, or click to browse
                                </p>
                            )}

                            <p className="text-sm text-gray-500 mb-6">
                                Supported formats: CSV, PDF (Max size: 10MB)
                            </p>
                        </div>

                        <input
                            ref={fileInputRef}
                            type="file"
                            className="hidden"
                            accept=".csv,.pdf"
                            onChange={handleChange}
                        />
                        {isUploading && (
                            <h3 className="text-sm text-gray-600 mb-4">Loading file...</h3>
                        )}
                        <Button
                            onClick={handleButtonClick}
                            variant="outline"
                            className="border-[#153333] text-[#153333] hover:bg-[#153333] hover:text-white"
                        >
                            Choose File
                        </Button>
                    </div>

                    {error && (
                        <p className="mt-4 text-sm text-red-600 bg-red-100 p-2 rounded-md">{error}</p>
                    )}

                    {selectedFile && (
                        <div className="mt-6 text-center">
                            <Button
                                onClick={handleNext}
                                className="bg-[#153333] hover:bg-[#153333]/90 text-white px-8 py-2"
                            >
                                Next Step
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
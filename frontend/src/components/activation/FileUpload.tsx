'use client';

import React, { useState } from 'react';
import { Input } from '../ui/input';

interface FileUploadProps {
    onFileSelect: (file: File) => void;
    userId: string;
}

export default function FileUpload({ onFileSelect, userId  }: FileUploadProps) {
    const [error, setError] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState<boolean>(false);

    const handleFileValidation = (file: File): boolean => {
        const MAX_CSV_SIZE = 1 * 1024 * 1024; // 1MB
        const MAX_PDF_SIZE = 5 * 1024 * 1024; // 5MB

        if (file.type === 'text/csv' && file.size > MAX_CSV_SIZE) {
            setError(`O arquivo CSV excede o limite de 1MB.`);
            return false;
        }

        if (file.type === 'application/pdf' && file.size > MAX_PDF_SIZE) {
            setError(`O arquivo PDF excede o limite de 5MB.`);
            return false;
        }

        if (file.type !== 'text/csv' && file.type !== 'application/pdf') {
            setError('Tipo de arquivo inválido. Por favor, envie um CSV ou PDF.');
            return false;
        }

        setError(null);
        return true;
    };

    const handleFileSelected = async (file: File) => {
        if (handleFileValidation(file)) {
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

                onFileSelect(file);

            } catch (e) {
                setError(`${e} It was not possible to register the upload event. Try again.`);
                setIsUploading(false);
            }
        }
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            handleFileSelected(file);
        }
    };

    return (
        <label htmlFor="file-upload" className={`flex flex-col items-center ... ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="mt-4 text-lg font-semibold">Drag and drop your file here, or click to browse</p>
            <p className="mt-1 text-sm text-gray-500">Supported formats: CSV, PDF (Max size: 1MB)</p>

            <Input
                id="file-upload"
                type="file"
                className="hidden"
                onChange={handleFileChange}
                accept=".csv, application/pdf"
                disabled={isUploading}
            />

            {error && (
                <p className="mt-4 text-sm text-red-600 bg-red-100 p-2 rounded-md">{error}</p>
            )}
        </label>
    );
}
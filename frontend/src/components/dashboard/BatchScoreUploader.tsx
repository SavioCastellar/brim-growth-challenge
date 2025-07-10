'use client';

import { useState } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import Error from 'next/error';

export function BatchScoreUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a JSON file first.");
      return;
    }
    if (file.type !== 'application/json') {
      toast.error("Invalid file type. Only JSON is allowed.");
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // We will create this Next.js API proxy route next
      const response = await fetch('/api/leads/batch-score', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'An unknown error occurred.');
      }

      toast.success("File upload accepted!", {
        description: result.message,
      });

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      toast.error("Upload failed", {
        description: error.message,
      });
    } finally {
      setIsUploading(false);
      setFile(null);
    }
  };

  return (
    <div className="flex flex-col space-y-4">
      <h3 className="text-lg font-medium">Upload Batch JSON</h3>
      <p className="text-sm text-muted-foreground">
        Select a JSON file containing a list of company objects to score them all at once.
      </p>
      <Input type="file" onChange={handleFileChange} accept="application/json" />
      <Button onClick={handleUpload} disabled={!file || isUploading}>
        {isUploading ? "Uploading..." : "Upload and Start Scoring"}
      </Button>
    </div>
  );
}
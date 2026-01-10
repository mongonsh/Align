'use client';

import { useState, useCallback } from 'react';
import { api } from '@/lib/api';

interface UploadViewProps {
  onUploadComplete: (imageId: string, imageFile: File) => void;
  onError: (error: string) => void;
}

export default function UploadView({ onUploadComplete, onError }: UploadViewProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFile = useCallback(async (file: File) => {
    if (!file.type.startsWith('image/')) {
      onError('Please upload an image file');
      return;
    }

    setIsUploading(true);
    setPreview(URL.createObjectURL(file));

    try {
      const response = await api.uploadImage(file);
      onUploadComplete(response.image_id, file);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Upload failed');
      setPreview(null);
    } finally {
      setIsUploading(false);
    }
  }, [onUploadComplete, onError]);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="mb-6 text-center">
        <h2 className="text-3xl font-bold mb-2">Upload Current Screenshot</h2>
        <p className="text-gray-600">Upload a screenshot of your current system to get started</p>
      </div>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center
          transition-colors cursor-pointer
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        {preview ? (
          <div className="space-y-4">
            <img src={preview} alt="Preview" className="max-h-64 mx-auto rounded" />
            {isUploading && <p className="text-blue-600">Uploading...</p>}
          </div>
        ) : (
          <div className="space-y-4">
            <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <div>
              <label htmlFor="file-upload" className="cursor-pointer">
                <span className="text-blue-600 hover:text-blue-500 font-medium">Upload a file</span>
                <input
                  id="file-upload"
                  type="file"
                  className="sr-only"
                  accept="image/*"
                  onChange={handleFileInput}
                  disabled={isUploading}
                />
              </label>
              <p className="text-gray-500"> or drag and drop</p>
            </div>
            <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
          </div>
        )}
      </div>
    </div>
  );
}

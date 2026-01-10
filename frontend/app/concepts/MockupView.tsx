'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface MockupViewProps {
  imageId: string;
  imageFile: File | null;
  description: string;
  requirements: any;
  onMockupGenerated: (mockupId: string, mockupHtml: string) => void;
  onError: (error: string) => void;
}

export default function MockupView({
  imageId,
  imageFile,
  description,
  requirements,
  onMockupGenerated,
  onError,
}: MockupViewProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [mockupId, setMockupId] = useState<string | null>(null);
  const [mockupHtml, setMockupHtml] = useState<string | null>(null);

  useEffect(() => {
    generateMockup();
  }, []);

  const generateMockup = async () => {
    setIsGenerating(true);
    setProgress(0);

    const progressInterval = setInterval(() => {
      setProgress((prev) => Math.min(prev + 10, 90));
    }, 300);

    try {
      const response = await api.generateMockup(imageId, description, requirements);
      setProgress(100);
      setMockupId(response.mockup_id);
      setMockupHtml(response.html);
      onMockupGenerated(response.mockup_id, response.html);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Failed to generate mockup');
    } finally {
      clearInterval(progressInterval);
      setIsGenerating(false);
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto">
      <div className="mb-6 text-center">
        <h2 className="text-3xl font-bold mb-2">Generated Mockup</h2>
        <p className="text-gray-600">Side-by-side comparison of original and mockup</p>
      </div>

      {isGenerating ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-4"></div>
          <p className="text-lg font-medium mb-2">Generating mockup...</p>
          <div className="w-full max-w-md mx-auto bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">{progress}% complete</p>
        </div>
      ) : mockupHtml ? (
        <div>
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800">
              <strong>Mockup generated successfully!</strong> Review the changes below.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3 text-lg">Original Screenshot</h3>
              <div className="border-2 border-gray-300 rounded-lg overflow-hidden bg-white">
                {imageFile && (
                  <img
                    src={URL.createObjectURL(imageFile)}
                    alt="Original"
                    className="w-full"
                  />
                )}
              </div>
              <p className="text-sm text-gray-500 mt-2">Before changes</p>
            </div>

            <div>
              <h3 className="font-semibold mb-3 text-lg">Generated Mockup</h3>
              <div className="border-2 border-blue-500 rounded-lg overflow-hidden bg-white">
                <iframe
                  srcDoc={mockupHtml}
                  className="w-full h-96 border-0"
                  sandbox="allow-same-origin"
                  title="Mockup Preview"
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">After changes</p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-2">Your Request:</h4>
            <p className="text-gray-700">{description}</p>
          </div>
        </div>
      ) : null}
    </div>
  );
}

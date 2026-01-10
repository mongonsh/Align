'use client';

import { api } from '@/lib/api';

interface ExportViewProps {
  mockupId: string;
  mockupHtml: string;
  description: string;
  onReset: () => void;
}

export default function ExportView({ mockupId, mockupHtml, description, onReset }: ExportViewProps) {
  const handleDownload = (format: 'html' | 'zip') => {
    const url = api.getDownloadUrl(mockupId, format);
    window.open(url, '_blank');
  };

  const handlePreview = () => {
    const url = api.getPreviewUrl(mockupId);
    window.open(url, '_blank');
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(mockupHtml);
      alert('HTML copied to clipboard!');
    } catch (error) {
      alert('Failed to copy HTML');
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="mb-6 text-center">
        <h2 className="text-3xl font-bold mb-2">Export & Share</h2>
        <p className="text-gray-600">Download or share your mockup with your team</p>
      </div>

      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-8 mb-6 border border-green-200">
        <div className="flex items-center justify-center mb-4">
          <svg className="h-16 w-16 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-2xl font-bold text-center mb-2">Mockup Ready!</h3>
        <p className="text-center text-gray-700 mb-4">Your mockup has been generated successfully</p>
        <div className="bg-white rounded p-4 text-sm">
          <p className="text-gray-600 mb-1"><strong>Request:</strong></p>
          <p className="text-gray-800">{description}</p>
          <p className="text-gray-500 mt-2 text-xs">Mockup ID: {mockupId}</p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <button
          onClick={() => handleDownload('html')}
          className="flex items-center justify-center gap-2 p-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download HTML
        </button>

        <button
          onClick={() => handleDownload('zip')}
          className="flex items-center justify-center gap-2 p-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-colors"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download ZIP Package
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <button
          onClick={handlePreview}
          className="flex items-center justify-center gap-2 p-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          Full Page Preview
        </button>

        <button
          onClick={copyToClipboard}
          className="flex items-center justify-center gap-2 p-4 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition-colors"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          Copy HTML
        </button>
      </div>

      <div className="border-t pt-6">
        <h4 className="font-semibold mb-3">Next Steps:</h4>
        <ul className="space-y-2 text-sm text-gray-700 mb-6">
          <li className="flex items-start gap-2">
            <span className="text-blue-600 font-bold">1.</span>
            <span>Download the mockup and share it with your team</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 font-bold">2.</span>
            <span>Get approval from all stakeholders</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 font-bold">3.</span>
            <span>Engineers build exactly what was approved - no miscommunication!</span>
          </li>
        </ul>

        <button
          onClick={onReset}
          className="w-full p-3 border-2 border-gray-300 hover:border-gray-400 text-gray-700 rounded-lg font-semibold transition-colors"
        >
          Create Another Mockup
        </button>
      </div>
    </div>
  );
}

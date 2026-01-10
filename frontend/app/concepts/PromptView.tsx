'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

interface PromptViewProps {
  imageId: string;
  imageFile: File | null;
  onSubmit: (description: string, requirements: any) => void;
  onError: (error: string) => void;
}

export default function PromptView({ imageId, imageFile, onSubmit, onError }: PromptViewProps) {
  const [description, setDescription] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [requirements, setRequirements] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!description.trim()) {
      onError('Please describe the changes you want');
      return;
    }

    setIsProcessing(true);

    try {
      const response = await api.parsePrompt(imageId, description);
      setRequirements(response.requirements);
      onSubmit(description, response.requirements);
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Failed to parse prompt');
    } finally {
      setIsProcessing(false);
    }
  };

  const examples = [
    "Make the header dark blue and add a search bar in the top right corner",
    "Add a dashboard card showing user statistics on the left side",
    "Change the sidebar to be collapsible and add icons to menu items",
    "Update the button style to be rounded with a gradient background",
  ];

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="mb-6 text-center">
        <h2 className="text-3xl font-bold mb-2">Describe Your Changes</h2>
        <p className="text-gray-600">Tell us what you want to change in plain English</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {imageFile && (
          <div>
            <h3 className="font-semibold mb-2">Current Screenshot</h3>
            <img
              src={URL.createObjectURL(imageFile)}
              alt="Current"
              className="w-full rounded-lg border-2 border-gray-200"
            />
          </div>
        )}

        <div>
          <h3 className="font-semibold mb-2">Example Prompts</h3>
          <div className="space-y-2">
            {examples.map((example, idx) => (
              <button
                key={idx}
                onClick={() => setDescription(example)}
                className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="description" className="block text-sm font-medium mb-2">
            Describe the changes you want
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="e.g., Make the header dark blue and add a search bar in the top right corner"
            disabled={isProcessing}
          />
        </div>

        {requirements && (
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="font-semibold text-blue-900 mb-2">Understood:</h4>
            <ul className="space-y-1 text-sm text-blue-800">
              <li>Action: {requirements.action_type}</li>
              <li>Targets: {requirements.targets.join(', ')}</li>
              {Object.keys(requirements.properties).length > 0 && (
                <li>Properties: {JSON.stringify(requirements.properties)}</li>
              )}
            </ul>
          </div>
        )}

        <button
          type="submit"
          disabled={isProcessing || !description.trim()}
          className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold rounded-lg transition-colors"
        >
          {isProcessing ? 'Processing...' : 'Generate Mockup'}
        </button>
      </form>
    </div>
  );
}

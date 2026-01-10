'use client';

import { useReducer } from 'react';
import { alignReducer, initialState } from '@/lib/stores/alignStore';
import UploadView from './concepts/UploadView';
import PromptView from './concepts/PromptView';
import MockupView from './concepts/MockupView';
import ExportView from './concepts/ExportView';

export default function Home() {
  const [state, dispatch] = useReducer(alignReducer, initialState);

  const handleUploadComplete = (imageId: string, imageFile: File) => {
    dispatch({ type: 'SET_IMAGE', imageId, imageFile });
  };

  const handlePromptSubmit = (description: string, requirements: any) => {
    dispatch({ type: 'SET_DESCRIPTION', description });
    dispatch({ type: 'SET_REQUIREMENTS', requirements });
    dispatch({ type: 'SET_STEP', step: 'generate' });
  };

  const handleMockupGenerated = (mockupId: string, mockupHtml: string) => {
    dispatch({ type: 'SET_MOCKUP', mockupId, mockupHtml });
  };

  const handleError = (error: string) => {
    dispatch({ type: 'SET_ERROR', error });
  };

  const handleReset = () => {
    dispatch({ type: 'RESET' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Align</h1>
                <p className="text-xs text-gray-500">AI-Powered Mockup Generator</p>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Built for De-Vibed Hackathon
            </div>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-center gap-4">
            {[
              { key: 'upload', label: 'Upload' },
              { key: 'prompt', label: 'Describe' },
              { key: 'generate', label: 'Generate' },
              { key: 'export', label: 'Export' },
            ].map((step, idx) => (
              <div key={step.key} className="flex items-center">
                <div className="flex items-center gap-2">
                  <div
                    className={`
                      w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm
                      ${
                        state.currentStep === step.key
                          ? 'bg-blue-600 text-white'
                          : ['upload', 'prompt', 'generate', 'export'].indexOf(state.currentStep) >
                            ['upload', 'prompt', 'generate', 'export'].indexOf(step.key)
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-200 text-gray-600'
                      }
                    `}
                  >
                    {['upload', 'prompt', 'generate', 'export'].indexOf(state.currentStep) >
                    ['upload', 'prompt', 'generate', 'export'].indexOf(step.key) ? (
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    ) : (
                      idx + 1
                    )}
                  </div>
                  <span
                    className={`
                      text-sm font-medium
                      ${state.currentStep === step.key ? 'text-blue-600' : 'text-gray-600'}
                    `}
                  >
                    {step.label}
                  </span>
                </div>
                {idx < 3 && (
                  <div className="w-12 h-0.5 bg-gray-200 mx-2" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Error Display */}
      {state.error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="text-red-800">{state.error}</span>
            </div>
            <button
              onClick={() => dispatch({ type: 'SET_ERROR', error: null })}
              className="text-red-600 hover:text-red-800"
            >
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {state.currentStep === 'upload' && (
          <UploadView onUploadComplete={handleUploadComplete} onError={handleError} />
        )}

        {state.currentStep === 'prompt' && state.imageId && (
          <PromptView
            imageId={state.imageId}
            imageFile={state.imageFile}
            onSubmit={handlePromptSubmit}
            onError={handleError}
          />
        )}

        {state.currentStep === 'generate' && state.imageId && state.description && (
          <MockupView
            imageId={state.imageId}
            imageFile={state.imageFile}
            description={state.description}
            requirements={state.requirements}
            onMockupGenerated={handleMockupGenerated}
            onError={handleError}
          />
        )}

        {state.currentStep === 'export' && state.mockupId && state.mockupHtml && (
          <ExportView
            mockupId={state.mockupId}
            mockupHtml={state.mockupHtml}
            description={state.description}
            onReset={handleReset}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p className="mb-2">
              <strong>Align</strong> - Align customer and engineer expectations before coding starts
            </p>
            <p>Built with concept-based design for the De-Vibed Hackathon</p>
            <p className="mt-2">Sponsored by CommandCenter (cc.dev)</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

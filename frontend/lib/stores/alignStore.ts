/**
 * State management for Align application
 * Using simple React state pattern (no external library needed for MVP)
 */

export type AlignStep = 'upload' | 'prompt' | 'generate' | 'export';

export interface AlignState {
  currentStep: AlignStep;
  imageId: string | null;
  imageFile: File | null;
  description: string;
  requirements: any | null;
  mockupId: string | null;
  mockupHtml: string | null;
  isLoading: boolean;
  error: string | null;
}

export const initialState: AlignState = {
  currentStep: 'upload',
  imageId: null,
  imageFile: null,
  description: '',
  requirements: null,
  mockupId: null,
  mockupHtml: null,
  isLoading: false,
  error: null,
};

export type AlignAction =
  | { type: 'SET_STEP'; step: AlignStep }
  | { type: 'SET_IMAGE'; imageId: string; imageFile: File }
  | { type: 'SET_DESCRIPTION'; description: string }
  | { type: 'SET_REQUIREMENTS'; requirements: any }
  | { type: 'SET_MOCKUP'; mockupId: string; mockupHtml: string }
  | { type: 'SET_LOADING'; isLoading: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'RESET' };

export function alignReducer(state: AlignState, action: AlignAction): AlignState {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, currentStep: action.step };
    case 'SET_IMAGE':
      return { ...state, imageId: action.imageId, imageFile: action.imageFile, currentStep: 'prompt' };
    case 'SET_DESCRIPTION':
      return { ...state, description: action.description };
    case 'SET_REQUIREMENTS':
      return { ...state, requirements: action.requirements };
    case 'SET_MOCKUP':
      return { ...state, mockupId: action.mockupId, mockupHtml: action.mockupHtml, currentStep: 'export' };
    case 'SET_LOADING':
      return { ...state, isLoading: action.isLoading };
    case 'SET_ERROR':
      return { ...state, error: action.error, isLoading: false };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

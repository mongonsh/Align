/**
 * API client for Align backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface UploadResponse {
  image_id: string;
  preview_url: string;
  metadata: {
    filename: string;
    size: number;
    width: number;
    height: number;
  };
}

export interface Requirements {
  raw_prompt: string;
  action_type: string;
  targets: string[];
  properties: Record<string, any>;
  clarifications: string[];
}

export interface PromptResponse {
  image_id: string;
  requirements: Requirements;
  clarifications: string[];
  summary: string;
}

export interface MockupResponse {
  mockup_id: string;
  html: string;
  download_url: string;
  preview_url: string;
  exported_at: string;
}

export interface MockupData {
  mockup_id: string;
  html: string;
  created_at: string;
  status: string;
  prompt: string;
}

export const api = {
  async uploadImage(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header for FormData - let browser set it with boundary
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Upload failed: ${response.statusText} - ${errorText}`);
    }

    return response.json();
  },

  async parsePrompt(imageId: string, description: string): Promise<PromptResponse> {
    const response = await fetch(`${API_BASE_URL}/api/prompt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_id: imageId,
        description,
      }),
    });

    if (!response.ok) {
      throw new Error(`Prompt parsing failed: ${response.statusText}`);
    }

    return response.json();
  },

  async generateMockup(imageId: string, description: string, requirements?: Requirements): Promise<MockupResponse> {
    const response = await fetch(`${API_BASE_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_id: imageId,
        description,
        requirements,
      }),
    });

    if (!response.ok) {
      throw new Error(`Mockup generation failed: ${response.statusText}`);
    }

    return response.json();
  },

  async getMockup(mockupId: string): Promise<MockupData> {
    const response = await fetch(`${API_BASE_URL}/api/mockup/${mockupId}`);

    if (!response.ok) {
      throw new Error(`Failed to get mockup: ${response.statusText}`);
    }

    return response.json();
  },

  getImageUrl(imageId: string): string {
    return `${API_BASE_URL}/api/image/${imageId}`;
  },

  getPreviewUrl(mockupId: string): string {
    return `${API_BASE_URL}/api/mockup/${mockupId}/preview`;
  },

  getDownloadUrl(mockupId: string, format: string = 'html'): string {
    return `${API_BASE_URL}/api/export/${mockupId}?format=${format}`;
  },
};

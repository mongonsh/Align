/**
 * Align Chrome Extension - Popup Script
 * Handles UI interactions and communication with background script
 */

class AlignExtensionPopup {
  constructor() {
    this.apiUrl = 'http://localhost:8000'; // Will be configurable
    this.currentStep = 1;
    this.captureId = null;
    this.partnerTeamId = null;
    
    this.init();
  }

  async init() {
    // Load saved settings
    const settings = await chrome.storage.sync.get(['apiUrl', 'partnerTeamId', 'apiKey']);
    if (settings.apiUrl) this.apiUrl = settings.apiUrl;
    if (settings.partnerTeamId) this.partnerTeamId = settings.partnerTeamId;
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Check partner connection
    await this.checkPartnerConnection();
    
    // Check if we're in the middle of a workflow
    await this.checkWorkflowState();
  }

  setupEventListeners() {
    // Main action buttons
    document.getElementById('capture-btn').addEventListener('click', () => {
      this.startCaptureWorkflow();
    });
    
    document.getElementById('quick-feedback-btn').addEventListener('click', () => {
      this.openQuickFeedback();
    });
    
    document.getElementById('view-mockups-btn').addEventListener('click', () => {
      this.openMockupViewer();
    });
    
    // Quick action buttons
    document.getElementById('retry-btn').addEventListener('click', () => {
      this.retryCurrentStep();
    });
    
    document.getElementById('reset-btn').addEventListener('click', () => {
      this.resetWorkflow();
    });
  }

  async startCaptureWorkflow() {
    try {
      this.showStatus('Capturing screenshot...', 'loading');
      this.showWorkflowSteps();
      this.updateStep(1, 'current');
      
      // Get current tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Capture screenshot
      const screenshot = await chrome.tabs.captureVisibleTab(null, {
        format: 'png',
        quality: 90
      });
      
      // Send to background script for processing
      const response = await chrome.runtime.sendMessage({
        action: 'captureScreenshot',
        data: {
          screenshot: screenshot,
          url: tab.url,
          title: tab.title
        }
      });
      
      if (response.success) {
        this.captureId = response.captureId;
        this.updateStep(1, 'completed');
        this.updateStep(2, 'current');
        this.showDescriptionInput();
      } else {
        throw new Error(response.error || 'Capture failed');
      }
      
    } catch (error) {
      this.showStatus(`Error: ${error.message}`, 'error');
      this.showQuickActions();
    }
  }

  showDescriptionInput() {
    // Create description input overlay
    const overlay = document.createElement('div');
    overlay.innerHTML = `
      <div style="margin: 15px 0;">
        <label style="display: block; margin-bottom: 5px; font-weight: 500;">
          Describe the changes you want:
        </label>
        <textarea 
          id="description-input" 
          placeholder="e.g., Make the button blue and add a search icon..."
          style="width: 100%; height: 60px; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; resize: none; font-size: 12px;"
        ></textarea>
        <div style="display: flex; gap: 8px; margin-top: 8px;">
          <button id="generate-btn" class="action-button primary" style="flex: 1;">
            ✨ Generate Mockup
          </button>
          <button id="voice-btn" class="action-button secondary" style="width: 40px;">
            🎤
          </button>
        </div>
      </div>
    `;
    
    // Replace main actions with description input
    const mainActions = document.getElementById('main-actions');
    mainActions.innerHTML = '';
    mainActions.appendChild(overlay);
    
    // Setup new event listeners
    document.getElementById('generate-btn').addEventListener('click', () => {
      const description = document.getElementById('description-input').value.trim();
      if (description) {
        this.generateMockup(description);
      } else {
        this.showStatus('Please describe the changes you want', 'error');
      }
    });
    
    document.getElementById('voice-btn').addEventListener('click', () => {
      this.startVoiceInput();
    });
    
    // Focus on textarea
    document.getElementById('description-input').focus();
  }

  async generateMockup(description) {
    try {
      this.showStatus('Generating mockup with AI...', 'loading');
      this.updateStep(2, 'completed');
      this.updateStep(3, 'current');
      
      const response = await chrome.runtime.sendMessage({
        action: 'generateMockup',
        data: {
          captureId: this.captureId,
          description: description
        }
      });
      
      if (response.success) {
        this.updateStep(3, 'completed');
        this.updateStep(4, 'current');
        this.showMockupResult(response.mockup);
        
        // Notify partner team if connected
        if (this.partnerTeamId) {
          await this.notifyPartnerTeam('mockup_generated', response.mockup);
        }
      } else {
        throw new Error(response.error || 'Generation failed');
      }
      
    } catch (error) {
      this.showStatus(`Error: ${error.message}`, 'error');
      this.showQuickActions();
    }
  }

  showMockupResult(mockup) {
    const resultHtml = `
      <div style="margin: 15px 0;">
        <div style="text-align: center; margin-bottom: 10px;">
          <strong style="color: #10b981;">✅ Mockup Generated!</strong>
        </div>
        
        <div style="display: flex; gap: 8px; margin-bottom: 10px;">
          <button id="preview-btn" class="action-button primary" style="flex: 1;">
            👁️ Preview
          </button>
          <button id="download-btn" class="action-button secondary" style="flex: 1;">
            💾 Download
          </button>
        </div>
        
        <div style="display: flex; gap: 8px;">
          <button id="share-btn" class="action-button secondary" style="flex: 1;">
            🔗 Share Link
          </button>
          <button id="collaborate-btn" class="action-button secondary" style="flex: 1;">
            👥 Collaborate
          </button>
        </div>
      </div>
    `;
    
    const mainActions = document.getElementById('main-actions');
    mainActions.innerHTML = resultHtml;
    
    // Setup result action listeners
    document.getElementById('preview-btn').addEventListener('click', () => {
      this.previewMockup(mockup);
    });
    
    document.getElementById('download-btn').addEventListener('click', () => {
      this.downloadMockup(mockup);
    });
    
    document.getElementById('share-btn').addEventListener('click', () => {
      this.shareMockup(mockup);
    });
    
    document.getElementById('collaborate-btn').addEventListener('click', () => {
      this.startCollaboration(mockup);
    });
    
    this.showStatus('Mockup ready! Choose an action below.', 'success');
  }

  async previewMockup(mockup) {
    // Open mockup in new tab
    const previewUrl = `${this.apiUrl}/api/mockup/${mockup.mockup_id}/preview`;
    await chrome.tabs.create({ url: previewUrl });
  }

  async downloadMockup(mockup) {
    // Trigger download
    const downloadUrl = `${this.apiUrl}/api/export/${mockup.mockup_id}`;
    await chrome.downloads.download({ url: downloadUrl });
    
    this.showStatus('Download started!', 'success');
  }

  async shareMockup(mockup) {
    // Copy share link to clipboard
    const shareUrl = `${this.apiUrl}/mockup/${mockup.mockup_id}`;
    
    try {
      await navigator.clipboard.writeText(shareUrl);
      this.showStatus('Share link copied to clipboard!', 'success');
    } catch (error) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = shareUrl;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      
      this.showStatus('Share link copied!', 'success');
    }
  }

  async startCollaboration(mockup) {
    try {
      const response = await chrome.runtime.sendMessage({
        action: 'startCollaboration',
        data: {
          mockupId: mockup.mockup_id,
          partnerTeamId: this.partnerTeamId
        }
      });
      
      if (response.success) {
        const collaborationUrl = `${this.apiUrl}/collaborate/${response.sessionId}`;
        await chrome.tabs.create({ url: collaborationUrl });
        
        this.showStatus('Collaboration session started!', 'success');
      } else {
        throw new Error(response.error || 'Failed to start collaboration');
      }
    } catch (error) {
      this.showStatus(`Error: ${error.message}`, 'error');
    }
  }

  async startVoiceInput() {
    // This would integrate with Web Speech API
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      this.showStatus('Voice input not supported in this browser', 'error');
      return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onstart = () => {
      document.getElementById('voice-btn').textContent = '🔴';
      this.showStatus('Listening... Speak now!', 'loading');
    };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById('description-input').value = transcript;
      this.showStatus('Voice input captured!', 'success');
    };
    
    recognition.onerror = (event) => {
      this.showStatus(`Voice error: ${event.error}`, 'error');
    };
    
    recognition.onend = () => {
      document.getElementById('voice-btn').textContent = '🎤';
    };
    
    recognition.start();
  }

  async checkPartnerConnection() {
    try {
      const response = await chrome.runtime.sendMessage({
        action: 'checkPartnerConnection'
      });
      
      if (response.connected) {
        document.getElementById('partner-dot').className = 'status-dot connected';
        document.getElementById('partner-status').textContent = `Connected to ${response.teamName}`;
      } else {
        document.getElementById('partner-dot').className = 'status-dot disconnected';
        document.getElementById('partner-status').textContent = 'Not connected';
      }
    } catch (error) {
      document.getElementById('partner-dot').className = 'status-dot disconnected';
      document.getElementById('partner-status').textContent = 'Connection error';
    }
  }

  async notifyPartnerTeam(eventType, data) {
    try {
      await chrome.runtime.sendMessage({
        action: 'notifyPartner',
        data: {
          eventType: eventType,
          data: data
        }
      });
    } catch (error) {
      console.error('Failed to notify partner team:', error);
    }
  }

  async checkWorkflowState() {
    // Check if there's an ongoing workflow
    const state = await chrome.storage.local.get(['workflowState']);
    if (state.workflowState) {
      this.currentStep = state.workflowState.step;
      this.captureId = state.workflowState.captureId;
      
      // Restore workflow UI
      this.showWorkflowSteps();
      this.updateStepsToCurrentState();
    }
  }

  updateStepsToCurrentState() {
    for (let i = 1; i < this.currentStep; i++) {
      this.updateStep(i, 'completed');
    }
    this.updateStep(this.currentStep, 'current');
  }

  showWorkflowSteps() {
    document.getElementById('workflow-steps').classList.remove('hidden');
  }

  hideWorkflowSteps() {
    document.getElementById('workflow-steps').classList.add('hidden');
  }

  updateStep(stepNumber, status) {
    const stepElement = document.getElementById(`step-${stepNumber}`);
    stepElement.className = `step-number ${status}`;
    
    if (status === 'completed') {
      stepElement.textContent = '✓';
    } else if (status === 'current') {
      stepElement.textContent = stepNumber;
    } else {
      stepElement.textContent = stepNumber;
    }
  }

  showStatus(message, type) {
    const statusElement = document.getElementById('status');
    statusElement.textContent = message;
    statusElement.className = `status ${type}`;
    statusElement.classList.remove('hidden');
    
    // Auto-hide success messages
    if (type === 'success') {
      setTimeout(() => {
        statusElement.classList.add('hidden');
      }, 3000);
    }
  }

  showQuickActions() {
    document.getElementById('quick-actions').classList.remove('hidden');
  }

  hideQuickActions() {
    document.getElementById('quick-actions').classList.add('hidden');
  }

  async retryCurrentStep() {
    // Retry the current step based on workflow state
    if (this.currentStep === 1) {
      await this.startCaptureWorkflow();
    } else if (this.currentStep === 3) {
      const description = document.getElementById('description-input')?.value;
      if (description) {
        await this.generateMockup(description);
      }
    }
  }

  async resetWorkflow() {
    // Clear workflow state
    await chrome.storage.local.remove(['workflowState']);
    
    // Reset UI
    this.currentStep = 1;
    this.captureId = null;
    this.hideWorkflowSteps();
    this.hideQuickActions();
    
    // Restore main actions
    location.reload();
  }

  async openQuickFeedback() {
    // Open quick feedback form
    const feedbackUrl = `${this.apiUrl}/feedback`;
    await chrome.tabs.create({ url: feedbackUrl });
  }

  async openMockupViewer() {
    // Open mockup gallery
    const galleryUrl = `${this.apiUrl}/mockups`;
    await chrome.tabs.create({ url: galleryUrl });
  }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new AlignExtensionPopup();
});
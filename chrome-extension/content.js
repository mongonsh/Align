/**
 * Align Chrome Extension - Content Script
 * Runs on all web pages to provide overlay functionality
 */

class AlignContentScript {
  constructor() {
    this.isOverlayVisible = false;
    this.overlay = null;
    this.init();
  }

  init() {
    // Listen for messages from popup/background
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true;
    });

    // Add keyboard shortcut (Ctrl+Shift+A)
    document.addEventListener('keydown', (event) => {
      if (event.ctrlKey && event.shiftKey && event.key === 'A') {
        event.preventDefault();
        this.toggleOverlay();
      }
    });
  }

  handleMessage(message, sender, sendResponse) {
    switch (message.action) {
      case 'showOverlay':
        this.showOverlay();
        sendResponse({ success: true });
        break;
        
      case 'hideOverlay':
        this.hideOverlay();
        sendResponse({ success: true });
        break;
        
      case 'captureArea':
        this.startAreaCapture();
        sendResponse({ success: true });
        break;
        
      default:
        sendResponse({ success: false, error: 'Unknown action' });
    }
  }

  toggleOverlay() {
    if (this.isOverlayVisible) {
      this.hideOverlay();
    } else {
      this.showOverlay();
    }
  }

  showOverlay() {
    if (this.overlay) {
      this.overlay.style.display = 'block';
      this.isOverlayVisible = true;
      return;
    }

    // Create overlay
    this.overlay = document.createElement('div');
    this.overlay.id = 'align-extension-overlay';
    this.overlay.innerHTML = `
      <div class="align-overlay-content">
        <div class="align-overlay-header">
          <div class="align-logo">
            <span>🎯 Align</span>
          </div>
          <button class="align-close-btn" id="align-close">×</button>
        </div>
        
        <div class="align-overlay-body">
          <h3>Quick Actions</h3>
          
          <button class="align-action-btn primary" id="align-capture-full">
            📸 Capture Full Page
          </button>
          
          <button class="align-action-btn secondary" id="align-capture-area">
            🎯 Capture Selected Area
          </button>
          
          <button class="align-action-btn secondary" id="align-quick-feedback">
            💬 Quick Feedback
          </button>
          
          <div class="align-description-area" id="align-description" style="display: none;">
            <textarea 
              placeholder="Describe the changes you want..."
              id="align-description-input"
            ></textarea>
            <div class="align-description-actions">
              <button class="align-action-btn primary" id="align-generate">
                ✨ Generate Mockup
              </button>
              <button class="align-action-btn secondary" id="align-voice">
                🎤 Voice Input
              </button>
            </div>
          </div>
        </div>
        
        <div class="align-overlay-footer">
          <small>Press Ctrl+Shift+A to toggle</small>
        </div>
      </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      #align-extension-overlay {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 320px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        border: 1px solid #e5e7eb;
      }
      
      .align-overlay-content {
        padding: 0;
      }
      
      .align-overlay-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid #e5e7eb;
        background: #f9fafb;
        border-radius: 12px 12px 0 0;
      }
      
      .align-logo {
        font-weight: 600;
        color: #2563eb;
        font-size: 16px;
      }
      
      .align-close-btn {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: #6b7280;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
      }
      
      .align-close-btn:hover {
        background: #e5e7eb;
        color: #374151;
      }
      
      .align-overlay-body {
        padding: 20px;
      }
      
      .align-overlay-body h3 {
        margin: 0 0 16px 0;
        font-size: 14px;
        font-weight: 600;
        color: #374151;
      }
      
      .align-action-btn {
        width: 100%;
        padding: 12px 16px;
        margin: 8px 0;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
      }
      
      .align-action-btn.primary {
        background: #2563eb;
        color: white;
      }
      
      .align-action-btn.primary:hover {
        background: #1d4ed8;
      }
      
      .align-action-btn.secondary {
        background: #f3f4f6;
        color: #374151;
        border: 1px solid #d1d5db;
      }
      
      .align-action-btn.secondary:hover {
        background: #e5e7eb;
      }
      
      .align-description-area {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #e5e7eb;
      }
      
      .align-description-area textarea {
        width: 100%;
        height: 80px;
        padding: 12px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        resize: none;
        font-size: 14px;
        font-family: inherit;
        margin-bottom: 12px;
      }
      
      .align-description-area textarea:focus {
        outline: none;
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
      }
      
      .align-description-actions {
        display: flex;
        gap: 8px;
      }
      
      .align-description-actions .align-action-btn {
        margin: 0;
        flex: 1;
      }
      
      .align-overlay-footer {
        padding: 12px 20px;
        border-top: 1px solid #e5e7eb;
        background: #f9fafb;
        border-radius: 0 0 12px 12px;
        text-align: center;
      }
      
      .align-overlay-footer small {
        color: #6b7280;
        font-size: 12px;
      }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(this.overlay);

    // Add event listeners
    this.setupOverlayEvents();
    
    this.isOverlayVisible = true;
  }

  setupOverlayEvents() {
    // Close button
    document.getElementById('align-close').addEventListener('click', () => {
      this.hideOverlay();
    });

    // Capture full page
    document.getElementById('align-capture-full').addEventListener('click', () => {
      this.captureFullPage();
    });

    // Capture area
    document.getElementById('align-capture-area').addEventListener('click', () => {
      this.startAreaCapture();
    });

    // Quick feedback
    document.getElementById('align-quick-feedback').addEventListener('click', () => {
      this.openQuickFeedback();
    });

    // Generate mockup
    document.getElementById('align-generate').addEventListener('click', () => {
      const description = document.getElementById('align-description-input').value.trim();
      if (description) {
        this.generateMockup(description);
      }
    });

    // Voice input
    document.getElementById('align-voice').addEventListener('click', () => {
      this.startVoiceInput();
    });
  }

  hideOverlay() {
    if (this.overlay) {
      this.overlay.style.display = 'none';
      this.isOverlayVisible = false;
    }
  }

  async captureFullPage() {
    try {
      // Send message to background script to capture
      const response = await chrome.runtime.sendMessage({
        action: 'captureScreenshot',
        data: {
          url: window.location.href,
          title: document.title,
          type: 'full_page'
        }
      });

      if (response.success) {
        // Show description area
        document.getElementById('align-description').style.display = 'block';
        document.getElementById('align-description-input').focus();
        
        // Store capture ID for later use
        this.currentCaptureId = response.captureId;
      } else {
        this.showError('Failed to capture screenshot');
      }
    } catch (error) {
      this.showError('Error: ' + error.message);
    }
  }

  startAreaCapture() {
    // Hide overlay temporarily
    this.hideOverlay();
    
    // Create selection overlay
    this.createSelectionOverlay();
  }

  createSelectionOverlay() {
    const selectionOverlay = document.createElement('div');
    selectionOverlay.id = 'align-selection-overlay';
    selectionOverlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.3);
      z-index: 10001;
      cursor: crosshair;
    `;

    const instructions = document.createElement('div');
    instructions.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: white;
      padding: 12px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      z-index: 10002;
    `;
    instructions.textContent = 'Click and drag to select an area, or press Escape to cancel';

    document.body.appendChild(selectionOverlay);
    document.body.appendChild(instructions);

    let isSelecting = false;
    let startX, startY;
    let selectionBox = null;

    const handleMouseDown = (e) => {
      isSelecting = true;
      startX = e.clientX;
      startY = e.clientY;

      selectionBox = document.createElement('div');
      selectionBox.style.cssText = `
        position: fixed;
        border: 2px solid #2563eb;
        background: rgba(37, 99, 235, 0.1);
        z-index: 10002;
        pointer-events: none;
      `;
      document.body.appendChild(selectionBox);
    };

    const handleMouseMove = (e) => {
      if (!isSelecting || !selectionBox) return;

      const currentX = e.clientX;
      const currentY = e.clientY;

      const left = Math.min(startX, currentX);
      const top = Math.min(startY, currentY);
      const width = Math.abs(currentX - startX);
      const height = Math.abs(currentY - startY);

      selectionBox.style.left = left + 'px';
      selectionBox.style.top = top + 'px';
      selectionBox.style.width = width + 'px';
      selectionBox.style.height = height + 'px';
    };

    const handleMouseUp = async (e) => {
      if (!isSelecting) return;

      const currentX = e.clientX;
      const currentY = e.clientY;

      const left = Math.min(startX, currentX);
      const top = Math.min(startY, currentY);
      const width = Math.abs(currentX - startX);
      const height = Math.abs(currentY - startY);

      // Clean up
      cleanup();

      // Capture the selected area
      if (width > 10 && height > 10) {
        await this.captureArea({ left, top, width, height });
      }
    };

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        cleanup();
        this.showOverlay();
      }
    };

    const cleanup = () => {
      document.body.removeChild(selectionOverlay);
      document.body.removeChild(instructions);
      if (selectionBox) {
        document.body.removeChild(selectionBox);
      }
      
      document.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('keydown', handleKeyDown);
    };

    document.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('keydown', handleKeyDown);
  }

  async captureArea(selection) {
    try {
      const response = await chrome.runtime.sendMessage({
        action: 'captureArea',
        data: {
          url: window.location.href,
          title: document.title,
          selection: selection
        }
      });

      if (response.success) {
        this.currentCaptureId = response.captureId;
        this.showOverlay();
        
        // Show description area
        document.getElementById('align-description').style.display = 'block';
        document.getElementById('align-description-input').focus();
      } else {
        this.showError('Failed to capture area');
      }
    } catch (error) {
      this.showError('Error: ' + error.message);
    }
  }

  async generateMockup(description) {
    try {
      const response = await chrome.runtime.sendMessage({
        action: 'generateMockup',
        data: {
          captureId: this.currentCaptureId,
          description: description
        }
      });

      if (response.success) {
        this.showSuccess('Mockup generated! Check the extension popup for options.');
        this.hideOverlay();
      } else {
        this.showError('Failed to generate mockup: ' + response.error);
      }
    } catch (error) {
      this.showError('Error: ' + error.message);
    }
  }

  startVoiceInput() {
    // Similar to popup implementation
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      this.showError('Voice input not supported');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    const voiceBtn = document.getElementById('align-voice');
    const originalText = voiceBtn.textContent;

    recognition.onstart = () => {
      voiceBtn.textContent = '🔴 Listening...';
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById('align-description-input').value = transcript;
    };

    recognition.onerror = (event) => {
      this.showError(`Voice error: ${event.error}`);
    };

    recognition.onend = () => {
      voiceBtn.textContent = originalText;
    };

    recognition.start();
  }

  openQuickFeedback() {
    // Open feedback form in new tab
    chrome.runtime.sendMessage({
      action: 'openFeedback'
    });
  }

  showError(message) {
    this.showNotification(message, 'error');
  }

  showSuccess(message) {
    this.showNotification(message, 'success');
  }

  showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      padding: 12px 20px;
      border-radius: 8px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      z-index: 10003;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      ${type === 'error' ? 
        'background: #fef2f2; color: #dc2626; border: 1px solid #fecaca;' :
        'background: #dcfce7; color: #166534; border: 1px solid #bbf7d0;'
      }
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 3000);
  }
}

// Initialize content script
new AlignContentScript();
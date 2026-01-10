/**
 * Align Chrome Extension - Background Service Worker
 * Handles API communication and cross-team integration
 */

class AlignExtensionBackground {
  constructor() {
    this.apiUrl = 'http://localhost:8000';
    this.apiKey = null;
    this.partnerTeamId = null;
    this.websocket = null;
    
    this.init();
  }

  async init() {
    // Load settings
    const settings = await chrome.storage.sync.get(['apiUrl', 'apiKey', 'partnerTeamId']);
    if (settings.apiUrl) this.apiUrl = settings.apiUrl;
    if (settings.apiKey) this.apiKey = settings.apiKey;
    if (settings.partnerTeamId) this.partnerTeamId = settings.partnerTeamId;
    
    // Setup message listeners
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async response
    });
    
    // Setup installation handler
    chrome.runtime.onInstalled.addListener(() => {
      this.handleInstallation();
    });
    
    // Connect to partner team if configured
    if (this.partnerTeamId) {
      await this.connectToPartnerTeam();
    }
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'captureScreenshot':
          const captureResult = await this.handleScreenshotCapture(message.data);
          sendResponse(captureResult);
          break;
          
        case 'generateMockup':
          const mockupResult = await this.handleMockupGeneration(message.data);
          sendResponse(mockupResult);
          break;
          
        case 'startCollaboration':
          const collabResult = await this.handleCollaborationStart(message.data);
          sendResponse(collabResult);
          break;
          
        case 'checkPartnerConnection':
          const connectionStatus = await this.checkPartnerConnection();
          sendResponse(connectionStatus);
          break;
          
        case 'notifyPartner':
          const notifyResult = await this.notifyPartnerTeam(message.data);
          sendResponse(notifyResult);
          break;
          
        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Background script error:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  async handleInstallation() {
    // Register extension with Align API
    try {
      const extensionId = chrome.runtime.id;
      
      const response = await fetch(`${this.apiUrl}/api/integration/register-extension`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          extension_id: extensionId,
          team_id: this.partnerTeamId || 'default',
          permissions: [
            'capture_screenshots',
            'generate_mockups',
            'create_collaborations',
            'sync_state'
          ]
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Save API key
        await chrome.storage.sync.set({
          apiKey: data.api_key,
          registrationStatus: 'registered'
        });
        
        this.apiKey = data.api_key;
        
        console.log('Extension registered successfully');
      }
    } catch (error) {
      console.error('Failed to register extension:', error);
    }
  }

  async handleScreenshotCapture(data) {
    try {
      // Convert data URL to blob
      const response = await fetch(data.screenshot);
      const blob = await response.blob();
      
      // Create form data
      const formData = new FormData();
      formData.append('file', blob, 'screenshot.png');
      formData.append('metadata', JSON.stringify({
        url: data.url,
        title: data.title,
        captured_at: new Date().toISOString(),
        source: 'chrome_extension'
      }));
      
      // Upload to Align API
      const uploadResponse = await fetch(`${this.apiUrl}/api/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: formData
      });
      
      if (uploadResponse.ok) {
        const uploadData = await uploadResponse.json();
        
        // Save workflow state
        await chrome.storage.local.set({
          workflowState: {
            step: 2,
            captureId: uploadData.image_id,
            imageData: uploadData
          }
        });
        
        return {
          success: true,
          captureId: uploadData.image_id,
          imageData: uploadData
        };
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async handleMockupGeneration(data) {
    try {
      // First, parse the prompt
      const promptResponse = await fetch(`${this.apiUrl}/api/prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          image_id: data.captureId,
          description: data.description
        })
      });
      
      if (!promptResponse.ok) {
        throw new Error('Prompt parsing failed');
      }
      
      const promptData = await promptResponse.json();
      
      // Generate mockup
      const generateResponse = await fetch(`${this.apiUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          image_id: data.captureId,
          description: data.description,
          requirements: promptData.requirements
        })
      });
      
      if (generateResponse.ok) {
        const mockupData = await generateResponse.json();
        
        // Update workflow state
        await chrome.storage.local.set({
          workflowState: {
            step: 4,
            captureId: data.captureId,
            mockupData: mockupData
          }
        });
        
        return {
          success: true,
          mockup: mockupData
        };
      } else {
        throw new Error('Mockup generation failed');
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async handleCollaborationStart(data) {
    try {
      const response = await fetch(`${this.apiUrl}/api/collaboration/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          mockup_id: data.mockupId,
          partner_team_id: data.partnerTeamId,
          created_by: 'chrome_extension_user'
        })
      });
      
      if (response.ok) {
        const sessionData = await response.json();
        return {
          success: true,
          sessionId: sessionData.session_id
        };
      } else {
        throw new Error('Failed to create collaboration session');
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async checkPartnerConnection() {
    try {
      if (!this.partnerTeamId) {
        return { connected: false, reason: 'No partner team configured' };
      }
      
      const response = await fetch(`${this.apiUrl}/api/integration/partner-status/${this.partnerTeamId}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        return {
          connected: data.is_active,
          teamName: data.team_name,
          lastSync: data.last_sync
        };
      } else {
        return { connected: false, reason: 'API error' };
      }
    } catch (error) {
      return { connected: false, reason: error.message };
    }
  }

  async notifyPartnerTeam(data) {
    try {
      if (!this.partnerTeamId) {
        return { success: false, error: 'No partner team configured' };
      }
      
      const response = await fetch(`${this.apiUrl}/api/integration/notify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          team_id: this.partnerTeamId,
          event_type: data.eventType,
          data: data.data,
          source: 'chrome_extension'
        })
      });
      
      return {
        success: response.ok,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async connectToPartnerTeam() {
    try {
      // Establish WebSocket connection for real-time sync
      const wsUrl = `ws://localhost:8000/ws/integration/${this.partnerTeamId}`;
      this.websocket = new WebSocket(wsUrl);
      
      this.websocket.onopen = () => {
        console.log('Connected to partner team WebSocket');
      };
      
      this.websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.handlePartnerMessage(message);
      };
      
      this.websocket.onclose = () => {
        console.log('Partner team WebSocket disconnected');
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
          this.connectToPartnerTeam();
        }, 5000);
      };
      
      this.websocket.onerror = (error) => {
        console.error('Partner team WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect to partner team:', error);
    }
  }

  async handlePartnerMessage(message) {
    // Handle real-time messages from partner team
    switch (message.type) {
      case 'collaboration_invite':
        await this.handleCollaborationInvite(message.data);
        break;
        
      case 'state_sync':
        await this.handleStateSync(message.data);
        break;
        
      case 'feature_request':
        await this.handlePartnerFeatureRequest(message.data);
        break;
        
      default:
        console.log('Unknown partner message type:', message.type);
    }
  }

  async handleCollaborationInvite(data) {
    // Show notification for collaboration invite
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Align - Collaboration Invite',
      message: `${data.inviter} invited you to collaborate on a mockup`
    });
  }

  async handleStateSync(data) {
    // Sync state with partner team
    await chrome.storage.local.set({
      partnerState: data.state
    });
  }

  async handlePartnerFeatureRequest(data) {
    // Show notification for feature request
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Align - Feature Request',
      message: `New feature request: ${data.title}`
    });
  }
}

// Initialize background script
new AlignExtensionBackground();
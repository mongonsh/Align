# Align - AI-Powered Mockup Generator

> Align customer and engineer expectations before coding starts

## The Problem

Customer: "Add a dashboard"
Engineer builds something
Customer: "No! That's not what I meant!"

**Result:** Wasted time, wasted money, frustrated teams.

## The Solution

**Align** creates visual mockups from customer descriptions, giving both customer and engineer the exact same picture before any code is written.

1. Customer uploads screenshot of current system
2. Customer describes desired changes in plain English
3. AI generates visual mockup (HTML/CSS)
4. Both sides see and approve the same design
5. Engineer builds exactly what was approved

## Architecture

Built with **concept-based design** principles from Daniel Jackson's "The Essence of Software":

### Backend Concepts (Python/FastAPI)

- **UploadConcept**: Handles image upload and storage
- **PromptConcept**: Parses natural language requirements
- **MockupConcept**: Generates HTML mockups using Gemini AI
- **ExportConcept**: Packages mockups for sharing

### Frontend Concepts (React/Next.js)

- **UploadView**: Drag-and-drop image upload UI
- **PromptView**: Natural language change description
- **MockupView**: Side-by-side comparison display
- **ExportView**: Download and sharing options

Each concept is **independent** and **reusable** - the hallmark of clean, maintainable code.

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (async web framework)
- Google Gemini AI (mockup generation)
- Pillow (image processing)
- Pydantic (validation)

**Frontend:**
- React 18
- Next.js 16
- TypeScript
- TailwindCSS
- Reducer pattern (state management)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Align
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. Start with Docker (recommended):
```bash
docker-compose up --build
```

Or run locally:

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Usage

1. **Upload Screenshot**
   - Drag and drop or select an image of your current system
   - Supports PNG, JPG, GIF

2. **Describe Changes**
   - Type what you want to change in plain English
   - Example: "Make the header dark blue and add a search bar in the top right corner"

3. **Generate Mockup**
   - AI generates a complete HTML mockup
   - See side-by-side comparison of before and after

4. **Export & Share**
   - Download as HTML or ZIP
   - Share with your team for approval
   - Get everyone aligned before coding

## API Documentation

Once running, visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

### Key Endpoints

- `POST /api/upload` - Upload screenshot
- `POST /api/prompt` - Parse change description
- `POST /api/generate` - Generate mockup
- `GET /api/mockup/{id}` - Retrieve mockup
- `GET /api/export/{id}` - Download mockup

## Project Structure

```
align/
├── backend/
│   ├── concepts/          # Core business logic (concept-based)
│   │   ├── upload.py
│   │   ├── prompt.py
│   │   ├── mockup.py
│   │   └── export.py
│   ├── services/          # External integrations
│   │   └── gemini_client.py
│   ├── api/               # API routes
│   │   └── routes.py
│   ├── main.py            # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── concepts/      # Concept-based components
│   │   │   ├── UploadView.tsx
│   │   │   ├── PromptView.tsx
│   │   │   ├── MockupView.tsx
│   │   │   └── ExportView.tsx
│   │   └── page.tsx       # Main application
│   └── lib/
│       ├── api.ts         # API client
│       └── stores/        # State management
├── docker-compose.yml
└── README.md
```

## Concept-Based Design

This project follows concept-based design principles:

1. **Free-standing concepts** - Each concept works independently
2. **Loose coupling** - Concepts synchronize via events, not direct dependencies
3. **Clear purpose** - Each concept has a single, well-defined purpose
4. **Composable** - Concepts can be combined without modification


## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs on [http://localhost:8000](http://localhost:8000)

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on [http://localhost:3000](http://localhost:3000)

### Environment Variables

**Backend (.env):**
- `GEMINI_API_KEY` - Your Google Gemini API key

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

## Features

- ✅ Drag-and-drop image upload
- ✅ Natural language change descriptions
- ✅ AI-powered mockup generation
- ✅ Side-by-side comparison view
- ✅ HTML/ZIP export
- ✅ Clean concept-based architecture
- ✅ Full TypeScript support
- ✅ Responsive design
- ✅ Error handling
- ✅ Docker support

## Future Enhancements

- [ ] Multi-page mockups
- [ ] Version history
- [ ] Team collaboration
- [ ] Figma/Sketch export
- [ ] Design system templates
- [ ] WebSocket real-time generation
- [ ] Mobile app


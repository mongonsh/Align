'use client';

import { useState, useRef } from 'react';
import { api } from '@/lib/api';

interface VoiceOutputProps {
  text: string;
  voiceId?: string;
  autoPlay?: boolean;
  onError?: (error: string) => void;
}

export default function VoiceOutput({ 
  text, 
  voiceId = "Fahco4VZzobUeiPqni1S", // Default to your custom voice
  autoPlay = false, 
  onError 
}: VoiceOutputProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const generateAndPlay = async () => {
    if (!text.trim()) {
      onError?.('No text to convert to speech');
      return;
    }

    setIsGenerating(true);
    
    try {
      const audioBlob = await api.textToSpeech(text, voiceId);
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      // Create and play audio
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onplay = () => setIsPlaying(true);
      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(url);
        setAudioUrl(null);
      };
      audio.onerror = () => {
        setIsPlaying(false);
        onError?.('Failed to play audio');
      };

      if (autoPlay) {
        await audio.play();
      }
    } catch (error) {
      onError?.(error instanceof Error ? error.message : 'Text-to-speech failed');
    } finally {
      setIsGenerating(false);
    }
  };

  const playAudio = async () => {
    if (audioRef.current) {
      try {
        await audioRef.current.play();
      } catch (error) {
        onError?.('Failed to play audio');
      }
    } else {
      await generateAndPlay();
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={isPlaying ? stopAudio : playAudio}
        disabled={isGenerating || !text.trim()}
        className={`
          w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200
          ${isPlaying 
            ? 'bg-red-500 hover:bg-red-600' 
            : 'bg-green-500 hover:bg-green-600'
          }
          ${isGenerating || !text.trim()
            ? 'opacity-50 cursor-not-allowed' 
            : 'cursor-pointer shadow-md hover:shadow-lg'
          }
        `}
        title={isPlaying ? 'Stop audio' : 'Play audio'}
      >
        {isGenerating ? (
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
        ) : isPlaying ? (
          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        ) : (
          <svg className="w-4 h-4 text-white ml-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
          </svg>
        )}
      </button>
      
      <div className="flex-1">
        <p className="text-sm text-gray-600 line-clamp-2">
          {text.length > 100 ? `${text.substring(0, 100)}...` : text}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          {isGenerating 
            ? 'Generating audio with your custom voice...' 
            : isPlaying 
              ? 'Playing...' 
              : 'Click to hear this text with your voice'
          }
        </p>
      </div>
    </div>
  );
}
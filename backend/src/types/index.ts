// TypeScript type definitions for video processing, country config, and caption generation

// Video Processing Types
export interface Video {
  id: string;
  title: string;
  url: string;
  duration: number; // in seconds
  format: string;
}

export interface VideoProcessingOptions {
  resolution: string;
  bitrate: number;
  codec: string;
}

// Country Configuration Types
export interface CountryConfig {
  countryCode: string;
  countryName: string;
  language: string;
}

// Caption Generation Types
export interface Caption {
  id: string;
  videoId: string;
  text: string;
  startTime: number; // in seconds
  endTime: number; // in seconds
}

export interface CaptionGenerationOptions {
  format: 'vtt' | 'srt';
  language: string;
}
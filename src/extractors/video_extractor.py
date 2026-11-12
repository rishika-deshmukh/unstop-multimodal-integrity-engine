"""
MP4 Video extractor using Hugging Face Transformers Whisper.
Extracts audio tracks via FFmpeg, generates timestamped speech transcripts,
and robustly handles silent video, missing audio streams, or corrupt media files
without depending on C-extension libraries blocked by OS security policies.
"""

import os
import wave
import subprocess
import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration

from src.extractors.base_extractor import BaseExtractor, ExtractedDocument, AudioSegment
from src.utils.ffmpeg_setup import ensure_ffmpeg_available
from src.utils.text_metrics import format_timestamp
from src.normalizer.normalizer import split_into_sentences

logger = logging.getLogger("video_extractor")

class VideoExtractor(BaseExtractor):
    def __init__(self, model_name: str = "openai/whisper-tiny", device: str = "cpu"):
        # Normalize model name for Hugging Face
        if not model_name.startswith("openai/"):
            model_name = f"openai/whisper-{model_name.replace('whisper-', '')}"
        self.model_name = model_name
        self.device = device
        self._processor = None
        self._model = None
        ensure_ffmpeg_available()

    @staticmethod
    def _parse_whisper_timestamps(decoded_str: str, offset_seconds: float = 0.0) -> List[Tuple[float, float, str]]:
        """Parses Whisper timestamp tokens (<|0.00|> ... <|7.00|>) and applies window offset."""
        parts = re.split(r'<\|(\d+\.\d+)\|>', decoded_str)
        segments: List[Tuple[float, float, str]] = []
        i = 1
        while i < len(parts):
            try:
                start_t = float(parts[i]) + offset_seconds
                txt = parts[i+1].strip() if i+1 < len(parts) else ""
                end_t = float(parts[i+2]) + offset_seconds if (i+2 < len(parts) and re.match(r'^\d+\.\d+$', parts[i+2])) else start_t + 2.0
                if txt and not txt.startswith("<|"):
                    clean_txt = re.sub(r'<\|.*?\|>', '', txt).strip()
                    if clean_txt:
                        segments.append((start_t, end_t, clean_txt))
                next_i = i + 2
                while next_i < len(parts) and not re.match(r'^\d+\.\d+$', parts[next_i]):
                    next_i += 1
                i = next_i
            except Exception:
                i += 1
        return segments

    def _load_model(self):
        if self._model is None:
            logger.info(f"Loading Transformers Whisper model '{self.model_name}' on {self.device}...")
            self._processor = WhisperProcessor.from_pretrained(self.model_name)
            self._model = WhisperForConditionalGeneration.from_pretrained(self.model_name)
            self._model.to(self.device)
            self._model.eval()

    def _has_audio_stream(self, file_path: Path) -> bool:
        """Uses ffmpeg to verify if the file contains an active, audible audio stream."""
        ffmpeg_bin = ensure_ffmpeg_available()
        if not ffmpeg_bin:
            return True
        try:
            cmd = [
                ffmpeg_bin,
                "-i", str(file_path),
                "-vn", "-af", "volumedetect",
                "-f", "null", "-"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
            stderr_out = res.stderr.lower()
            if "matches no streams" in stderr_out or "does not contain any stream" in stderr_out:
                return False
            if "mean_volume: -91.0 db" in stderr_out or "mean_volume: -inf db" in stderr_out:
                return False
            return True
        except Exception as e:
            logger.debug(f"Audio stream probe encountered exception: {e}")
            return True

    def extract(self, file_path: Path) -> ExtractedDocument:
        file_path = Path(file_path)
        file_name = file_path.name
        doc_id = file_name

        if not file_path.exists():
            logger.warning(f"[MP4] Video file not found: {file_path}")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="mp4",
                status="SKIPPED_CORRUPT",
                warning_message=f"File not found: {file_name}"
            )

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.warning(f"[MP4] Zero-byte MP4 video: {file_name}. Gracefully skipping.")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="mp4",
                status="SKIPPED_EMPTY",
                warning_message=f"Zero-byte empty MP4 file: {file_name}"
            )

        # 1. Probe audio stream
        if not self._has_audio_stream(file_path):
            logger.warning(f"[MP4] Silent or missing audio stream in video: {file_name}")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="mp4",
                status="SKIPPED_SILENT",
                warning_message=f"Video contains no audible audio track or is completely silent: {file_name}"
            )

        # 2. Extract 16kHz mono WAV using FFmpeg
        ffmpeg_bin = ensure_ffmpeg_available()
        temp_wav = file_path.parent / f"_temp_audio_{file_path.stem}.wav"

        try:
            extract_cmd = [
                ffmpeg_bin,
                "-y",
                "-i", str(file_path),
                "-ar", "16000",
                "-ac", "1",
                "-f", "wav",
                str(temp_wav)
            ]
            subprocess.run(extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=30)

            if not temp_wav.exists() or os.path.getsize(temp_wav) < 100:
                logger.warning(f"[MP4] Audio extraction resulted in empty stream for: {file_name}")
                return ExtractedDocument(
                    file_path=file_path,
                    file_name=file_name,
                    doc_id=doc_id,
                    modality="mp4",
                    status="SKIPPED_SILENT",
                    warning_message=f"No audio stream extracted: {file_name}"
                )

            # Read WAV samples
            with wave.open(str(temp_wav), "rb") as wf:
                n_frames = wf.getnframes()
                frames = wf.readframes(n_frames)
                duration = float(n_frames) / 16000.0

            audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

            # Check for silent audio (low amplitude)
            if np.max(np.abs(audio_data)) < 0.005:
                logger.warning(f"[MP4] Audio waveform amplitude is silent (<0.005) for: {file_name}")
                return ExtractedDocument(
                    file_path=file_path,
                    file_name=file_name,
                    doc_id=doc_id,
                    modality="mp4",
                    status="SKIPPED_SILENT",
                    warning_message=f"Silent audio track detected in video: {file_name}"
                )

            # Run Transformers Whisper ASR over full audio using 30s sliding windows
            self._load_model()
            sample_rate = 16000
            window_size_samples = 30 * sample_rate
            total_samples = len(audio_data)

            valid_segments: List[AudioSegment] = []

            # Slide in 30-second windows across full audio duration (supporting clips > 30s)
            for start_sample in range(0, total_samples, window_size_samples):
                end_sample = min(total_samples, start_sample + window_size_samples)
                window_audio = audio_data[start_sample:end_sample]
                window_offset_s = float(start_sample) / float(sample_rate)

                # Skip windows shorter than 0.5s or silent
                if len(window_audio) < int(0.5 * sample_rate) or np.max(np.abs(window_audio)) < 0.005:
                    continue

                inputs = self._processor(window_audio, sampling_rate=sample_rate, return_tensors="pt").to(self.device)

                with torch.no_grad():
                    pred_ids = self._model.generate(
                        inputs.input_features,
                        language="en",
                        task="transcribe",
                        return_timestamps=True
                    )

                decoded_str = self._processor.tokenizer.decode(pred_ids[0], decode_with_timestamps=True)
                window_segments = self._parse_whisper_timestamps(decoded_str, offset_seconds=window_offset_s)

                if window_segments:
                    for s_start, s_end, s_text in window_segments:
                        ts_str = f"{format_timestamp(s_start)} - {format_timestamp(s_end)}"
                        valid_segments.append(
                            AudioSegment(
                                start_seconds=round(s_start, 2),
                                end_seconds=round(s_end, 2),
                                timestamp_str=ts_str,
                                text=s_text,
                                no_speech_prob=0.0
                            )
                        )
                else:
                    # Fallback to plain batch decode if timestamp tokens were absent
                    plain_text = self._processor.batch_decode(pred_ids, skip_special_tokens=True)[0].strip()
                    if plain_text:
                        w_end_s = min(duration, float(end_sample) / float(sample_rate))
                        ts_str = f"{format_timestamp(window_offset_s)} - {format_timestamp(w_end_s)}"
                        valid_segments.append(
                            AudioSegment(
                                start_seconds=round(window_offset_s, 2),
                                end_seconds=round(w_end_s, 2),
                                timestamp_str=ts_str,
                                text=plain_text,
                                no_speech_prob=0.0
                            )
                        )

            full_transcript = " ".join(seg.text for seg in valid_segments).strip()

            if not full_transcript:
                logger.warning(f"[MP4] Whisper transcription yielded empty text for: {file_name}")
                return ExtractedDocument(
                    file_path=file_path,
                    file_name=file_name,
                    doc_id=doc_id,
                    modality="mp4",
                    status="SKIPPED_SILENT",
                    warning_message=f"No intelligible speech transcribed from: {file_name}"
                )

            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="mp4",
                raw_text=full_transcript,
                audio_segments=valid_segments,
                status="SUCCESS"
            )

        except Exception as e:
            logger.warning(f"[MP4] Video processing failed for {file_name}: {e}")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="mp4",
                status="SKIPPED_CORRUPT",
                warning_message=f"Audio extraction or ASR failure: {e}"
            )
        finally:
            if temp_wav.exists():
                try:
                    temp_wav.unlink()
                except Exception:
                    pass

import subprocess
import os
from typing import List

class AssemblerService:
    def merge_segments_and_video(self, video_path: str, segments: List[dict], bgm_path: str, output_path: str):
        """
        Merges multiple translated audio segments into the final video at their correct timestamps.
        Uses FFmpeg filter_complex for high-performance stitching.
        """
        # Create a silent audio base or just mix directly
        # For simplicity in this scaffold, we'll build a filter that delays each segment

        filter_parts = []
        inputs = ["-i", video_path]

        # Add segments as inputs
        for i, seg in enumerate(segments):
            inputs.extend(["-i", seg["local_audio_path"]])
            start_ms = int(seg["start"] * 1000)
            # Delay segment to its start time
            filter_parts.append(f"[{i+1}:a]adelay={start_ms}|{start_ms}[a{i}]")

        inputs.extend(["-i", bgm_path])
        bgm_index = len(segments) + 1

        # Mix delayed segments
        mix_inputs = "".join([f"[a{i}]" for i in range(len(segments))])
        # Note: amix needs careful volume handling or it gets quiet.
        # Using normalized mix if multiple segments overlap.
        filter_parts.append(f"{mix_inputs}amix=inputs={len(segments)}:dropout_transition=0[vocals]")

        # Mix vocals with BGM
        filter_parts.append(f"[vocals][{bgm_index}:a]amix=inputs=2:duration=first[final_a]")

        filter_complex = ";".join(filter_parts)

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[final_a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg multi-segment merge failed: {e.stderr.decode()}")

        return output_path

    def merge_audio_video(self, video_path: str, vocal_path: str, bgm_path: str, output_path: str):
        """
        High-performance merging using FFmpeg.
        Combines translated vocals + original BGM and replaces the video's audio.
        """
        # 1. Mix vocals and BGM with ducking (if needed) or simple mix
        # 2. Map to video stream

        # Simple mix command example:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", vocal_path,
            "-i", bgm_path,
            "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",        # Stream copy video to avoid re-encoding
            "-c:a", "aac",
            "-shortest",
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg merge failed: {e.stderr.decode()}")

        return output_path

assembler_service = AssemblerService()

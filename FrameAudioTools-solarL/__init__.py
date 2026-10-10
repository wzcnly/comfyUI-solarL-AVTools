# SPDX-License-Identifier: MIT
# Copyright (c) 2026 solarL
"""Frame-based video/audio trimming and alignment by solarL."""

import math


def fit_audio(audio, start_frame, frame_count, fps, short_audio):
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError("FPS 必须是大于 0 的有限数值")
    if start_frame < 0 or frame_count < 1:
        raise ValueError("起始帧不能为负，截取帧数必须大于 0")
    if short_audio not in ("pad_silence", "loop", "error"):
        raise ValueError("未知的音频不足处理模式")
    if not isinstance(audio, dict):
        raise ValueError("请连接有效的 AUDIO")
    waveform = audio.get("waveform")
    sample_rate = audio.get("sample_rate")
    if waveform is None or waveform.ndim != 3:
        raise ValueError("音频必须为 [batch, channels, samples]")
    if not isinstance(sample_rate, int) or sample_rate <= 0:
        raise ValueError("音频采样率必须为正整数")

    # Independent endpoint rounding keeps adjacent frame ranges contiguous.
    start = round(start_frame * sample_rate / fps)
    end = round((start_frame + frame_count) * sample_rate / fps)
    target = end - start
    if target < 1:
        raise ValueError("截取区间不足一个音频采样点")
    clip = waveform[..., start:end]
    available = clip.shape[-1]
    if available == target:
        result = clip.clone()
    elif short_audio == "error":
        raise ValueError("指定帧区间内的音频长度不足")
    elif short_audio == "loop":
        if available == 0:
            raise ValueError("指定起点后没有可循环的音频")
        repeats = (target + available - 1) // available
        result = clip.repeat(1, 1, repeats)[..., :target].contiguous()
    else:
        result = waveform.new_zeros((*waveform.shape[:-1], target))
        if available:
            result[..., :available] = clip
    return {**audio, "waveform": result}


def shared_inputs():
    return {
        "audio": ("AUDIO",),
        "fps": ("FLOAT", {
            "default": 24.0, "min": 0.001, "max": 1000.0, "step": 0.001,
            "tooltip": "与当前视频帧序列和最终合成使用相同的 FPS",
        }),
        "start_frame": ("INT", {
            "default": 0, "min": 0, "max": 2147483647,
            "tooltip": "起始帧，从 0 开始编号",
        }),
        "short_audio": (["pad_silence", "loop", "error"], {
            "tooltip": "音频不足时：pad_silence 补静音；loop 循环可用音频；error 报错",
        }),
    }


class SolarLAVFrameTrim:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "images": ("IMAGE",),
            **shared_inputs(),
            "frame_count": ("INT", {
                "default": 0, "min": 0, "max": 2147483647,
                "tooltip": "截取帧数；0 表示从起始帧取到结尾",
            }),
        }}

    RETURN_TYPES = ("IMAGE", "AUDIO", "INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("images", "audio", "frame_count", "fps", "duration")
    FUNCTION = "trim"
    CATEGORY = "solarL/AV Tools/FrameAudioTools-solarL"
    DESCRIPTION = "使用相同帧区间裁剪视频和音频，读取实际 IMAGE 批次长度。"

    def trim(self, images, audio, fps, start_frame, short_audio, frame_count):
        if images.ndim != 4 or images.shape[0] < 1:
            raise ValueError("请连接非空的 IMAGE 视频帧批次")
        total = int(images.shape[0])
        if start_frame < 0 or start_frame >= total:
            raise ValueError(f"起始帧 {start_frame} 超出视频范围 0～{total - 1}")
        if frame_count < 0:
            raise ValueError("截取帧数不能为负")
        remaining = total - start_frame
        actual_count = remaining if frame_count == 0 else min(frame_count, remaining)
        output_audio = fit_audio(audio, start_frame, actual_count, fps, short_audio)
        output_images = images[start_frame:start_frame + actual_count]
        return output_images, output_audio, actual_count, fps, actual_count / fps


class SolarLAudioAlignByFrames:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            **shared_inputs(),
            "frame_count": ("INT", {
                "default": 121, "min": 1, "max": 2147483647,
                "tooltip": "目标音频对应的视频帧数",
            }),
        }}

    RETURN_TYPES = ("AUDIO", "INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("audio", "frame_count", "fps", "duration")
    FUNCTION = "align"
    CATEGORY = "solarL/AV Tools/FrameAudioTools-solarL"
    DESCRIPTION = "仅处理音频，按起始帧和目标帧数裁剪、补静音或循环。"

    def align(self, audio, fps, start_frame, short_audio, frame_count):
        output_audio = fit_audio(audio, start_frame, frame_count, fps, short_audio)
        return output_audio, frame_count, fps, frame_count / fps


NODE_CLASS_MAPPINGS = {
    "AVFrameTrim-solarL": SolarLAVFrameTrim,
    "AudioAlignByFrames-solarL": SolarLAudioAlignByFrames,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "AVFrameTrim-solarL": "视频音频按帧裁剪-solarL",
    "AudioAlignByFrames-solarL": "音频按帧数对齐-solarL",
}

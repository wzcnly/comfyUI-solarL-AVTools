# comfyUI-solarL-AV Tools

solarL 个人 ComfyUI 音视频工具集。

## 安装

将整个 `comfyUI-solarL-AV Tools` 文件夹放进 `ComfyUI/custom_nodes/`，然后重启 ComfyUI。无需新增第三方依赖。

## 视频音频按帧裁剪-solarL

按同一个帧区间裁剪视频和音频，可接在加载、循环或拼接节点之后。

| 参数 | 说明 |
| --- | --- |
| images | 当前视频帧批次 |
| audio | 与视频具有共同时间起点的音频 |
| fps | 视频帧率，需与最终合成一致 |
| start_frame | 起始帧，从 0 开始编号 |
| frame_count | 截取帧数，0 表示取到结尾 |
| short_audio | `pad_silence` 补静音、`loop` 循环可用音频或 `error` 报错 |

输出视频帧、音频、实际帧数、FPS 和时长。截取帧数超过视频剩余长度时，按实际剩余帧数输出。

## 音频按帧数对齐-solarL

仅处理音频，支持输入或连接整数帧数。`start_frame` 控制音频起点，`frame_count` 控制目标长度。

## 示例

起始帧 48、截取帧数 120、FPS 24：输出视频第 48～167 帧，音频从第 2 秒开始截取 5 秒。

## 接线

将裁剪节点的 `images`、`audio` 和 `fps` 分别连接到 Video Combine 的 `images`、`audio` 和 `frame_rate`。可右键将 `frame_rate` 控件转换为输入。

## 使用说明

- 视频和音频已经同步裁过时，起始帧通常保持 0。
- 帧率需与当前帧序列一致；节点不重采样视频，不改变音频播放速度。
- 音频按采样点取整；实际音频时长与帧区间时长最多相差一个采样点。
- 循环音频采用硬循环，接缝不做交叉淡化。
- 循环或拼接的视频如果需要保留原声音顺序，音频也应做相同处理后再连接。
- Video Combine 内部的循环或往返播放不会反映在上游帧数中。
- IMAGE 输入需包含完整目标帧序列；VHS Meta Batch 每次传入的局部批次只会按该批次处理。

## License

本项目采用 [MIT License](LICENSE)。Copyright (c) 2026 solarL。

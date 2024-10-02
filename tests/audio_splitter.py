import os
import gradio as gr
import numpy as np
from pydub import AudioSegment
import logging
from multiprocessing import Pool, cpu_count
import subprocess
import json
import sys

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# FFmpeg 和 FFprobe 的路径
FFMPEG_PATH = os.path.join(current_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')
FFPROBE_PATH = os.path.join(current_dir, 'ffmpeg', 'bin', 'ffprobe.exe')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def validate_input(input_path, output_folder, min_seconds, max_seconds):
    if not input_path or not os.path.exists(input_path):
        raise ValueError(f"输入路径不存在或未指定: {input_path}")
    if output_folder and not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)
        logging.info(f"创建输出文件夹: {output_folder}")
    if min_seconds is None or max_seconds is None:
        raise ValueError("最小和最大秒数必须指定")
    if min_seconds <= 0 or max_seconds <= 0:
        raise ValueError("最小和最大秒数必须大于0")
    if min_seconds >= max_seconds:
        raise ValueError("最小秒数必须小于最大秒数")


# def get_audio_info(file_path):
#     cmd = [FFPROBE_PATH, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path]
#     result = subprocess.run(cmd, capture_output=True, text=True)
#     info = json.loads(result.stdout)
#     audio_stream = next(s for s in info['streams'] if s['codec_type'] == 'audio')
#     return {
#         'duration': float(info['format']['duration']),
#         'sample_rate': int(audio_stream['sample_rate']),
#         'channels': int(audio_stream['channels']),
#         'codec': audio_stream['codec_name']
#     }


def find_split_points(file_path, min_seconds, max_seconds, min_silence_len, silence_thresh):
    audio = AudioSegment.from_file(file_path)
    audio_array = np.array(audio.get_array_of_samples())

    chunk_length = int(max_seconds * audio.frame_rate)
    min_silence_samples = int(min_silence_len / 1000 * audio.frame_rate)
    silence_thresh = silence_thresh * (1 << (audio.sample_width * 8 - 1))

    split_points = [0]
    start = 0
    while start < len(audio_array):
        end = min(start + chunk_length, len(audio_array))
        chunk = audio_array[start:end]

        volume = np.abs(chunk)
        silent_ranges = np.where(volume < silence_thresh)[0]
        silent_ranges = np.split(silent_ranges, np.where(np.diff(silent_ranges) != 1)[0] + 1)
        silent_ranges = [r for r in silent_ranges if len(r) >= min_silence_samples]

        if silent_ranges:
            split_point = start + silent_ranges[-1][-1]
            if split_point - split_points[-1] >= min_seconds * audio.frame_rate:
                split_points.append(split_point)
                start = split_point
            else:
                start = end
        else:
            start = end

    if split_points[-1] != len(audio_array):
        split_points.append(len(audio_array))

    return [p / audio.frame_rate for p in split_points]


def process_audio_file(args):
    file_path, output_folder, min_seconds, max_seconds, min_silence_len, silence_thresh = args
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        logging.info(f"开始处理文件: {file_path}")

        # audio_info = get_audio_info(file_path)
        split_points = find_split_points(file_path, min_seconds, max_seconds, min_silence_len, silence_thresh)

        file_name = os.path.splitext(os.path.basename(file_path))[0]
        original_format = os.path.splitext(file_path)[1][1:]

        output_files = []
        for i, (start, end) in enumerate(zip(split_points[:-1], split_points[1:])):
            output_file = os.path.join(output_folder, f"{file_name}_{i + 1}.{original_format}")
            duration = end - start
            cmd = [
                FFMPEG_PATH, '-i', file_path, '-ss', str(start), '-t', str(duration),
                '-c', 'copy', '-y', output_file
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            output_files.append(output_file)

        logging.info(f"成功处理文件 {file_path}，生成了 {len(output_files)} 个片段")
        return f"处理完成: {os.path.basename(file_path)} - 生成了 {len(output_files)} 个片段"
    except Exception as e:
        logging.error(f"处理文件 {file_path} 时出错: {str(e)}")
        return f"处理文件 {file_path} 时出错: {str(e)}"


def split_audio(input_path, output_folder, min_seconds, max_seconds, min_silence_len, silence_thresh):
    try:
        validate_input(input_path, output_folder, min_seconds, max_seconds)

        if not output_folder:
            output_folder = os.path.dirname(input_path) if os.path.isfile(input_path) else input_path

        output_folder = os.path.join(output_folder, "split_audio_output")
        os.makedirs(output_folder, exist_ok=True)
        logging.info(f"创建输出文件夹: {output_folder}")

        if os.path.isfile(input_path):
            files_to_process = [input_path]
        else:
            files_to_process = [os.path.join(input_path, f) for f in os.listdir(input_path)
                                if f.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a'))]

        if not files_to_process:
            return "没有找到可处理的音频文件"

        with Pool(processes=cpu_count()) as pool:
            results = pool.map(process_audio_file,
                               [(f, output_folder, min_seconds, max_seconds, min_silence_len, silence_thresh) for f in
                                files_to_process])

        total_chunks = sum(int(r.split(' - 生成了 ')[1].split(' ')[0]) for r in results if ' - 生成了 ' in r)

        final_message = f"\n所有音频处理完成。共处理 {len(files_to_process)} 个文件，生成 {total_chunks} 个音频片段。\n输出文件夹: {output_folder}"
        results.append(final_message)
        logging.info(final_message)

        return "\n".join(results)
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        logging.error(error_msg)
        return error_msg


iface = gr.Interface(
    fn=split_audio,
    inputs=[
        gr.Textbox(label="输入路径 (文件夹或单个文件)"),
        gr.Textbox(label="输出文件夹路径 (可选,留空则使用输入路径所在文件夹)"),
        gr.Number(label="最小秒数", value=6),
        gr.Number(label="最大秒数", value=8),
        gr.Number(label="最小静音长度 (毫秒)", value=500),
        gr.Number(label="静音阈值 (dB)", value=-40),
    ],
    outputs=gr.Textbox(label="处理结果"),
    title="音频文件切分工具",
    description="将音频文件切分成固定秒数的片段,保留原有音质"
)

if __name__ == "__main__":
    iface.launch()
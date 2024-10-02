from moviepy.editor import *
from pydub import AudioSegment
import os
import gradio as gr


def extract_audio_and_remove_silence(video_path, output_folder=None):
    if not output_folder:
        output_folder = os.path.dirname(video_path)
    else:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    temp_audio_path = "../data/temp_audio.wav"
    if video_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        # 提取视频文件中的音频
        try:
            video = VideoFileClip(video_path)
        except Exception as e:
            return f"文件读取失败：{str(e)}"
        audio = video.audio
        audio.write_audiofile(temp_audio_path)
        audio.close()
        video.close()
    elif video_path.lower().endswith(('.wav', '.mp3')):
        temp_audio_path = video_path
    else:
        raise ValueError("输入文件必须是视频文件（.mp4, .avi, .mov, .mkv）或音频文件（.wav, .mp3）")
    try:
        # 使用pydub去除音频中的静音部分
        sound = AudioSegment.from_file(temp_audio_path)

        # 去除静音的参数，可以根据实际情况调整
        silence_threshold = -50  # 静音阈值，默认为-50dBFS
        min_silence_len = 2000  # 连续静音最短时长（毫秒）

        # 导入并使用pydub的silence模块
        from pydub.silence import split_on_silence

        # 分割音频，去除静音段
        nonsilent_parts = split_on_silence(sound,
                                           min_silence_len=min_silence_len,
                                           silence_thresh=silence_threshold)

        # 合并非静音部分
        combined_audio = AudioSegment.empty()
        for part in nonsilent_parts:
            combined_audio += part + AudioSegment.silent(duration=1000)  # 加上一秒空白

        # 获取视频文件名（不带扩展名）以命名输出音频文件
        video_filename = os.path.splitext(os.path.basename(video_path))[0]
        output_audio_file = os.path.join(output_folder, f"{video_filename}_cleaned_audio.wav")

        # 导出处理后的音频
        combined_audio.export(output_audio_file, format="wav")

        # 清理临时文件
        if os.path.exists("../data/temp_audio.wav"):
            os.remove("../data/temp_audio.wav")
    except Exception as e:
        return f"处理遇到错误：{str(e)}"

    return f"处理成功！输出文件：{output_audio_file}"

# 创建界面
iface = gr.Interface(
    fn=extract_audio_and_remove_silence,
    inputs=["text", gr.Textbox(placeholder="不填则与输入路径相同")],
    outputs="text",
    title="音频文本提取",
    description="从视频（音频）中提取音频文件并去除空白。",
    allow_flagging="never"
)

iface.launch()
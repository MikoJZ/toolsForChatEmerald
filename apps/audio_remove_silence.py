from moviepy.editor import *
from pydub import AudioSegment
import os


def audio_remove_silence(audio_path):
    # 使用pydub去除音频中的静音部分
    sound = AudioSegment.from_wav(audio_path)

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
    audio_filename = os.path.splitext(os.path.basename(audio_path))[0]
    output_audio_file = f"../data/{audio_filename}_cleaned_audio.wav"

    # 导出处理后的音频
    combined_audio.export(output_audio_file, format="wav")

# 使用函数
audio_file_path = "../data/vocal_1-2_temp_audio.wav"  # 替换为你的视频文件路径
audio_remove_silence(audio_file_path)
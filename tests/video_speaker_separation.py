from moviepy.editor import VideoFileClip
from pyAudioAnalysis import audioSegmentation as aS
from pydub import AudioSegment
import os


# 从视频中提取音频文件
def extract_audio(video_file_path, audio_file_path):
    video = VideoFileClip(video_file_path)
    audio = video.audio
    audio.write_audiofile(audio_file_path)
    audio.close()
    video.close()

# 分离音频
# 使用pyAudioAnalysis来分离音频中的不同说话者。
def speaker_diarization(audio_file_path):
    # 设置 num_speakers 为 0 以启用自动检测说话者数量
    segments, _, _ = aS.speaker_diarization(audio_file_path, 0, plot_res=False)
    return segments

# 保存分离的音频
# # 根据分离出的说话者信息，将音频分割并保存为不同的文件。
def save_speaker_segments(audio_file_path, segments):
    audio = AudioSegment.from_file(audio_file_path)
    for i, segment in enumerate(segments):
        try:
            start, end = segment
            start = int(start * 1000)
            end = int(end * 1000)
            speaker_audio = audio[start:end]
            speaker_audio.export(f"../data/{video_name}_speaker_{i}.wav", format="wav")
        except (TypeError, ValueError):
            print(f"Invalid segment format at index {i}: {segment}")

def process_video(video_file_path):
    video_name = os.path.splitext(os.path.basename(video_file_path))[0]  # 提取视频文件名
    audio_file_path = f"../data/{video_name}_temp_audio.wav"
    extract_audio(video_file_path, audio_file_path)
    segments = speaker_diarization(audio_file_path)
    save_speaker_segments(audio_file_path, segments)

# 使用示例
process_video("../data/1-2.mp4")
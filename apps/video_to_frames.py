import cv2
import os

def video_to_frames(video_path, output_folder, interval):
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    current_frame = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        current_frame += 1

        if current_frame % interval == 0:
            frame_count += 1
            frame_name = f"frame_{frame_count}.jpg"
            output_path = os.path.join(output_folder, frame_name)
            cv2.imwrite(output_path, frame)
            print(f"Saved frame {frame_count}")

    cap.release()

if __name__ == "__main__":
    video_path = "RPReplay_Final1717141295.mov"

    # 获取视频文件名
    video_filename = os.path.basename(video_path)
    output_filename = os.path.splitext(video_filename)[0]  # 获取视频文件名（不含扩展名）
    output_folder = f'{output_filename}_frames'
    interval = 10  # 间隔帧数
    video_to_frames(video_path, output_folder, interval)
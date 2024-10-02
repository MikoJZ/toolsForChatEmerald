# video_processor.py

import cv2
import os
from collections import OrderedDict
from datetime import datetime

class VideoProcessor:
    def __init__(self, ocr, interval, specific_values, prefix, suffix):
        self.ocr = ocr
        self.interval = interval
        self.specific_values = specific_values
        self.prefix = prefix
        self.suffix = suffix

    def process_video(self, video_path, output_folder, update_text_callback):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_message = f"--- Processing started for file: {video_path} at {current_time} ---"
        update_text_callback(start_message)
        update_text_callback("--------------------------------------------------")

        # 读取视频
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return

        frame_count = 0
        text_dict = OrderedDict()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % self.interval == 0:
                result = self.ocr.ocr(frame)
                for line in result:
                    if line is not None and len(line) > 0:
                        text = ""
                        for tuple in line:
                            tuple_text = tuple[1][0]
                            # 检查文本是否在特定值数组中
                            if tuple_text in self.specific_values:
                                tuple_text = f"{self.prefix}{tuple_text}{self.suffix}"
                            text += tuple_text
                            update_text_callback(f"正在处理：“{text}”")
                        text_dict[text] = None

            frame_count += 1

        # 获取视频文件名
        video_filename = os.path.basename(video_path)
        output_filename = os.path.splitext(video_filename)[0]  # 获取视频文件名（不含扩展名）

        # 创建文件用于存储文字
        output_file_path = os.path.join(output_folder, f'{output_filename}.txt')
        output_file = open(output_file_path, 'w', encoding='utf-8')

        # 写入文件
        for text in text_dict.keys():
            output_file.write(text + '\n')

        # 关闭文件和释放资源
        output_file.close()
        cap.release()
        cv2.destroyAllWindows()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        end_message = f"--- Processing finished for file: {video_path} at {current_time} ---"
        update_text_callback(end_message)
        update_text_callback("--------------------------------------------------")
import cv2
from paddleocr import PaddleOCR
import os
from collections import OrderedDict
import re
import gradio as gr
from tkinter import filedialog

# 初始化PaddleOCR，使用角度分类器和中文语言模型
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 默认特定值文件路径
specific_values_file = "../data/specific_values.txt"

# 从文件中读取特定值
with open(specific_values_file, 'r', encoding='utf-8') as f:
    specific_values = f.read()

def process_video(video_path, interval, specific_values, caller, output_folder=None, sub_from=None, sub_to="", save_frames=False):
    try:
        # 验证video_path是否为视频文件
        if not video_path.endswith(('.mp4', '.avi', '.mov')):
            return "Error: Invalid video file format. Please provide a .mp4, .avi, or .mov file."

        # 验证output_folder是否为文件夹
        if output_folder and not os.path.isdir(output_folder):
            return "Error: Output folder path is not a valid directory."

        # 检查文件是否存在
        if not os.path.exists(video_path):
            return "Error: Video file does not exist."

        cap = cv2.VideoCapture(video_path)

        # 获取视频文件名并创建输出文件名
        video_filename = os.path.basename(video_path)
        output_filename = os.path.splitext(video_filename)[0]

        # 如果未指定输出文件夹，使用与输入相同的目录作为默认输出目录
        if not output_folder:
            output_folder = os.path.dirname(video_path)
        elif not os.path.exists(output_folder):
            os.makedirs(output_folder)

        if save_frames:
            # 创建存储帧的文件夹
            frames_folder = os.path.join(output_folder, f'{output_filename}_frames')
            os.mkdir(frames_folder)

        # 写入特定值到文件
        with open(specific_values_file, 'w', encoding='utf-8') as f:
            f.write(specific_values)

        # 文本提取，使用有序字典存储以避免重复
        text_dict = OrderedDict()

        frame_count = 0
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % interval == 0:
                    result = ocr.ocr(frame)
                    for line in result:
                        if line:
                            text = ""
                            for tuple in line:
                                tuple_text = tuple[1][0]
                                if tuple_text in specific_values:
                                    tuple_text += "："
                                text += tuple_text
                            # 绘旅人通讯特别处理（加入通话人）
                            if caller:
                                text = re.sub(r"通话中.*通讯|视频中.*\d{2}:\d{2}|5.5|全球通信.*通话中...", "", text)
                                if text and not text.startswith("我："):
                                    text = caller + "：" + text
                            if sub_from:
                                text = re.sub(sub_from, sub_to, text)
                            text_dict[text] = None

                            if save_frames:
                                cv2.imwrite(os.path.join(frames_folder, f"frame_{frame_count}.jpg"), frame)

                frame_count += 1
        finally:
            texts = list(text_dict.keys())
            filtered_texts = []

            for i in range(len(texts) - 1):
                current_text = texts[i]
                next_text = texts[i + 1]
                if not next_text.startswith(current_text) and not current_text.startswith(next_text) and next_text != current_text:
                    filtered_texts.append(current_text)
            filtered_texts.append(texts[-1])

            msg = ""
            # 创建文本输出文件
            output_file = open(os.path.join(output_folder, f'{output_filename}.txt'), 'w', encoding='utf-8')
            for text in filtered_texts:
                output_file.write(text + '\n')
                msg += text + '\n'

            output_file.close()
            cap.release()
            cv2.destroyAllWindows()

            return f"{msg}\nText extracted and saved to {output_filename}.txt"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# 创建界面
with gr.Blocks() as blocks:
    gr.Label("视频文本提取(绘旅人版)")
    gr.Markdown("从视频中提取文本并保存到文件中。")
    with gr.Row():
        with gr.Column():
            video_path = gr.Textbox(label="输入文件路径")
            output_folder = gr.Textbox(label="输出文件路径", placeholder="不填则与输入路径相同")
            interval = gr.Number(label="间隔帧", value=50)
            specific_values = gr.Text(label="人名检测（输入需要检测的人名，以‘,’号分隔，将在人名后加‘：’）", value=specific_values)
            caller = gr.Textbox(label="绘旅人通讯特别处理（加入通话人）", placeholder="如：叶瑄")
            with gr.Tab("替换文本"):
                sub_from = gr.Text(label="替换前：(可使用正则表达式)")
                sub_to = gr.Text(label="替换后：")
            save_frames = gr.Checkbox(label="Save Frames")
            submit_button = gr.Button("Submit", variant="primary")
            inputs = [video_path, interval, specific_values, caller, output_folder, sub_from, sub_to, save_frames]
        with gr.Column():
            outputs = gr.Textbox(label="输出信息")
    submit_button.click(process_video, inputs, outputs)

blocks.launch()
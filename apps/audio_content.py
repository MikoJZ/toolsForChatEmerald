import gradio as gr
import os
import whisper

# 加载 Whisper 模型
model = whisper.load_model("base")

def transcribe_and_rename(file_path):
    # 使用 Whisper 模型进行音频转录
    result = model.transcribe(file_path)
    # 获取转录的文本
    text = result['text'].strip().replace(" ", "_")  # 去除空格并替换为下划线
    # 获取文件扩展名
    file_extension = os.path.splitext(file_path)[1]
    # 构建新的文件名
    new_file_name = f"{text}{file_extension}"
    # 获取文件所在目录
    directory = os.path.dirname(file_path)
    # 构建新的文件路径
    new_file_path = os.path.join(directory, new_file_name)
    # 重命名文件
    os.rename(file_path, new_file_path)
    return new_file_path

def process_files(input_path):
    if os.path.isfile(input_path):
        # 如果是文件，直接转录并重命名
        return transcribe_and_rename(input_path)
    elif os.path.isdir(input_path):
        # 如果是文件夹，遍历文件夹中的所有文件
        renamed_files = []
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                renamed_files.append(transcribe_and_rename(file_path))
        return renamed_files
    else:
        return "输入路径无效"

# 使用 Gradio 创建界面
iface = gr.Interface(
    fn=process_files,
    inputs=gr.Textbox(label="输入文件或文件夹路径"),
    outputs="json",
    title="音频文件重命名工具"
)

# 启动 Gradio 应用
iface.launch()
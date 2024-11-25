import gradio as gr
import os


def remove_blank_lines_from_file(file):
    # 读取文件内容
    with open(file.name, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 过滤掉空白行
    non_empty_lines = [line for line in lines if line.strip() != '']

    # 构建新的文件名
    base, ext = os.path.splitext(file.name)
    new_file_name = f"{base}_noblank{ext}"

    # 将非空行写入新的文件
    with open(new_file_name, 'w', encoding='utf-8') as f:
        f.writelines(non_empty_lines)

    return new_file_name


# 创建 Gradio 界面
iface = gr.Interface(
    fn=remove_blank_lines_from_file,
    inputs="file",
    outputs="file",
    title="删除文件中的空白行",
    description="上传一个文件，删除其中所有的空白行，并保存为新文件。"
)

# 启动界面
iface.launch()
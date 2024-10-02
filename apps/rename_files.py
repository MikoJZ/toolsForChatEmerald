import os
import gradio as gr


def rename_files(folder_path, old_str, new_str):
    result = ""
    # 遍历指定文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件名中是否包含被替换词
        if old_str in filename:
            # 构造新的文件名,将被替换词替换为替换词
            new_filename = filename.replace(old_str, new_str)
            # 构造完整的文件路径
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_filename)
            # 重命名文件
            os.rename(old_file, new_file)
            result += "已将文件 '{filename}' 重命名为 '{new_filename}'\n"

    return result + "文件全部处理完成。"


folder_path = gr.Textbox(label="文件夹路径")
old_str = gr.Textbox(label="被替换词")
new_str = gr.Textbox(label="替换词")

iface = gr.Interface(fn=rename_files, title="文件重命名工具", inputs=[folder_path, old_str, new_str], outputs=gr.Textbox())

iface.launch()
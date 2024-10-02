import os
import shutil
import gradio as gr
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple


def get_unique_filename(dst_path: str) -> str:
    base, extension = os.path.splitext(dst_path)
    counter = 1
    while os.path.exists(dst_path):
        dst_path = f"{base}_{counter}{extension}"
        counter += 1
    return dst_path


def process_file(src_path: str, dst_path: str, operation: str) -> Tuple[str, str, bool]:
    original_name = os.path.basename(src_path)
    renamed = False
    try:
        if not os.path.exists(src_path):
            return original_name, f"错误: 源文件不存在", False

        if operation == "移动":
            if os.path.exists(dst_path):
                dst_path = get_unique_filename(dst_path)
                renamed = True
            shutil.move(src_path, dst_path)
        elif operation == "复制":
            if os.path.exists(dst_path):
                dst_path = get_unique_filename(dst_path)
                renamed = True
            shutil.copy2(src_path, dst_path)
        elif operation == "删除":
            os.remove(src_path)
            return original_name, "已删除", False

        return original_name, os.path.basename(dst_path), renamed
    except Exception as e:
        return original_name, f"错误: {str(e)}", False


def move_copy_or_delete_files(input_folders: str, output_folder: str, file_extensions: List[str], operation: str,
                              include_subfolders: bool) -> str:
    try:
        if operation != "删除":
            os.makedirs(output_folder, exist_ok=True)

        input_folders = [folder.strip() for folder in input_folders.split(',')]
        file_extensions = [ext.strip().lower() for ext in file_extensions]

        files_to_process = []
        for folder in input_folders:
            if not os.path.exists(folder):
                return f"错误: 输入文件夹不存在: {folder}"

            if include_subfolders:
                for root, _, files in os.walk(folder):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in file_extensions):
                            src_path = os.path.join(root, file)
                            dst_path = os.path.join(output_folder, file)
                            files_to_process.append((src_path, dst_path))
            else:
                for file in os.listdir(folder):
                    if os.path.isfile(os.path.join(folder, file)) and any(
                            file.lower().endswith(ext) for ext in file_extensions):
                        src_path = os.path.join(folder, file)
                        dst_path = os.path.join(output_folder, file)
                        files_to_process.append((src_path, dst_path))

        if not files_to_process:
            return "未找到匹配的文件"

        processed_files = []
        renamed_files = []
        errors = []

        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda x: process_file(*x, operation), files_to_process)

            for original, new, renamed in results:
                if new.startswith("错误:"):
                    errors.append(f"{original}: {new}")
                else:
                    processed_files.append(original)
                    if renamed:
                        renamed_files.append((original, new))

        result = f"成功{operation}了 {len(processed_files)} 个文件"
        if operation != "删除":
            result += f" 到 {output_folder}"
        result += "\n"
        if renamed_files:
            result += f"\n{len(renamed_files)} 个文件被重命名以避免冲突"
        if errors:
            result += f"\n\n{len(errors)} 个文件处理出错"

        return result
    except Exception as e:
        return f"发生错误: {str(e)}"


# 预定义的文件扩展名选项
predefined_extensions = [".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".png", ".mp3", ".mp4", ".wav"]

# Gradio界面代码
with gr.Blocks() as demo:
    gr.Markdown("## 文件移动/复制/删除工具")
    with gr.Row():
        with gr.Column():
            with gr.Column():
                input_folders = gr.Textbox(label="输入文件夹（多个文件夹用逗号分隔）")
                include_subfolders = gr.Checkbox(label="包含子文件夹", value=False)
            output_folder = gr.Textbox(label="输出文件夹（删除操作时可不填）")
            file_extensions = gr.Dropdown(choices=predefined_extensions, label="文件后缀名", multiselect=True,
                                          allow_custom_value=True)
            operation = gr.Radio(["移动", "复制", "删除"], label="操作")
            submit_btn = gr.Button("执行")
        with gr.Column():
            output = gr.Textbox(label="结果")

    submit_btn.click(
        move_copy_or_delete_files,
        inputs=[input_folders, output_folder, file_extensions, operation, include_subfolders],
        outputs=output
    )

demo.launch()
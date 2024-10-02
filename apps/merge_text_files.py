import os
import gradio as gr
from datetime import datetime

def merge_text_files(folder_path, file_type):
    output_file = os.path.join(folder_path, f"{os.path.basename(folder_path)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for root, _, files in os.walk(folder_path):
                for filename in files:
                    if filename.endswith(f'.{file_type}'):
                        with open(os.path.join(root, filename), 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read() + '\n')
        return f"所有.{file_type}文件已合并到 {output_file}"
    except Exception as e:
        return f"发生错误: {e}"
    finally:
        # 确保文件和文件夹资源被正确释放
        outfile.close()
        infile.close()

def main():
    folder_input = gr.Textbox(label="文件夹路径")
    file_type_input = gr.Dropdown(
        choices=["txt", "doc", "md"],
        value="txt",
        label="文件类型"
    )
    output_text = gr.Textbox(label="结果")

    interface = gr.Interface(
        fn=merge_text_files,
        inputs=[folder_input, file_type_input],
        outputs=output_text,
        title="文件合并器",
        description="将一个文件夹中所有指定类型的文件内容整合成一个文件"
    )

    interface.launch()

if __name__ == "__main__":
    main()
import os
from paddleocr import PaddleOCR
import glob
import gradio as gr

def extract_text(input_path, input_image=None, output_folder=None):
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # 初始化PaddleOCR，设定为中文识别
    # 输入来自于图片控件(这段无法独立成一个方法，否则报错)
    if not input_path and input_image.size > 0:
        ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # 初始化PaddleOCR，设定为中文识别
        try:
            result = ocr.ocr(input_image)
            if result:
                text = ""
                # 解析识别结果，提取文字
                for line in result:
                    if line:
                        for tuple in line:
                            tuple_text = tuple[1][0]
                            text += tuple_text + '\n'
                if text:
                    return text
                else:
                    return "No text found in this image."
        except Exception as e:
            return f"Error processing this image: {str(e)}.\n"
    elif not input_path and input_image.size == 0:
        return "未输入图像文件。"
    else:
        msg = ""
        # 验证output_folder是否为文件夹
        if output_folder is not None and not os.path.isdir(output_folder):
            return "Error: Output folder path is not a valid directory."

        # 检查输入是否为文件夹
        if os.path.isdir(input_path):
            files = glob.glob(os.path.join(input_path, '*.[jpJP][pnPN][gG]'))  # 查找目录下的所有图片文件
        elif os.path.isfile(input_path):  # 检查是否为单个文件
            files = [input_path]
        else:
            return "输入路径既不是有效的文件也不是目录。"

        # 如果未指定输出文件夹，使用与输入相同的目录作为默认输出目录
        if output_folder is None or output_folder == '':
            # 如果input_path是文件夹，直接使用该路径
            if os.path.isdir(input_path):
                output_folder = input_path
            # 如果input_path是文件，获取该文件所在的目录
            else:
                output_folder = os.path.dirname(input_path)

        # 确保输出目录存在
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for file in files:
            # 使用PaddleOCR进行文字识别
            try:
                result = ocr.ocr(file)

                # 检查是否有识别到的文字
                if result:
                    text = ""
                    # 解析识别结果，提取文字
                    for line in result:
                        if line:
                            for tuple in line:
                                tuple_text = tuple[1][0]
                                text += tuple_text + '\n'

                    # 判断是否有识别到的文字
                    if text:  # 只有当text不为空时才保存
                        # 构建输出文本文件的路径
                        base_name = os.path.basename(file)
                        txt_filename = os.path.splitext(base_name)[0] + '.txt'
                        txt_path = os.path.join(output_folder, txt_filename)

                        # 保存到文本文件
                        with open(txt_path, 'w', encoding='utf-8') as f:
                            f.write(text)
                        msg += f"Text from {base_name} saved to {txt_path}\n"
                    else:
                        msg += f"No text found in {file}, skipping this image.\n"
            except Exception as e:
                msg += f"Error processing {file}: {str(e)}, skipping this image.\n"

        return msg


# extract_text("D:/Emerald/Goods/Resource/hand-written letter1.jpg")

iface = gr.Interface(fn=extract_text, inputs=[gr.Textbox(placeholder="输入图片文件或文件夹路径"), gr.Image(), gr.Textbox(placeholder="不填则与输入路径相同")], outputs=gr.Textbox(),
                     title="提取图片中的文字",
                     description="输入路径和上传图片二选一，输入路径优先。\n输入的图片文件OCR结果会生成txt文件保存在输出路径。\n输出路径不填默认放在输入路径的文件夹。\n上传图片不生成文件，直接出结果。")
iface.launch()

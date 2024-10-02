import gradio as gr
#import pytesseract
from PIL import Image
import requests
from io import BytesIO

# 定义图片转文字的函数
def image_to_text(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    text = ""#pytesseract.image_to_string(image)
    return text

# 创建Gradio界面
iface = gr.Interface(
    fn=image_to_text,
    inputs=gr.inputs.Textbox(label="图片地址"),
    outputs="text",
    title="图片转文字",
    description="输入图片的URL，提取其中的文字内容。"
)

# 启动界面
iface.launch()
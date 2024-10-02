import cv2
from paddleocr import PaddleOCR
import os
from collections import OrderedDict

# 初始化PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 读取视频
video_path = '../data/3-14.mp4'
cap = cv2.VideoCapture(video_path)

# 获取视频文件名
video_filename = os.path.basename(video_path)
output_filename = os.path.splitext(video_filename)[0]  # 获取视频文件名（不含扩展名）

# 创建文件用于存储文字
output_file = open(f'{output_filename}.txt', 'w', encoding='utf-8')

# 创建文件夹用于存储帧
output_folder = f'{output_filename}_frames'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 提取视频中的文字
text_dict = OrderedDict()
interval = 50  # 间隔帧数设为变量

# 定义一个数组包含特定的值
specific_values = ['叶瑄', '优希沐']

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    if frame_count % interval == 0:
        result = ocr.ocr(frame)
        for line in result:
            print(f"line:{line}")
            if line is not None and len(line) > 0:
                text = ""
                for tuple in line:
                    tuple_text = tuple[1][0]
                    # 检查文本是否在特定值数组中
                    if tuple_text in specific_values:
                        tuple_text = f"{tuple_text}："
                    text = text + tuple_text
                print(f"text:{text}")

                text_dict[text] = None  # 使用None作为字典值，因为我们只关心键
                # 将帧保存到文件夹
                #cv2.imwrite(os.path.join(output_folder, f"frame_{frame_count}.jpg"), frame)

    frame_count += 1

# 写入文件
for text in text_dict.keys():
    output_file.write(text + '\n')

# 关闭文件和释放资源
output_file.close()
cap.release()
cv2.destroyAllWindows()
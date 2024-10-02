import cv2
from paddleocr import PaddleOCR
import os
from collections import OrderedDict

# 初始化PaddleOCR，使用角度分类器和中文语言模型
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 视频路径
video_path = '../data/3-26.mp4'
# 检查文件是否存在
if not os.path.isfile(video_path):
    print("Error: Video file does not exist.")
    exit(1)

cap = cv2.VideoCapture(video_path)

# 获取视频文件名并创建输出文件名
video_filename = os.path.basename(video_path)
output_filename = os.path.splitext(video_filename)[0]

# 创建文本输出文件
video_folder = os.path.dirname(video_path)
output_file = open(video_folder + f'/{output_filename}.txt', 'w', encoding='utf-8')

# 创建存储帧的文件夹
# output_folder = video_folder + f'/{output_filename}_frames'
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# 文本提取，使用有序字典存储以避免重复
text_dict = OrderedDict()
interval = 50  # 每隔50帧进行一次OCR处理

# 定义特定值数组
specific_values = ['叶瑄', '优希沐', '汉梅尔', '白银骑士', '罗夏', '司岚']

frame_count = 0
try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % interval == 0:
            result = ocr.ocr(frame)
            for line in result:
                # print(f"line:{line}")
                if line:
                    text = ""
                    for tuple in line:
                        tuple_text = tuple[1][0]
                        if tuple_text in specific_values:
                            tuple_text += "："
                        text += tuple_text
                    # print(f"text:{text}")

                    text_dict[text] = None  # 使用None作为字典值，因为我们只关心键
                    # 将帧保存到文件夹
                    # cv2.imwrite(os.path.join(output_folder, f"frame_{frame_count}.jpg"), frame)

        frame_count += 1
finally:
    # 写入文件
    # for text in text_dict.keys():
    #     output_file.write(text + '\n')

    # 准备写入文件的文本列表
    texts = list(text_dict.keys())
    filtered_texts = []

    # 过滤文本：如果下一行以当前行为开头，则不添加当前行
    for i in range(len(texts) - 1):
        current_text = texts[i]
        next_text = texts[i + 1]
        if not next_text.startswith(current_text):
            filtered_texts.append(current_text)
    # 添加最后一行，因为它不会被任何行开始
    filtered_texts.append(texts[-1])

    # 写入过滤后的文本到文件
    for text in filtered_texts:
        output_file.write(text + '\n')

    # 关闭文件和释放资源
    output_file.close()
    cap.release()
    cv2.destroyAllWindows()

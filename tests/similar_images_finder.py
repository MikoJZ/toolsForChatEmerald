import cv2
import os
import shutil

def calculate_similarity(image1, image2):
    img1 = cv2.imread(image1)
    img2 = cv2.imread(image2)

    # 转换为灰度图像
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 计算直方图
    hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])

    # 计算直方图相似性
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return similarity

def find_similar_images(target_image, folder_path, output_folder, threshold):
    os.makedirs(output_folder, exist_ok=True)

    image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]

    similarities = [(image, calculate_similarity(target_image, os.path.join(folder_path, image))) for image in image_files]
    similar_images = [img for img, sim in similarities if sim > threshold]

    for img in similar_images:
        source_path = os.path.join(folder_path, img)
        target_path = os.path.join(output_folder, img)
        shutil.copyfile(source_path, target_path)

if __name__ == "__main__":
    target_image = "IMG_2144.jpg"
    folder_path = "RPReplay_Final1717089789_frames"
    output_folder = "similar_images"
    threshold = 0.8  # 设置相似性阈值 取值范围是[-1, 1]。值越接近1表示两个直方图之间的相似性越高，值越接近-1表示两个直方图之间的相似性越低。

    find_similar_images(target_image, folder_path, output_folder, threshold)
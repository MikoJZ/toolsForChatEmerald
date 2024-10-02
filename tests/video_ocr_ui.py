# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QTextEdit, \
    QFileDialog, QMessageBox, QCheckBox, QSpinBox
from PyQt5.QtCore import pyqtSignal, QThread
from paddleocr import PaddleOCR
from video_ocr_logic import VideoProcessor


class OCRThread(QThread):
    update_text = pyqtSignal(str)
    #finished = pyqtSignal()
    widget_enabled = pyqtSignal(bool)

    def __init__(self, video_path, output_folder, processor):
        super().__init__()
        self.video_path = video_path
        self.output_folder = output_folder
        self.processor = processor

    def run(self):
     # 在处理开始后发送信号通知主窗口冻结界面
     self.widget_enabled.emit(False)
     self.processor.process_video(self.video_path, self.output_folder, self.update_text.emit)
     #self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.total_videos = 0  # 总视频数量
        self.processed_videos = 0  # 已处理视频数量

    def initUI(self):
        self.setWindowTitle('视频文字识别')
        self.setGeometry(100, 100, 800, 600)

        # 基本设置区域
        self.basic_settings_layout = QVBoxLayout()

        self.video_path_input = QTextEdit(self)
        self.video_path_input.setPlaceholderText("请输入视频文件地址...")
        self.basic_settings_layout.addWidget(self.video_path_input)

        self.browse_button = QPushButton('浏览', self)
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.basic_settings_layout.addWidget(self.browse_button)

        self.output_folder_input = QLineEdit(self)
        self.output_folder_input.setPlaceholderText("请输入输出文件夹地址，如果为空则保存在第一个视频文件所在的路径")
        self.basic_settings_layout.addWidget(self.output_folder_input)

        self.output_folder_button = QPushButton('选择文件夹', self)
        self.output_folder_button.clicked.connect(self.open_output_folder_dialog)
        self.basic_settings_layout.addWidget(self.output_folder_button)

        self.interval_spinbox = QSpinBox(self)
        self.interval_spinbox.setValue(50)
        self.basic_settings_layout.addWidget(self.interval_spinbox)

        self.save_frame_checkbox = QCheckBox('保留截图', self)
        self.basic_settings_layout.addWidget(self.save_frame_checkbox)

        self.specific_values_input = QLineEdit(self)
        self.specific_values_input.setPlaceholderText("请输入特定值，用逗号分隔...")
        self.basic_settings_layout.addWidget(self.specific_values_input)

        self.prefix_input = QLineEdit(self)
        self.prefix_input.setPlaceholderText("请输入前缀...")
        self.basic_settings_layout.addWidget(self.prefix_input)

        self.suffix_input = QLineEdit(self)
        self.suffix_input.setPlaceholderText("请输入后缀...")
        self.basic_settings_layout.addWidget(self.suffix_input)

        # 文本设置区域
        text_settings_layout = QVBoxLayout()

        self.text_display = QTextEdit(self)
        self.text_display.setPlaceholderText("处理记录将显示在这里...")
        text_settings_layout.addWidget(self.text_display)

        # 按钮设置区域
        button_settings_layout = QVBoxLayout()

        self.start_button = QPushButton('开始', self)
        self.start_button.clicked.connect(self.start_processing)
        button_settings_layout.addWidget(self.start_button)

        self.cancel_button = QPushButton('取消', self)
        self.cancel_button.clicked.connect(self.cancel_processing)
        button_settings_layout.addWidget(self.cancel_button)

        # 添加基本设置，文本设置和按钮设置到主界面
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.basic_settings_layout)
        main_layout.addLayout(text_settings_layout)
        main_layout.addLayout(button_settings_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def widget_enabled_handler(self, status):
        if not status:
            for i in range(self.basic_settings_layout.count()):
                widget = self.basic_settings_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setEnabled(False)
            self.start_button.setEnabled(False)
        else:
            for i in range(self.basic_settings_layout.count()):
                widget = self.basic_settings_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setEnabled(True)
            self.start_button.setEnabled(True)
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "选择视频文件", "", "视频文件 (*.mp4 *.avi)", options=options)
        if files:
            for file in files:
                self.video_path_input.append(file)  # 逐条添加文件路径到文本框


    # 弹出文件对话框功能选择输出文件夹路径
    def open_output_folder_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹", "", options=options)
        if folder_path:
            self.output_folder_input.setText(folder_path)


    # 在 start_processing 方法中触发视频处理逻辑
    # "开始"按钮
    def start_processing(self):
        video_paths = self.video_path_input.toPlainText().split('\n')
        output_folder = self.output_folder_input.text()
        # 检查存放文档的路径是否为空，如果为空则设置为第一个视频文件所在的路径
        if not output_folder:
            output_folder = os.path.dirname(video_paths[0])
            self.output_folder_input.setText(output_folder)

        self.total_videos = len(video_paths)  # 总视频数量

        def ocr_thread_finished():
            self.processed_videos += 1
            if self.processed_videos == self.total_videos:
                # 打开存放文档的路径
                if os.path.exists(output_folder):
                    os.startfile(output_folder)
                self.widget_enabled.emit(True)

        for video_path in video_paths:
            if video_path:
                ocr = PaddleOCR(use_angle_cls=True, lang='ch')
                processor = VideoProcessor(ocr, self.interval_spinbox.value(),
                                           [value.strip() for value in self.specific_values_input.text().replace('，', ',').split(',')], # 中文逗号的Unicode编码为\uFF0C
                                           self.prefix_input.text(), self.suffix_input.text())
                self.ocr_thread = OCRThread(video_path, output_folder, processor)
                self.ocr_thread.update_text.connect(self.update_text_display)
                self.ocr_thread.finished.connect(ocr_thread_finished)
                self.ocr_thread.widget_enabled.connect(self.widget_enabled_handler)
                self.ocr_thread.start()

    # 在 cancel_processing 方法中取消视频处理逻辑
    # "取消"按钮
    def cancel_processing(self):
        if self.ocr_thread.isRunning():
            self.ocr_thread.terminate()

    def update_text_display(self, text):
        self.text_display.append(text)
        self.text_display.ensureCursorVisible()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    app.exec_()
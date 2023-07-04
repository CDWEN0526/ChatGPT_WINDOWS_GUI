import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextBrowser, QPlainTextEdit, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSlot
import markdown
import requests
import json



#api获取
def create_completion(messages: list):
    url = 'https://chat.aivvm.com/api/chat'
    data = {
        "model":{"id":"gpt-3.5-turbo-16k","name":"GPT-3.5-16K"},
        "messages":messages,
        "key":"",
        "prompt":"You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown.",
        "temperature":1
        }
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
        'Referer':'https://chat.aivvm.com/zh',
        'Content-Type':'application/json',
    }

    data = json.dumps(data)
    r = requests.post(url=url,data=data,headers=header)
    print(r.text,r.status_code)
    return r.text

#运行指定功能
class MyRunnable(QRunnable):
    def __init__(self, input_value, callback,submit_button):
        super().__init__()
        self.input_value = input_value
        self.callback = callback
        self.submit_button = submit_button

    @pyqtSlot()
    def run(self):
        processed_value = self.process_data(self.input_value)
        self.callback(processed_value)

    def process_data(self, data):
        # 在这里添加数据处理逻辑
        # 示例：将输入的数据转换为Markdown格式的HTML
        messages.append({"role": "user", "content": data})
        response = create_completion(messages=messages)
        bot = {'content':response,'role':'assistant'}
        messages.append(bot)
        markdown_html = markdown.markdown(response,extensions=['markdown.extensions.extra'])
        self.submit_button.setEnabled(True)
        print(messages)
        return markdown_html

#qt5窗口
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 创建垂直布局
        layout = QVBoxLayout()

        # 创建标题标签
        output_label = QLabel(f'欢迎使用GPT-3.5版本,本软件有持续对话的能力!\n清除历史: 将会让gpt失去对你之前提问的记忆,关闭软件也一样会清除gpt记忆。\n作者：Davin\n版本：{version}', self)
        output_label.setStyleSheet('color: #EEE; font-size: 12px; font-weight: bold;')
        layout.addWidget(output_label)

        # 创建输出信息框
        self.output_text = QTextBrowser(self)
        layout.addWidget(self.output_text)


        # 创建标题标签
        title_label = QLabel('请输入对ChatGpt的提问：', self)
        title_label.setStyleSheet('color: #EEE; font-size: 12px; font-weight: bold;')
        layout.addWidget(title_label)

        # 创建输入框
        self.input_text = QPlainTextEdit(self)
        self.input_text.setFixedSize(600, 100)  # 设置输入框大小为 400x200
        layout.addWidget(self.input_text)

        # 创建提交按钮
        self.submit_button = QPushButton('提交', self)
        self.submit_button.clicked.connect(self.handle_submit)
        layout.addWidget(self.submit_button)

        # 创建清屏按钮
        self.clear_button = QPushButton('清屏', self)
        self.clear_button.clicked.connect(self.handle_clear)
        layout.addWidget(self.clear_button)

        # 创建清除历史按钮
        self.clear_history_button = QPushButton('清除历史', self)
        self.clear_history_button.clicked.connect(self.handle_clear_history)
        layout.addWidget(self.clear_history_button)

        # 设置窗口布局
        self.setLayout(layout)

        # 设置窗口标题和初始大小
        self.setWindowTitle('Free GPT')
        self.setGeometry(600, 600, 600, 800)

        # 设置黑色系风格样式表
        self.setStyleSheet('''
            QWidget {
                background-color: #333;
            }
            QTextBrowser {
                color: #EEE;
                background-color: #222;
                border: none;
            }
            QPlainTextEdit {
                color: #EEE;
                background-color: #222;
                border: none;
            }
            QPushButton {
                color: #EEE;
                background-color: #444;
                border: 1px solid #555;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #888;
            }
        ''')

        # 设置输出信息框字体
        font = QFont('Courier New')
        self.output_text.setFont(font)

        # 设置输出信息框只读
        self.output_text.setReadOnly(True)

        # 将输入框焦点设置为初始状态
        self.input_text.setFocus()

        # 创建线程池
        self.threadpool = QThreadPool()

        # 显示窗口
        self.show()

    def handle_submit(self):
        input_value = self.input_text.toPlainText()

        # 创建异步任务并将其添加到线程池中
        runnable = MyRunnable(input_value, self.handle_result, self.submit_button)
        self.submit_button.setEnabled(False)
        self.threadpool.start(runnable)
        self.output_text.append(f'<div><span style="color: #FFA500;">【我】:</span></div>')
        self.output_text.append(f'{input_value}')
        self.input_text.clear()

    def handle_result(self, result):
        self.output_text.append(f'<div><span style="color: #00FF00;">【ChatGpt】:</span></div>')
        self.output_text.append(f'{result}')

    def handle_clear(self):
        self.output_text.clear()

    def handle_clear_history(self):
        self.output_text.append(f'<span style="color: red;">执行：</span>【清除历史提问，会清除掉你之前与GPT的对话，GPT也不再根据上下文回答你的问题！】\n\n')
        messages.clear()


if __name__ == '__main__':
    messages = []
    version = "v2.2"
    app = QApplication(sys.argv)
    widget = MyWidget()
    sys.exit(app.exec_())

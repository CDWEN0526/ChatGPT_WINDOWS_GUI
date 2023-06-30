import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextBrowser, QPlainTextEdit, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSlot
import markdown
import os
import requests
import re
import base64

#api获取
def create_completion(messages: list):
    def get_nonce():
        res = requests.get('https://chatgptlogin.ac/use-chatgpt-free/', headers={
            "Referer": "https://chatgptlogin.ac/use-chatgpt-free/",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        })

        src = re.search(r'class="mwai-chat mwai-chatgpt">.*<span>Send</span></button></div></div></div> <script defer src="(.*?)">', res.text).group(1)
        decoded_string = base64.b64decode(src.split(",")[-1]).decode('utf-8')
        return re.search(r"let restNonce = '(.*?)';", decoded_string).group(1)
    
    def transform(messages: list) -> list:
        def html_encode(string: str) -> str:
            table = {
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '>': '&gt;',
                '<': '&lt;',
                '\n': '<br>',
                '\t': '&nbsp;&nbsp;&nbsp;&nbsp;',
                ' ': '&nbsp;'
            }
            
            for key in table:
                string = string.replace(key, table[key])
                
            return string
        
        return [{
            'id': os.urandom(6).hex(),
            'role': message['role'],
            'content': message['content'],
            'who': 'AI: ' if message['role'] == 'assistant' else 'User: ',
            'html': html_encode(message['content'])} for message in messages]
    
    headers = {
        'authority': 'chatgptlogin.ac',
        'accept': '*/*',
        'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
        'content-type': 'application/json',
        'origin': 'https://chatgptlogin.ac',
        'referer': 'https://chatgptlogin.ac/use-chatgpt-free/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'x-wp-nonce': get_nonce()
    }
    
    conversation = transform(messages)

    json_data = {
        'env': 'chatbot',
        'session': 'N/A',
        'prompt': 'Converse as if you were an AI assistant. Be friendly, creative.',
        'context': 'Converse as if you were an AI assistant. Be friendly, creative.',
        'messages': conversation,
        'newMessage': messages[-1]['content'],
        'userName': '<div class="mwai-name-text">User:</div>',
        'aiName': '<div class="mwai-name-text">AI:</div>',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.8,
        'maxTokens': 1024,
        'maxResults': 1,
        'apiKey': '',
        'service': 'openai',
        'embeddingsIndex': '',
        'stop': '',
        'clientId': os.urandom(6).hex()
    }
    try:
        response = requests.post('https://chatgptlogin.ac/wp-json/ai-chatbot/v1/chat', 
                             headers=headers, json=json_data)
        print(response.text)
        return response.json()['reply']
    except:
        return "请求异常，请重新点击提交。或者清理历史数据重新提问。"


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
        markdown_html = markdown.markdown(response,extensions=['markdown.extensions.extra'])
        self.submit_button.setEnabled(True)
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
        output_label = QLabel('欢迎使用GPT-3.5 Turbo版本,本软件有持续对话的能力!\n清除历史: 将会让gpt失去对你之前提问的记忆,关闭软件也一样会清除gpt记忆。\n数据源：chatgptlogin.ac\n作者：Davin', self)
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

        self.output_text.append(f'<div><span style="color: #FFA500;">【我】:</span><br>{input_value}</div><br>')
        self.input_text.clear()

    def handle_result(self, result):
        self.output_text.insertHtml(f'<div><span style="color: #00FF00;">【ChatGpt】:</span>{result}</div>')

    def handle_clear(self):
        self.output_text.clear()

    def handle_clear_history(self):
        self.output_text.append(f'<span style="color: red;">执行：</span>【清除历史提问，会清除掉你之前与GPT的对话，GPT也不再根据上下文回答你的问题！】\n\n')
        messages.clear()

if __name__ == '__main__':
    messages = []
    app = QApplication(sys.argv)
    widget = MyWidget()
    sys.exit(app.exec_())

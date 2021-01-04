import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui import Ui_MainWindow
from spider import *


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.Handle_init()  # 初始化槽函数
        self.baseUrl = 'https://www.shicimingju.com'
        # 模式字典
        self.choices = {'作者': 0, '标题': 1, '诗句': 2, '句首': 3, '句尾': 4, '古籍': 5, '成语': 6}
        self.choice = ''
        self.choiceId = 0
        self.keys = ''
        self.datas = ''
        self.dirs = ''
        self.fpath = ''

    # 绑定每个按钮到方法
    def Handle_init(self):
        self.searchButton.clicked.connect(self.search_keys)
        self.saveDataButton.clicked.connect(self.save_data)
        self.generateWordCloudButton.clicked.connect(self.generate_word_cloud)

    # 搜索
    def search_keys(self):
        self.outputText.clear()
        self.datas = ''
        self.choice = self.choiceBox.currentText()
        self.choiceId = self.choices[self.choice]
        self.keys = self.inputText.text()
        url = get_url(self.baseUrl, self.choiceId, self.keys)

        if self.choiceId == 0:
            status = True
            nextUrl = url
            while (nextUrl != self.baseUrl):
                self.outputText.insertPlainText('正在爬取 ' + nextUrl + '\n')
                html = get_html(nextUrl)
                data, nextUrl, status = get_data_zuozhe(html, status)
                self.datas += data
                nextUrl = self.baseUrl + nextUrl
        elif self.choiceId >= 1 and self.choiceId <= 4:
            self.outputText.insertPlainText('正在爬取 ' + url + '\n')
            html = get_html(url)
            data = get_data_part(html)
            self.datas += data
        elif self.choiceId == 5:
            self.outputText.insertPlainText('正在爬取 ' + url + '\n')
            html = get_html(url)
            data = get_data_book(self.baseUrl, html)
            self.datas += data
        elif self.choiceId == 6:
            self.outputText.insertPlainText('正在爬取 ' + url + '\n')
            html = get_html(url)
            data = get_data_chengyu(html)
            self.datas += data

        time.sleep(1)

        if self.choiceId == 0:
            findFG = re.compile(r'(.*?)---', re.S)
            intro = re.findall(findFG, self.datas)[0]
            self.outputText.insertPlainText('\n' + self.keys + '\n' + intro + '\n点击保存数据以查看\n')
        else:
            self.outputText.insertPlainText(self.datas + '\n')

    # 保存数据
    def save_data(self):
        self.dirs = os.path.join('datas', self.choice, self.keys)
        if os.path.isdir(self.dirs) == False:
            os.makedirs(self.dirs)

        self.fpath = os.path.join(self.dirs, 'contents.txt')
        with open(self.fpath, 'w', encoding='utf-8') as f:
            f.write(self.datas)

        self.outputText.insertPlainText("数据已保存至 " + self.fpath + '\n\n')

    # 生成词云图
    def generate_word_cloud(self):
        title_dict = change_title_to_dict(self.fpath)
        title_dict_sorted = sorted(title_dict.items(), key=lambda x: x[1], reverse=True)  # 将字典按照value值从小到大排序，再逆序

        frequency = "出现频率最高的10个词为：\n"
        for i in range(10):
            frequency += title_dict_sorted[i][0] + "：" + str(title_dict_sorted[i][1]) + "次\n"

        self.outputText.insertPlainText(frequency + "\n正在生成词云图...\n")
        dict_to_cloud(title_dict, self.dirs, self.keys)
        self.outputText.insertPlainText("词云图已保存至 " + os.path.join(self.dirs, '词云.png') + '\n\n')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MyWindow()
    MainWindow.show()
    sys.exit(app.exec_())

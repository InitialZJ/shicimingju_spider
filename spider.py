import os
import time
import requests
from bs4 import BeautifulSoup
import re
from xpinyin import Pinyin
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image, ImageFont, ImageDraw
import numpy as np


# 获取目标链接
def get_url(baseUrl, choiceId, keys):
    findUrl = re.compile(r'<a href="(.*?)" target="_blank">')  # 目标链接匹配规则
    if choiceId == 0:
        keysUrl = 'https://www.shicimingju.com/chaxun/zuozhe_list/' + keys
        html = get_html(keysUrl)
        bs = BeautifulSoup(html, 'html.parser')
        zuozhe = bs.select('div.card.zuozhe_card > div.zuozhe_list_item > h3')
        zzUrl = re.findall(findUrl, str(zuozhe))[0]
        url = baseUrl + zzUrl
    elif choiceId == 1:
        keysUrl = 'https://www.shicimingju.com/chaxun/shici/' + keys
        html = get_html(keysUrl)
        bs = BeautifulSoup(html, 'html.parser')
        shici = bs.select('div.card.shici_card > div.shici_card_sub > div.shici_list_main > h3 > a')
        scUrl = re.findall(findUrl, str(shici))[0]
        url = baseUrl + scUrl
    elif choiceId == 2:
        keysUrl = 'https://www.shicimingju.com/chaxun/shiju/' + keys
        html = get_html(keysUrl)
        bs = BeautifulSoup(html, 'html.parser')
        shiju = bs.select('div.card.shici_card > div.shici_card_sub > div.shiju_list_main > h3 > a')
        sjUrl = re.findall(findUrl, str(shiju))[0]
        url = baseUrl + sjUrl
    elif choiceId == 3:
        keysUrl = 'https://www.shicimingju.com/chaxun/shiju/first/' + keys
        html = get_html(keysUrl)
        bs = BeautifulSoup(html, 'html.parser')
        first = bs.select('div.card.shici_card > div.shici_card_sub > div.shiju_list_main > h3 > a')
        fUrl = re.findall(findUrl, str(first))[0]
        url = baseUrl + fUrl
    elif choiceId == 4:
        keysUrl = 'https://www.shicimingju.com/chaxun/shiju/end/' + keys
        html = get_html(keysUrl)
        bs = BeautifulSoup(html, 'html.parser')
        end = bs.select('div.card.shici_card > div.shici_card_sub > div.shiju_list_main > h3 > a')
        eUrl = re.findall(findUrl, str(end))[0]
        url = baseUrl + eUrl
    elif choiceId == 5:
        p = Pinyin()
        keys_pinyin = p.get_pinyin(keys, '')
        url = 'https://www.shicimingju.com/book/' + keys_pinyin + '.html'
    elif choiceId == 6:
        keysUrl = 'https://www.shicimingju.com/chengyu/chaxun?kw=' + keys
        html = get_html(keysUrl)
        bs = BeautifulSoup(html, 'html.parser')
        chengyu = bs.select('div.card.shici_card > div.shici_card_sub > div.shiju_list_main > h3 > a')
        cyUrl = re.findall(findUrl, str(chengyu))[0]
        url = baseUrl + cyUrl

    return url

# 获取网页源代码
def get_html(url):
    global response
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    }
    html = None

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print("未能正确爬取页面：" + str(e))
    finally:
        time.sleep(1)
        response.close()

    return html

# 作者模式下获取数据
def get_data_zuozhe(html, status):
    data = ""
    bs = BeautifulSoup(html, 'html.parser')

    # 第一次调用函数时，获取页面中的作者信息，之后不再获取
    if status:
        status = False
        intro_zuozhe = ''
        intros = bs.select('div.card.about_zuozhe > div > div > div.des')
        for intro in intros:
            intro_zuozhe += intro.text.replace("\n", "").replace("\t","").replace(" ", "")
        dynasty = bs.select('div.card.about_zuozhe > div > div.aside_left > div.aside_val > a')[0].text
        works = bs.select('div.card.about_zuozhe > div > div.aside_right > div.aside_val > a')[0].text
        data = intro_zuozhe + '\n' + '年代：' + dynasty  + '\n''收录作品：' + works + '\n' + '---\n'

    titles = bs.select('div.shici_list_main > h3 > a')  # 获取诗词题
    infos = bs.select('div.shici_list_main > div.shici_content')  # 获取诗词内容
    # 结合bs.select和re.compile匹配下一页的链接
    nextUrl = bs.select('div#list_nav_part')
    findNU = re.compile(r'href="(.*?)">下一页')
    nextUrl = re.findall(findNU, str(nextUrl))
    nextUrl = "".join(nextUrl)

    for title, info in zip(titles, infos):
        data += title.text + '\n' + info.text.replace("收起", "").replace("展开全文", "").replace("\n", "").replace("\t","").replace(" ", "") + '\n'

    return data, nextUrl, status

# 标题、诗句、句首、句尾模式下获取数据
def get_data_part(html):
    bs = BeautifulSoup(html, 'html.parser')

    title = ""
    for t in bs.select('div#item_div.card > h1#zs_title'):
        title += t.text

    zuozhe = ""
    for z in bs.select('div#item_div.card > div.niandai_zuozhe'):
        zuozhe += z.text

    content = ""
    for c in bs.select('div#item_div.card > div#zs_content.item_content'):
        content += c.text.replace("\n", "").replace("\t", "").replace(" ", "")

    shangxi = ""
    for s in bs.select('div#item_shangxi.card > div.shangxi_content'):
        shangxi += s.text.replace("\n", "").replace("\t", "").replace(" ", "")

    data = '\n' + title + '\n' + zuozhe + '\n' + content + '\n\n作品赏析：' + shangxi + '\n'
    return data

# 古籍模式下获取数据
def get_data_book(baseUrl, html):
    bs = BeautifulSoup(html, 'html.parser')
    # 本模式下仅获取古籍目录及链接
    mulu = bs.select('div.book-mulu > ul > li > a')
    findBU = re.compile(r'href="(.*?)">')

    data = ''
    for m in mulu:
        data += m.text.replace("\n", "") + '\n' + baseUrl + re.findall(findBU, str(m))[0] + '\n'

    return data

# 成语模式下获取数据
def get_data_chengyu(html):
    bs = BeautifulSoup(html, 'html.parser')
    chengyu = bs.select('div.card > h1')[0].text
    content = bs.select('div.card > table.chengyu-table')[0].text
    contents = content.split()
    # 仅获取词目发音、释义、出处、近义词、反义词
    data = '\n' + chengyu + '\n' + contents[0] + '：' + contents[1] + '\n' +\
           contents[2] + '：' + contents[3] + ' ' + contents[4] + ' ' +\
           contents[5] + ' ' + contents[6] + '\n' + contents[7] + '：' +\
           contents[8] + '\n', contents[9] + '：' + contents[10] + '\n' +\
           contents[11] + '：' + contents[12] + '\n' + contents[13] + '：' + contents[14]
    return "".join(data)

def change_title_to_dict(fpath):
    with open(fpath, "r", encoding='utf-8') as f:
        str = f.read()
        stringList = list(jieba.cut(str))  # 使用jieba分词

        # 获取停用词set
        delWord = set()
        with open('cn_stopwords.txt', "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                delWord.add(line.strip('\n'))
        delWord.update({'\n', '\t', ' '})

        # 删除诗词中的停用词
        stringSet = set(stringList) - delWord
        title_dict = {}

        # 对各个词计数
        for i in stringSet:
            title_dict[i] = stringList.count(i)

    return title_dict

# 生成作者姓名对应的图片
def name_to_img(dirs, keys):
    im = Image.new("RGB", (len(keys) * 1000, 1150), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    font = r'C:\Windows\Fonts\方正粗黑宋简体.ttf'
    font = ImageFont.truetype(font, 1000)
    dr.text((0, 0), keys, font=font, fill="#000000")
    im.save(os.path.join(dirs, 'name.png'))

# 生成词云图
def dict_to_cloud(title_dict, dirs, keys):
    name_to_img(dirs, keys)
    font_path = r'C:\Windows\Fonts\simhei.ttf'
    mask = np.array(Image.open(os.path.join(dirs, 'name.png')))
    wc = WordCloud(background_color='white', max_words=500, font_path=font_path, mask=mask)
    wc.generate_from_frequencies(title_dict)
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
    plt.savefig(os.path.join(dirs, '词云.png'), dpi=500)  # 保存词云图

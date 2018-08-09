#coding:utf-8

import itchat
import re
import io
from os import path
from wordcloud import WordCloud, ImageColorGenerator
import jieba
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import random
import os
from matplotlib import pyplot as plt


def draw(datas):
    sex = ['unknown', 'male', 'female' ]
    keys = [0, 1, 2]
    for i in keys:
        # 画柱状图
        plt.bar(i, datas[i])

    # 横坐标转换
    plt.xticks(keys, sex)

    plt.legend()
    # 标题文字
    plt.xlabel('sex')
    plt.ylabel('number')
    plt.title("Gender of Leo's friends")
    # 显示图片
    plt.show()

def parse_friends():
    # 爬取自己好友相关信息，返回一个json文件
    itchat.login()
    text = dict()
    friends = itchat.get_friends(update=True)[0:]

    # friends[0]是自己的信息，所以要从friends[1]开始
    for i in friends[1:]:
        sex = i['Sex']
        if sex == 1:
            text[1] = text.get(1, 0) + 1
        elif sex == 2:
            text[2] = text.get(2, 0) + 1
        else:
            text[0] = text.get(0, 0) + 1

    # 计算朋友总数
    total = len(friends[1:])

    # 打印出自己的好友性别个数
    print("man： %d" % text[1] + "\n" +
          "woman： %d" % text[2] + "\n" +
          "unknown： %d" % text[0])
    # 打印出自己的好友性别比例
    print("man： %.2f%%" % (float(text[1]) / total * 100) + "\n" +
          "woman： %.2f%%" % (float(text[2]) / total * 100) + "\n" +
          "unknown： %.2f%%" % (float(text[0]) / total * 100))

    # 将统计结果画图显示
    draw(text)

def parse_signature():
    itchat.login()
    siglist = []
    friends = itchat.get_friends(update=True)[1:]
    for i in friends:
        # 用正则表达式替换掉无关紧要的词
        signature = i["Signature"].strip().replace("span", "").replace("class", "").replace("emoji", "")
        rep = re.compile("1f\d+\w*|[<>/=]")
        signature = rep.sub("", signature)
        siglist.append(signature)

    # 再把所有拼起来，得到text字串
    text = "".join(siglist)

    with io.open('text.txt', 'a', encoding='utf-8') as f:
        # 使用结巴分词
        wordlist = jieba.cut(text, cut_all=True)
        word_space_split = " ".join(wordlist)
        f.write(word_space_split)
        f.close()

# 画图（词云）
def draw_signature():
    text = open(u'text.txt', encoding='utf-8').read()
    # 选择底色图片
    coloring = np.array(Image.open('pic.dib'))
    my_wordcloud = WordCloud(background_color="white", max_words=2000,
                         mask=coloring, max_font_size=40, min_font_size=5, random_state=42, scale=2,
                         # 选择字体文件
                         font_path="C:\Windows\Fonts\STKAITI.TTF").generate(text)
    image_colors = ImageColorGenerator(coloring)
    plt.imshow(my_wordcloud.recolor(color_func=image_colors))
    plt.imshow(my_wordcloud)
    plt.axis("off")
    plt.show()


if __name__ == '__main__':
    # 统计好友性别信息并画图
    # parse_friends()
    # 爬取好友个性签名保存到文本文件
    # parse_signature()
    # 根据文本文件画出词云
    draw_signature()
import itchat
import os
import time
# import cv2

# 自动回复消息
sendMsg = u"【消息助手】：暂时无法回复"
# 使用方法示例消息
usageMsg = u"使用方法：\n1.运行CMD命令：cmd xxx (xxx为命令)\n" \
           u"-例如关机命令:\ncmd shutdown -s -t 0 \n" \
           u"2.获取当前电脑用户：cap\n3.启用消息助手(默认关闭)：ast\n" \
           u"4.关闭消息助手：astc"
# 消息助手开关标志位，默认关闭
flag = 0
# 获取当前时间
nowTime = time.localtime()
# 根据当前时间命名临时文本文件
filename = str(nowTime.tm_mday)+str(nowTime.tm_hour)+str(nowTime.tm_min)+str(nowTime.tm_sec)+".txt"
myfile = open(filename, 'w')

# itchat的注册操作
# 此处只需要获取最简单的文本消息
@itchat.msg_register('Text')
def text_reply(msg):
    # 消息助手开关标志位
    global flag
    # 消息内容字段
    message = msg['Text']
    # 消息发送方
    fromName = msg['FromUserName']
    # 消息接收方
    toName = msg['ToUserName']

    # 接收用户指令
    # 暂时只用文件传输助手做示例
    if toName == "filehelper":
        # if message == "cap":
        #     cap = cv2.VideoCapture(0)
        #     ret, img = cap.read()
        #     cv2.imwrite("weixinTemp.jpg", img)
        #     itchat.send('@img@%s'%u'weixinTemp.jpg', 'filehelper')
        #     cap.release()
        if message[0:3] == "cmd":
            os.system(message.strip(message[0:4]))
        if message == "ast":
            flag = 1
            itchat.send("消息助手已开启", "filehelper")
        if message == "astc":
            flag = 0
            itchat.send("消息助手已关闭", "filehelper")
    elif flag == 1:
        # 自动回复
        # itchat.send(sendMsg, fromName)
        # 记录发送者
        myfile.write(fromName)
        myfile.write(" ： ")
        # 记录消息
        myfile.write(message)
        myfile.write("\n")
        myfile.flush()

        # 将消息直接转发给文件传输助手
        itchat.send(message, "filehelper")

if __name__ == '__main__':
    # 扫码登陆
    itchat.auto_login(hotReload=True)
    # 控制网页版微信向文件传输助手发送消息，说明使用方法
    itchat.send(usageMsg, "filehelper")
    itchat.run()
import json
import urllib.request as request
import random
from datetime import datetime
from PyQt5 import QtWidgets
from UI import Ui_MainWindow
from PyQt5.QtCore import QDate
from random import sample

class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_time()
        self.setup_control()

    def set_time(self):
        self.ui.dateEdit_2.setDate(QDate.currentDate())
        self.ui.dateEdit_1.setMinimumDate(QDate.currentDate().addDays(-3650))
        self.ui.dateEdit_1.setMaximumDate(QDate.currentDate().addDays(1))
        self.ui.dateEdit_1.setCalendarPopup(True)
        self.ui.dateEdit_2.setMinimumDate(QDate.currentDate().addDays(-3650))
        self.ui.dateEdit_2.setMaximumDate(QDate.currentDate().addDays(1))
        self.ui.dateEdit_2.setCalendarPopup(True)

    def setup_control(self):
        # TODO
        # qpushbutton doc: https://doc.qt.io/qt-5/qpushbutton.html
        self.ui.URLbutton.setText('送出')
        self.clicked_counter = 0
        self.ui.URLbutton.clicked.connect(self.buttonClicked)

    def buttonClicked(self):
        self.name=0
        self.content=0
        self.time=0
        self.limit_char = self.ui.lineEdit_2.text().strip()
        self.lottery_count = self.ui.lineEdit_3.text().strip()
        self.video_id_tmp = self.ui.lineEdit.text().strip() # strip是去掉左右的空白
        for i in range (33) : # 自動去除前面的網址 保留後面的 讓使用者直接貼網址就好不用去用v=後面的資料
            self.video_id = self.video_id_tmp[i:]
        if self.ui.CB_name.isChecked():
            self.name=1
        if self.ui.CB_content.isChecked():
            self.content=1
        if self.ui.CB_time.isChecked():
            self.time=1
        self.start_datetime=self.ui.dateEdit_1.dateTime()
        self.end_datetime=self.ui.dateEdit_2.dateTime()
        main()

def html_to_json(path):
    with request.urlopen(path) as response:
        return json.load(response)

def get_comments(video_id, page_token='', part='snippet', max_results=100): # 跑max_results的次數並且將資料存入list

   flag_count=0
   comments=[]
   youtube_furl="https://www.googleapis.com/youtube/v3/"
   my_key="AIzaSyAaEfqZf6_s5podhh4dGW2frLByNEEPzNk"
   path = youtube_furl+f'commentThreads?part={part}&videoId={video_id}&maxResults={max_results}&pageToken={page_token}&key='+my_key
   data=html_to_json(path)
   next_page_token = data.get('nextPageToken', '')

   for data_item in data['items']:
        data_item = data_item['snippet']
        top_comment = data_item['topLevelComment']
        flag_count+=1 # 拿來判斷第一筆資料是否是置頂留言用
        try:
            time_ = datetime.strptime(top_comment['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # 日期格式錯誤
            time_ = None
        if flag_count==1 and window.start_datetime > time_ : # 如果第一筆資料就超出最舊的時間範圍 執行下一次迴圈 避免碰到是置頂留言
            continue
        if window.start_datetime > time_ : # 離開迴圈的條件 超過最舊的時間範圍    資料由新到舊開始抓 進入區間開始記錄 超過區間就 break 
           return [comments, ''] 
        if window.start_datetime <= time_ <= window.end_datetime: # 資料進入區間範圍 開始記錄
            if window.limit_char != "" : # 判斷有無設定特定字串
                if window.limit_char not in top_comment['snippet']['textOriginal'] : # 想要查的字串沒有在留言內容的話 執行下一次迴圈 不紀錄
                    continue
            if 'authorChannelId' in top_comment['snippet']:
                ru_id = top_comment['snippet']['authorChannelId']['value'] # 取得回文者id
            else:
                ru_id = ''

            ru_name = top_comment['snippet'].get('authorDisplayName', '') # 取得回文者名稱
            if not ru_name:
                ru_name = ''

            comments.append({
                'reply_id': top_comment['id'],
                'ru_id': ru_id,
                'ru_name': ru_name,
                'reply_time': str(time_),
                'reply_content': top_comment['snippet']['textOriginal'],
                'rm_positive': int(top_comment['snippet']['likeCount']),
                'rn_comment': int(data_item['totalReplyCount'])
            })
            #print(comments)
   return comments, next_page_token

def main():
    have_error=0
    comments = []
    next_page_token=''
    all_comments=[] # 最後得出結果資料的list
    flag=0
    while next_page_token !='' or flag==0 : # 當token為空字串(代表無資料)時 就跳出迴圈
        try:
            [comments,next_page_token]=get_comments(window.video_id,next_page_token)
        except:
            window.ui.textEdit.setText("網址錯誤!!! 請確認網址")
            have_error=1 
        all_comments.extend(comments)   
        flag=1
    if have_error == 0 : # 如果沒有發生過錯誤 就清除畫面 避免使用者多按幾次跑出一堆append
        window.ui.textEdit.clear()
    if window.lottery_count !='': # 如果抽獎欄位有東西 就抽
        try:
            user=random.sample(all_comments,int(window.lottery_count))
        except:
            if window.ui.textEdit.toPlainText() =="網址錯誤!!! 請確認網址": # 避免被抽獎的錯誤字元蓋過網址錯誤
                pass
            else :
                window.ui.textEdit.setText("抽獎數量超過符合條件的留言數，或輸入了非法字元，請重新輸入")
            return
        if window.time==0 :
            if window.name==0 and window.content==0:
                window.ui.textEdit.setText("請點選上方的選項")
            if window.name==0 and window.content==1:
                for i in user:
                    window.ui.textEdit.append("留言內容:"+i["reply_content"]+"\n")
            if window.name==1 and window.content==0:
                for i in user:
                    window.ui.textEdit.append("留言者:"+i["ru_name"]+"\n")
            if window.name==1 and window.content==1:
                for i in user:
                    window.ui.textEdit.append("留言者:"+i["ru_name"])
                    window.ui.textEdit.append("留言內容:"+i["reply_content"]+"\n")
        if window.time==1 :
            if window.name==0 and window.content==0:
                for i in user:
                    window.ui.textEdit.append(i["reply_time"]+"\n")
            if window.name==0 and window.content==1:
                for i in user:
                    window.ui.textEdit.append(i["reply_time"])
                    window.ui.textEdit.append("留言內容:"+i["reply_content"]+"\n")
            if window.name==1 and window.content==0:
                    for i in user:
                        window.ui.textEdit.append(i["reply_time"])
                        window.ui.textEdit.append("留言者:"+i["ru_name"]+"\n")
            if window.name==1 and window.content==1:
                for i in user:
                    window.ui.textEdit.append(i["reply_time"])
                    window.ui.textEdit.append("留言者:"+i["ru_name"])
                    window.ui.textEdit.append("留言內容:"+i["reply_content"]+"\n")
        window.ui.total.setText("共有 "+str(len(user))+" 筆資料")
        
    else : # 沒有使用抽獎功能 就執行印出全部留言
        if window.time==0 :
            if window.name==0 and window.content==0:
                window.ui.textEdit.setText("請點選上方的選項")
            if window.name==0 and window.content==1:
                for i in all_comments:
                    window.ui.textEdit.append("留言內容:"+i["reply_content"]+"\n")
            if window.name==1 and window.content==0:
                for i in all_comments:
                    window.ui.textEdit.append("留言者:"+i["ru_name"]+"\n")
            if window.name==1 and window.content==1:
                for i in all_comments:
                    window.ui.textEdit.append("留言者:"+i["ru_name"])
                    window.ui.textEdit.append("留言內容:"+i["reply_content"]+"\n")
        if window.time==1 :
            if window.name==0 and window.content==0:
                for i in all_comments:
                    window.ui.textEdit.append(i["reply_time"]+"\n")
            if window.name==0 and window.content==1:
                for i in all_comments:
                    window.ui.textEdit.append(i["reply_time"])
                    window.ui.textEdit.append("留言內容:"+i["reply_content"]+"\n")
            if window.name==1 and window.content==0:
                    for i in all_comments:
                        window.ui.textEdit.append(i["reply_time"])
                        window.ui.textEdit.append("留言者:"+i["ru_name"]+"\n")
            if window.name==1 and window.content==1:
                for i in all_comments:
                    window.ui.textEdit.append(i["reply_time"])
                    window.ui.textEdit.append("留言者:"+i["ru_name"])
                    window.ui.textEdit.append("留言內容:"+i["reply_content"]+"\n")
        window.ui.total.setText("共有 "+str(len(all_comments))+" 筆資料")
    if all_comments==[] and window.ui.textEdit.toPlainText()=="":
        window.ui.textEdit.setText("查無資料")

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.show()
    sys.exit(app.exec_())
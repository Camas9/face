from PictureToolUI import Ui_MainWindow
from zichuangkou import Ui_zi
import os
import time
import cv2
import sys
import numpy as np
import pyttsx3
import MySQLdb
import time
from PIL import Image


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.EVENT()

    def EVENT(self):
        # 摄像头打开标志
        self.cap = 0
        self.flag = 0
        # 班级学生标签
        self.facelabel = ['1 ouxijie', '2 chenxuan', '3 chenliyi', '4 guohuhang', '5 guoyansheng', '6 huangjialin',
                          '7 huangzhaoqian',
                          '8 tangwenhao', '9 sunhongtao', '10 zhoushiyuan', '11 liuhaodian', '12 liuhao',
                          '13 zhengjiayi', '1 ouxijie',
                          '14 yangjinhao', '15 zhangxinglong', '1 ouxijie', '1 ouxijie', '1 ouxijie']
        # 画笔信息
        self.lines = []
        self.last_point = None
        # 将标签保存
        self.data_id = []
        # 人脸识别
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(r'C:\Users\Administrator\PycharmProjects\pythonProject2\trainer\train.yml')
        # 语音
        self.soud = pyttsx3.init()
        # 设置图片的默认路径为当前工作路径（项目的路径）
        self.defaultImFolder = os.getcwd()
        # 控件链接
        self.pushButton_Open.clicked.connect(self.OpenPictureDir)
        self.pushButton_Opencap.clicked.connect(self.Opencapture)
        self.pushButton_Closecap.clicked.connect(self.Colsecapture)
        self.pushButton_Signin.clicked.connect(self.Cutcapture)
        self.pushButton_Logs.clicked.connect(self.Logs)
        self.pushButton.clicked.connect(self.save)

    # 检测人脸
    def ReFileName(data_path):
        # 对目录下的文件进行遍历
        facesS = []
        ids = []
        imageP = []
        for file in os.listdir(data_path):
            result = os.path.join(data_path, file)
            imageP.append(result)
        face_detector = cv2.CascadeClassifier(
            r"C:\Users\Administrator\PycharmProjects\pythonProject2\venv\haarcascade_frontalface_default.xml")
        flag = 0
        id = 0
        for p in imageP:
            img = cv2.imread(p)
            PIL_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_np = np.array(PIL_img)
            faces = face_detector.detectMultiScale(img_np)
            if (flag) % 15 == 0:  # 每十五张为一个人
                id = id + 1
            flag = flag + 1
            for (x, y, w, h) in faces:
                facesS.append(img_np[y:y + h, x:x + w])
                ids.append(id)
        return facesS, ids

    # 释放鼠标
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.lines.append([self.last_point])

    # 移动鼠标
    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton:
            self.lines[-1].append(event.pos())
            self.update()

    # 点击鼠标画画
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0), 10, Qt.SolidLine))

        for line in self.lines:
            if len(line) > 1:
                for i in range(1, len(line)):
                    painter.drawLine(line[i - 1], line[i])

    #  导入数据
    def OpenPictureDir(self):
        selectimgFolder = QtWidgets.QFileDialog.getExistingDirectory(None, "selectfolder", self.defaultImFolder)
        if selectimgFolder != '':
            self.imgFolder = selectimgFolder
            self.imageNameList = os.listdir(self.imgFolder)
            if len(self.imageNameList) > 0:
                imgPath = os.path.join(self.imgFolder)

    # 打开摄像头
    def Opencapture(self):
        self.cap = cv2.VideoCapture(0)  # 打开摄像头
        self.cap.open(0, cv2.CAP_DSHOW)
        while True:
            if self.flag == 1:
                break
            else:
                flag, image = self.cap.read()
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                else:
                    image_show = cv2.resize(image, (640, 480))
                    image_show = cv2.cvtColor(image_show, cv2.COLOR_BGR2RGB)  # opencv读的通道是BGR,要转成RGB
                    image_show = cv2.flip(image_show, 1)
                    gray = cv2.cvtColor(image_show, cv2.COLOR_BGR2GRAY)  # 灰度化
                    face_detector = cv2.CascadeClassifier(
                        r"C:\Users\Administrator\PycharmProjects\pythonProject2\venv\haarcascade_frontalface_default.xml")
                    faces = face_detector.detectMultiScale(gray, 1.2, 5)
                    for (x, y, w, h) in faces:
                        cv2.rectangle(image_show, (x, y), (x + w, y + h), (0, 255, 0), thickness=4)
                        grade = self.recognizer.predict(gray[y:y + h, x:x + w])
                        if grade[1] <= 80:
                            label = self.facelabel[grade[0] - 1]
                            for (x, y, w, h) in faces:
                                cv2.putText(image_show, label, (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 128, 0), 2)

                        else:
                            for (x, y, w, h) in faces:
                                cv2.putText(image_show, "not in class", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1,
                                            (255, 128, 0), 2)
                    # 将获取到的摄像头图片在区域中显示
                    self.showImage = QtGui.QImage(image_show.data, image_show.shape[1], image_show.shape[0],
                                                  QtGui.QImage.Format_RGB888)
                    self.piximg = QtGui.QPixmap(self.showImage)
                    self.label_Cap.setPixmap(self.piximg)

    # 关闭摄像头
    def Colsecapture(self):
        if self.cap == 0:
            pass
        else:
            self.label_Cap.clear()  # 清除label组件上的图片
            self.cap.release()  # 释放摄像头
            self.cap = 0
            self.flag = 1

    # 注册
    def Cutcapture(self):
        name = self.lineEdit.text()  # 输入
        cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        cv2.imwrite(r'C:\Users\Administrator\Desktop\p\photo.jpg', frame)
        data_img = cv2.imread(r'C:\Users\Administrator\Desktop\p\photo.jpg')
        data_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        con = MySQLdb.connect(host='localhost', user='root', password='', db='facepro', charset='utf8')
        cur = con.cursor()
        sql = 'insert into data(student_name,student_time,student_face) values(%s,%s,%s)'
        data = (name, data_time, np.array(data_img))
        cur.execute(sql, data)
        con.commit()
        cur.close()

    # 考勤
    def push_button_click(self):
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        cv2.imwrite(r'C:\Users\Administrator\Desktop\p\photo.jpg', frame)
        img = cv2.imread(r'C:\Users\Administrator\Desktop\p\photo.jpg')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_detector = cv2.CascadeClassifier(
            r"C:\Users\Administrator\PycharmProjects\pythonProject2\venv\haarcascade_frontalface_default.xml")
        faces = face_detector.detectMultiScale(gray)
        label = []
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)
            grade = self.recognizer.predict(gray[y:y + h, x:x + w])
            if grade[1] <= 100:
                label = self.facelabel[grade[0] - 1]
                self.textEdit_2.setText(label)
                self.soud.say("签到成功,请在签名区域签名")
                self.soud.runAndWait()
            else:
                self.textEdit_2.setText("当前学生不在班级里")

    # 图片考勤
    def push_button_clickpp(self):
        # 导入图片
        img = cv2.imread(r'C:\Users\Administrator\Desktop\p\photo.jpg')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_detector = cv2.CascadeClassifier(
            r"C:\Users\Administrator\PycharmProjects\pythonProject2\venv\haarcascade_frontalface_default.xml")
        faces = face_detector.detectMultiScale(gray)
        label = []
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)
            grade = self.recognizer.predict(gray[y:y + h, x:x + w])
            if grade[1] <= 80:
                label = self.facelabel[grade[0] - 1]
                if grade[1] <= 80:
                    label = self.facelabel[grade[0] - 1]
                    self.textEdit_3.setText(label)
                    # 发出识别语音
                    self.soud.say("签到成功，请在签名区域签名")
                    self.soud.runAndWait()
                else:
                    self.textEdit_3.setText("当前学生不在班级里")

    # 记录
    def Logs(self):
        # 将摄像头结果导入
        data_img = cv2.imread(r'C:\Users\Administrator\Desktop\p\photo.jpg')
        data_sign = cv2.imread(r'C:\Users\Administrator\PycharmProjects\pythonProject2\data\video\text.jpg')
        data_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        gray = cv2.cvtColor(data_img, cv2.COLOR_BGR2GRAY)
        face_detector = cv2.CascadeClassifier(
            r"C:\Users\Administrator\PycharmProjects\pythonProject2\venv\haarcascade_frontalface_default.xml")
        faces = face_detector.detectMultiScale(gray)
        label = []
        for (x, y, w, h) in faces:
            cv2.rectangle(data_img, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)
            grade = self.recognizer.predict(gray[y:y + h, x:x + w])
            if grade[1] <= 80:
                label = self.facelabel[grade[0] - 1]
                self.data_id = label
                if grade[1] <= 80:
                    label = self.facelabel[grade[0] - 1]
                else:
                    self.textEdit_3.setText("当前学生不在班级里")
        con = MySQLdb.connect(host='localhost', user='root', password='', db='facepro', charset='utf8')
        # 创建游标
        cur = con.cursor()
        sql = 'insert into signin(student_name,student_time,student_face,student_sign) values(%s,%s,%s,%s)'
        data = (self.data_id, data_time, np.array(data_img), np.array(data_sign))
        # 执行数据库插入
        cur.execute(sql, data)
        # 提交
        con.commit()

        stu = 'select student_name from signin'
        # 获取结果
        cur.execute(stu)
        # 获取记录
        all = cur.fetchall()
        print("当前出勤名单为：")
        print(all)
        # 释放游标
        cur.close()

    def save(self):
        file_path = r'C:\Users\Administrator\PycharmProjects\pythonProject2\data\video\text.jpg'
        # 获取画布图像，并将其转换为 QImage 对象
        image = QImage(self.grab())
        # 将图像缩小到 8*8
        image = image.scaled(QSize(8, 8))
        # 将 QImage 对象转换为 QPixmap 对象
        pixmap = QPixmap.fromImage(image)
        # 将 QPixmap 对象保存到文件
        pixmap.save(file_path)


if __name__ == '__main__':
    # 实现可视化
    app = QtWidgets.QApplication(sys.argv)
    ui = MyWindow()
    # 将界面展示
    ui.show()
    sys.exit(app.exec_())

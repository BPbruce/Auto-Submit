import sys
import os
import json
import datetime
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QMessageBox, QComboBox
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QTimer
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ======= 参数设置 =======
USER_DATA_DIRS = {
    "电鸭社区": os.path.join(os.getcwd(), "eleduck_session"),
    "V2EX": os.path.join(os.getcwd(), "v2ex_session"),
    "登链": os.path.join(os.getcwd(), "denglian_session"),
}
LOGIN_URLS = {
    "电鸭社区": "https://eleduck.com/",
    "V2EX": "https://www.v2ex.com/",
    "登链": "https://learnblockchain.cn/",
}
V2EX_POST_URLS = {
    "jobs": "https://www.v2ex.com/write?node=jobs",
    "bitcoin": "https://www.v2ex.com/write?node=bitcoin",
    "crypto": "https://www.v2ex.com/write?node=crypto",
}
DENGLIAN_POST_URLS = {
    "后端岗位": "https://learnblockchain.cn/job/677",
    "AI岗位": None,
    "高级区块链岗位": "https://learnblockchain.cn/job/658",
}
ELEDUCK_POST_URL = "https://eleduck.com/jobs/new?c=jd"

# 登录状态持久化配置
LOGIN_STATUS_FILE = os.path.join(os.getcwd(), ".login_status.json")
LOGIN_EXPIRE_DAYS = 20
login_flags = {site: False for site in USER_DATA_DIRS}

def load_login_status():
    try:
        with open(LOGIN_STATUS_FILE, 'r') as f:
            data = json.load(f)
        now = datetime.datetime.now().timestamp()
        for site, ts in data.items():
            if site in login_flags and now - ts < LOGIN_EXPIRE_DAYS * 86400:
                login_flags[site] = True
    except Exception:
        pass

def save_login_status(site):
    data = {}
    if os.path.exists(LOGIN_STATUS_FILE):
        try:
            with open(LOGIN_STATUS_FILE, 'r') as f:
                data = json.load(f)
        except Exception:
            data = {}
    data[site] = datetime.datetime.now().timestamp()
    with open(LOGIN_STATUS_FILE, 'w') as f:
        json.dump(data, f)

load_login_status()

drivers = {}

def get_driver(site_name, headless=False):
    global drivers
    if site_name in drivers:
        try:
            _ = drivers[site_name].current_url
            return drivers[site_name]
        except Exception:
            try:
                drivers[site_name].quit()
            except Exception:
                pass
            del drivers[site_name]
    options = Options()
    options.add_argument(f"user-data-dir={USER_DATA_DIRS[site_name]}")
    options.add_argument("--new-window")
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    drivers[site_name] = driver
    return driver

# ---------- 电鸭 自动发帖 ----------
def click_span_by_text(driver, text):
    span = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//span[text()='{text}']"))
    )
    driver.execute_script("arguments[0].scrollIntoView();", span)
    span.click()

def auto_post_job(title, description):
    driver = get_driver("电鸭社区", headless=False)
    try:
        driver.get(ELEDUCK_POST_URL)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        click_span_by_text(driver, "全职坐班")
        click_span_by_text(driver, "广州")
        input_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='title']"))
        )
        input_title.clear(); input_title.send_keys(title)
        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[name='textarea']"))
        )
        driver.execute_script("arguments[0].value = ''", textarea)
        textarea.send_keys(description)
        for label in ["企业直招", "开发", "区块链&Web3", "AI/人工智能"]:
            click_span_by_text(driver, label)
    except Exception as e:
        print(f"电鸭发帖失败: {e}")

# ---------- 登录 ----------
def open_login(site_name):
    driver = get_driver(site_name, headless=False)
    try:
        driver.get(LOGIN_URLS[site_name])
        login_flags[site_name] = True
        save_login_status(site_name)
    except Exception as e:
        print(f"打开登录页失败: {e}")
    # 不退出驱动

# ---------- V2EX 自动填充 ----------
def open_v2ex(node, title, desc):
    driver = get_driver("V2EX", headless=False)
    try:
        driver.get(V2EX_POST_URLS[node])
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "topic_title")))
        tbox = driver.find_element(By.ID, "topic_title"); tbox.clear(); tbox.send_keys(title)
        driver.execute_script("document.querySelector('.CodeMirror').CodeMirror.setValue(arguments[0]);", desc)
    except Exception as e:
        print(f"V2EX 发帖失败: {e}")

# ---------- 登链 编辑并保存 (Headless) ----------
def open_denglian(role_name):
    url = DENGLIAN_POST_URLS.get(role_name)
    if not url:
        QMessageBox.information(None, "敬请期待", f"{role_name} 暂未开放发布入口，稍后补充。")
        return
    driver = get_driver("登链", headless=True)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        edit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.edit"))
        )
        edit_btn.click()
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit_btn"))
        )
        save_btn.click()
    except Exception as e:
        print(f"登链操作失败: {e}")

# ---------- PyQt UI ----------
class JobPostUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("比特鹰-渠道维护V1.0")
        self.resize(720, 660)
        self.init_ui()

    def init_ui(self):
        lay = QVBoxLayout(self)

        # 登录选择
        login_bar = QHBoxLayout()
        login_bar.addWidget(QLabel("🔐 平台登录："))
        self.login_select = QComboBox(); self.login_select.addItems(LOGIN_URLS.keys())
        login_bar.addWidget(self.login_select)
        login_btn = QPushButton("登录"); login_btn.clicked.connect(lambda: threading.Thread(target=open_login, args=(self.login_select.currentText(),)).start())
        login_bar.addWidget(login_btn); lay.addLayout(login_bar)

        # 标题输入
        lay.addWidget(QLabel("标题"))
        self.title_in = QLineEdit(); self.title_in.setPlaceholderText("请输入职位标题")
        lay.addWidget(self.title_in)

        # 正文输入
        lay.addWidget(QLabel("正文"))
        self.body_in = QTextEdit(); self.body_in.setPlaceholderText("请输入职位描述")
        lay.addWidget(self.body_in)

        # 电鸭
        row1 = QHBoxLayout(); row1.addWidget(QLabel("电鸭社区")); row1.addStretch()
        btn1 = QPushButton("维护"); btn1.clicked.connect(self.handle_eleduck); row1.addWidget(btn1); lay.addLayout(row1)

        # V2EX
        row2 = QHBoxLayout(); row2.addWidget(QLabel("V2EX")); row2.addStretch()
        self.v2ex_select = QComboBox(); self.v2ex_select.addItems(V2EX_POST_URLS.keys()); row2.addWidget(self.v2ex_select)
        btn2 = QPushButton("维护"); btn2.clicked.connect(self.handle_v2ex); row2.addWidget(btn2); lay.addLayout(row2)

        # 登链
        row3 = QHBoxLayout(); row3.addWidget(QLabel("登链")); row3.addStretch()
        self.dl_select = QComboBox(); self.dl_select.addItems(DENGLIAN_POST_URLS.keys()); row3.addWidget(self.dl_select)
        btn3 = QPushButton("维护"); btn3.clicked.connect(self.handle_denglian); row3.addWidget(btn3); lay.addLayout(row3)

        self.apply_dark()

    def apply_dark(self):
        pal = QPalette(); pal.setColor(QPalette.Window, QColor(30,30,30)); pal.setColor(QPalette.WindowText, QColor(255,215,0)); pal.setColor(QPalette.Base, QColor(45,45,45)); pal.setColor(QPalette.Text, QColor(255,255,255)); self.setPalette(pal)
        self.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: gold;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #222;
                padding-top: 8px;
                padding-left: 8px;
            }
            QLabel {
                color: gold;
                font-size: 15px;
            }
        """
        )

    def handle_eleduck(self):
        if not login_flags["电鸭社区"]:
            QMessageBox.warning(self, "未登录", "请先登录电鸭社区")
            return
        threading.Thread(target=auto_post_job, args=(self.title_in.text(), self.body_in.toPlainText())).start()

    def handle_v2ex(self):
        if not login_flags["V2EX"]:
            QMessageBox.warning(self, "未登录", "请先登录 V2EX")
            return
        threading.Thread(target=open_v2ex, args=(self.v2ex_select.currentText(), self.title_in.text(), self.body_in.toPlainText())).start()

    def handle_denglian(self):
        if not login_flags["登链"]:
            QMessageBox.warning(self, "未登录", "请先登录登链")
            return
        threading.Thread(target=open_denglian, args=(self.dl_select.currentText(),)).start()

# ---------- 清理驱动 ----------
def cleanup_drivers():
    for drv in list(drivers.values()):
        try:
            drv.quit()
        except:
            pass

# ---------- main ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JobPostUI(); window.show()
    app.aboutToQuit.connect(cleanup_drivers)
    sys.exit(app.exec_())

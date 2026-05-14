import sys
import os
import json
import datetime
import threading
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QMessageBox, QComboBox
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QTimer, Qt

# ========== 原功能部分 ==========
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class JobPostManager:
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
    LOGIN_STATUS_FILE = os.path.join(os.getcwd(), ".login_status.json")
    CHROME_DRIVER_PATH = ChromeDriverManager().install()
    LOGIN_EXPIRE_DAYS = 20
    DRAFT_FILE = Path(os.getcwd()) / ".job_draft.json"
    login_flags = {site: False for site in USER_DATA_DIRS}
    drivers = {}

    def __init__(self):
        self.load_login_status()

    def load_login_status(self):
        if not os.path.exists(self.LOGIN_STATUS_FILE):
            return
        try:
            with open(self.LOGIN_STATUS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            now = datetime.datetime.now().timestamp()
            for site, ts in data.items():
                if site in self.login_flags and now - ts < self.LOGIN_EXPIRE_DAYS * 86400:
                    self.login_flags[site] = True
        except Exception as e:
            print(f"加载登录状态失败: {e}")

    def save_login_status(self, site):
        data = {}
        if os.path.exists(self.LOGIN_STATUS_FILE):
            try:
                with open(self.LOGIN_STATUS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"读取登录状态文件失败: {e}")
        data[site] = datetime.datetime.now().timestamp()
        with open(self.LOGIN_STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def get_driver(self, site_name, headless=False):
        if site_name in self.drivers:
            try:
                _ = self.drivers[site_name].current_url
                return self.drivers[site_name]
            except Exception as e:
                print(f"获取现有驱动程序失败: {e}")
                try:
                    self.drivers[site_name].quit()
                except Exception as e:
                    print(f"关闭驱动程序失败: {e}")
                del self.drivers[site_name]

        Path(self.USER_DATA_DIRS[site_name]).mkdir(parents=True, exist_ok=True)
        options = Options()
        options.add_argument(f"user-data-dir={self.USER_DATA_DIRS[site_name]}")
        options.add_argument("--new-window")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--allow-insecure-localhost")
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(service=Service(self.CHROME_DRIVER_PATH), options=options)
        self.drivers[site_name] = driver
        return driver

    def click_span_by_text(self, driver, text):
        span = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[text()='{text}']"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", span)
        span.click()

    def auto_post_job(self, title, description):
        driver = self.get_driver("电鸭社区", headless=False)
        try:
            driver.get(self.ELEDUCK_POST_URL)
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            self.click_span_by_text(driver, "全职坐班")
            self.click_span_by_text(driver, "广州")
            input_title = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='title']"))
            )
            input_title.clear()
            input_title.send_keys(title)
            textarea = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[name='textarea']"))
            )
            driver.execute_script("arguments[0].value = ''", textarea)
            textarea.send_keys(description)
            for label in ["企业直招", "开发", "区块链&Web3", "AI/人工智能"]:
                self.click_span_by_text(driver, label)
        except Exception as e:
            print(f"电鸭发帖失败: {e}")

    def open_login(self, site_name):
        driver = self.get_driver(site_name, headless=False)
        try:
            driver.get(self.LOGIN_URLS[site_name])
            self.login_flags[site_name] = True
            self.save_login_status(site_name)
        except Exception as e:
            print(f"打开登录页失败: {e}")

    def open_v2ex(self, node, title, desc):
        driver = self.get_driver("V2EX", headless=False)
        try:
            driver.get(self.V2EX_POST_URLS[node])
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "topic_title")))
            tbox = driver.find_element(By.ID, "topic_title")
            tbox.clear()
            tbox.send_keys(title)
            driver.execute_script("document.querySelector('.CodeMirror').CodeMirror.setValue(arguments[0]);", desc)
        except Exception as e:
            print(f"V2EX 发帖失败: {e}")

    def open_denglian(self, role_name):
        url = self.DENGLIAN_POST_URLS.get(role_name)
        if not url:
            QMessageBox.information(None, "敬请期待", f"{role_name} 暂未开放发布入口，稍后补充。")
            return
        driver = self.get_driver("登链", headless=False)
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            edit_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.edit")))
            edit_btn.click()
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            save_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit_btn")))
            save_btn.click()
        except Exception as e:
            print(f"登链操作失败: {e}")

    def save_draft(self, title, body):
        payload = {
            "title": title,
            "body": body,
            "updated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        with open(self.DRAFT_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def load_draft(self):
        if not self.DRAFT_FILE.exists():
            return None
        with open(self.DRAFT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def cleanup_drivers(self):
        for drv in list(self.drivers.values()):
            try:
                drv.quit()
            except Exception as e:
                print(f"清理驱动程序失败: {e}")

class JobPostUI(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("比特鹰-渠道维护V1.0")
        self.resize(720, 660)
        self.init_ui()

    def init_ui(self):
        lay = QVBoxLayout(self)

        # 登录选择
        login_bar = QHBoxLayout()
        login_bar.addWidget(QLabel("🔐 平台登录："))
        self.login_select = QComboBox()
        self.login_select.addItems(self.manager.LOGIN_URLS.keys())
        login_bar.addWidget(self.login_select)

        login_btn = QPushButton("登录")
        login_btn.clicked.connect(lambda: threading.Thread(target=self.manager.open_login, args=(self.login_select.currentText(),), daemon=True).start())
        login_bar.addWidget(login_btn)
        lay.addLayout(login_bar)

        # 标题输入
        lay.addWidget(QLabel("标题"))
        self.title_in = QLineEdit()
        self.title_in.setPlaceholderText("请输入职位标题")
        lay.addWidget(self.title_in)

        # 正文输入
        lay.addWidget(QLabel("正文"))
        self.body_in = QTextEdit()
        self.body_in.setPlaceholderText("请输入职位描述")
        lay.addWidget(self.body_in)

        draft_row = QHBoxLayout()
        save_draft_btn = QPushButton("保存草稿")
        save_draft_btn.clicked.connect(self.handle_save_draft)
        draft_row.addWidget(save_draft_btn)

        load_draft_btn = QPushButton("读取草稿")
        load_draft_btn.clicked.connect(self.handle_load_draft)
        draft_row.addWidget(load_draft_btn)

        clear_btn = QPushButton("清空内容")
        clear_btn.clicked.connect(self.handle_clear_fields)
        draft_row.addWidget(clear_btn)
        draft_row.addStretch()
        lay.addLayout(draft_row)

        # 电鸭
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("电鸭社区"))
        row1.addStretch()
        btn1 = QPushButton("维护")
        btn1.clicked.connect(self.handle_eleduck)
        row1.addWidget(btn1)
        lay.addLayout(row1)

        # V2EX
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("V2EX"))
        row2.addStretch()
        self.v2ex_select = QComboBox()
        self.v2ex_select.addItems(self.manager.V2EX_POST_URLS.keys())
        row2.addWidget(self.v2ex_select)
        btn2 = QPushButton("维护")
        btn2.clicked.connect(self.handle_v2ex)
        row2.addWidget(btn2)
        lay.addLayout(row2)

        # 登链
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("登链"))
        row3.addStretch()
        self.dl_select = QComboBox()
        self.dl_select.addItems(self.manager.DENGLIAN_POST_URLS.keys())
        row3.addWidget(self.dl_select)
        btn3 = QPushButton("维护")
        btn3.clicked.connect(self.handle_denglian)
        row3.addWidget(btn3)
        lay.addLayout(row3)

        # 替代原暗色风格，应用现代玻璃 UI
        self.apply_modern_glass_style()

    def apply_modern_glass_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: 'Segoe UI', 'MiSans', 'SF Pro Display';
                font-size: 14px;
            }
            QLabel {
                color: #333;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton {
                background-color: #FF6700;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #ff8533;
            }
            QPushButton:pressed {
                background-color: #cc5500;
                padding-top: 9px;
                padding-left: 9px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 6px;
            }
            QTextEdit {
                padding: 8px;
            }
            QComboBox {
                padding-left: 6px;
            }
        """)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(255, 255, 255, 245))
        pal.setColor(QPalette.Base, QColor(255, 255, 255, 240))
        pal.setColor(QPalette.Text, QColor(51, 51, 51))
        pal.setColor(QPalette.Button, QColor(255, 103, 0))
        pal.setColor(QPalette.ButtonText, Qt.white)
        self.setPalette(pal)

    def handle_save_draft(self):
        title = self.title_in.text().strip()
        body = self.body_in.toPlainText().strip()
        if not title and not body:
            QMessageBox.information(self, "提示", "标题和正文都为空，未保存。")
            return
        try:
            self.manager.save_draft(title, body)
            QMessageBox.information(self, "已保存", "草稿保存成功。")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存草稿失败：{e}")

    def handle_load_draft(self):
        try:
            draft = self.manager.load_draft()
        except Exception as e:
            QMessageBox.critical(self, "读取失败", f"读取草稿失败：{e}")
            return

        if not draft:
            QMessageBox.information(self, "无草稿", "尚未找到已保存的草稿。")
            return

        self.title_in.setText(draft.get("title", ""))
        self.body_in.setPlainText(draft.get("body", ""))
        updated_at = draft.get("updated_at", "未知时间")
        QMessageBox.information(self, "已读取", f"草稿读取成功（更新时间：{updated_at}）。")

    def handle_clear_fields(self):
        self.title_in.clear()
        self.body_in.clear()

    def handle_eleduck(self):
        if not self.manager.login_flags["电鸭社区"]:
            QMessageBox.warning(self, "未登录", "请先登录电鸭社区")
            return
        threading.Thread(target=self.manager.auto_post_job, args=(self.title_in.text(), self.body_in.toPlainText()), daemon=True).start()

    def handle_v2ex(self):
        if not self.manager.login_flags["V2EX"]:
            QMessageBox.warning(self, "未登录", "请先登录 V2EX")
            return
        threading.Thread(target=self.manager.open_v2ex, args=(self.v2ex_select.currentText(), self.title_in.text(), self.body_in.toPlainText()), daemon=True).start()

    def handle_denglian(self):
        if not self.manager.login_flags["登链"]:
            QMessageBox.warning(self, "未登录", "请先登录登链")
            return
        threading.Thread(target=self.manager.open_denglian, args=(self.dl_select.currentText(),), daemon=True).start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = JobPostManager()
    window = JobPostUI(manager)
    window.show()
    app.aboutToQuit.connect(manager.cleanup_drivers)
    sys.exit(app.exec_())
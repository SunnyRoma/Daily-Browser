import sys
import os
import json
import shutil
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, 
    QHBoxLayout, QDialog, QLineEdit, QLabel, QDialogButtonBox, QListWidget, 
    QMessageBox, QToolBar, QMenu, QFileDialog, QProgressBar, QShortcut, QListWidgetItem,
    QInputDialog, QAction, QWidgetAction, QSplashScreen
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, Qt, QSize, QTimer, QEvent, QObject, QPropertyAnimation, QRect
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QPainter, QLinearGradient, QColor, QFont
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

HISTORY_FILE = "settings/history.json"
PROFILES_DIR = "profiles"
INCOGNITO_ICON = "assets/incognito.svg"  # добавьте подходящую иконку в проект

# === Локализация ===
LANGS = {
    'ru': {
        'save_tabs': 'Сохранить вкладки?',
        'save_tabs_text': 'Сохранить все открытые вкладки перед выходом?',
        'restore_tabs': 'Восстановить вкладки?',
        'restore_tabs_text': 'Обнаружены сохранённые вкладки. Восстановить их?',
        'add_profile': 'Добавить профиль',
        'delete_profile': 'Удалить профиль',
        'new_incognito_tab': 'Новая инкогнито-вкладка',
        'new_incognito_window': 'Новое окно инкогнито',
        'language': 'Язык',
        'russian': 'Русский',
        'english': 'Английский',
        'manage_bookmarks': 'Управление закладками',
        'add_bookmark': 'Добавить закладку',
        'add_link_title': 'Добавить ссылку',
        'name_label': 'Название:',
        'url_label': 'URL:',
        'ok': 'OK',
        'cancel': 'Cancel',
        'manage_links_title': 'Управление ссылками',
        'name_placeholder': 'Название',
        'url_placeholder': 'URL',
        'add': 'Добавить',
        'delete': 'Удалить',
        'yes': 'Да',
        'no': 'Нет',
        'clear_history_confirm': 'Удалить всю историю?',
        'history_title': 'История посещений',
        'search_history_placeholder': 'Поиск по истории…',
        'delete_selected': 'Удалить выбранное',
        'clear_history': 'Очистить историю',
    },
    'en': {
        'save_tabs': 'Save tabs?',
        'save_tabs_text': 'Save all open tabs before exit?',
        'restore_tabs': 'Restore tabs?',
        'restore_tabs_text': 'Saved tabs found. Restore them?',
        'add_profile': 'Add profile',
        'delete_profile': 'Delete profile',
        'new_incognito_tab': 'New incognito tab',
        'new_incognito_window': 'New incognito window',
        'language': 'Language',
        'russian': 'Russian',
        'english': 'English',
        'manage_bookmarks': 'Manage bookmarks',
        'add_bookmark': 'Add bookmark',
        'add_link_title': 'Add link',
        'name_label': 'Name:',
        'url_label': 'URL:',
        'ok': 'OK',
        'cancel': 'Cancel',
        'manage_links_title': 'Manage links',
        'name_placeholder': 'Name',
        'url_placeholder': 'URL',
        'add': 'Add',
        'delete': 'Delete',
        'yes': 'Yes',
        'no': 'No',
        'clear_history_confirm': 'Delete all history?',
        'history_title': 'History',
        'search_history_placeholder': 'Search history…',
        'delete_selected': 'Delete selected',
        'clear_history': 'Clear history',
    }
}
current_lang = 'ru'

def _t(key):
    return LANGS[current_lang].get(key, key)

STARTPAGE_LANGS = {
    'ru': {
        'title': 'Daily Browser Start',
        'search_placeholder': 'Поиск в Google...',
        'search_button': 'Найти',
        'add_shortcut': 'Добавить ярлык',
        'browser_name': 'Daily Browser',
    },
    'en': {
        'title': 'Daily Browser Start',
        'search_placeholder': 'Search in Google...',
        'search_button': 'Search',
        'add_shortcut': 'Add shortcut',
        'browser_name': 'Daily Browser',
    }
}

def generate_startpage(lang=None):
    if lang is None:
        lang = current_lang
    t = STARTPAGE_LANGS.get(lang, STARTPAGE_LANGS['en'])
    try:
        with open("settings/quicklinks.json", "r", encoding="utf-8") as f:
            links = json.load(f)
    except FileNotFoundError:
        links = []
        with open("settings/quicklinks.json", "w", encoding="utf-8") as f:
            json.dump(links, f, ensure_ascii=False, indent=4)

    html = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <title>{t['title']}</title>
    <style>
        body {{
            background: linear-gradient(135deg, #a8e063 0%, #43a047 100%);
            color: #222;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }}
        .logo {{
            font-size: 48px;
            color: #43a047;
            font-weight: bold;
            margin-bottom: 30px;
            text-shadow: 1px 1px 8px #a8e06388;
        }}
        .search-box {{
            display: flex;
            width: 400px;
            margin-bottom: 30px;
        }}
        .search-box input {{
            flex: 1;
            padding: 12px;
            font-size: 18px;
            border: 2px solid #43a047;
            border-radius: 25px 0 0 25px;
            outline: none;
            background: #a8e063;
            color: #222;
        }}
        .search-box button {{
            padding: 12px 24px;
            font-size: 18px;
            background: #43a047;
            color: #fff;
            border: none;
            border-radius: 0 25px 25px 0;
            cursor: pointer;
        }}
        .quick-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: center;
            max-width: 800px;
        }}
        .quick-link {{
            width: 100px;
            height: 100px;
            background: #43a047;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: #fff;
            font-size: 22px;
            font-weight: bold;
            transition: background 0.2s, color 0.2s;
            box-shadow: 0 2px 8px #0002;
            text-align: center;
        }}
        .quick-link:hover {{
            background: #a8e063;
            color: #222;
        }}
        .add-shortcut {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-decoration: none;
            color: #222;
            font-size: 16px;
            margin-top: 5px;
        }}
        .add-shortcut-btn {{
            width: 56px;
            height: 56px;
            background: #006064;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            color: #fff;
            border: none;
            margin-bottom: 5px;
            box-shadow: 0 2px 8px #0002;
            transition: background 0.2s;
            cursor: pointer;
        }}
        .add-shortcut-btn:hover {{
            background: #00838f;
        }}
        .add-shortcut-label {{
            color: #fff;
            font-size: 14px;
            text-shadow: 0 1px 4px #0005;
        }}
    </style>
</head>
<body>
    <div class="logo">{t['browser_name']}</div>
    <form class="search-box" action="https://www.google.com/search" method="get" target="_self">
        <input type="text" name="q" placeholder="{t['search_placeholder']}" autofocus>
        <button type="submit">{t['search_button']}</button>
    </form>
    <div class="quick-links">
        <a href="addshortcut://" class="add-shortcut">
            <div class="add-shortcut-btn">+</div>
            <div class="add-shortcut-label">{t['add_shortcut']}</div>
        </a>
'''
    for idx, link in enumerate(links):
        html += f'''        <a href="{link["url"]}" target="_self" class="quick-link">{link["name"]}</a>\n'''
    html += '''    </div>
</body>
</html>'''
    with open("assets/startpage/startpage.html", "w", encoding="utf-8") as f:
        f.write(html)

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None, add_shortcut_callback=None):
        super().__init__(parent)
        self.add_shortcut_callback = add_shortcut_callback

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.scheme() == "addshortcut":
            if self.add_shortcut_callback:
                self.add_shortcut_callback()
            return False  # Не переходить по ссылке
        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def createStandardContextMenu(self):
        menu = super().createStandardContextMenu()
        # Добавляем пункт PiP только если это YouTube
        url = self.url().toString()
        if "youtube.com" in url:
            pip_action = menu.addAction("Картинка в картинке (PiP)")
            pip_action.triggered.connect(self.trigger_pip)
        return menu

    def trigger_pip(self):
        # Выполнить JS для включения PiP на первом видео
        js = '''
            (function() {
                var v = document.querySelector('video');
                if (v) {
                    if (document.pictureInPictureElement) {
                        document.exitPictureInPicture();
                    } else {
                        v.requestPictureInPicture();
                    }
                } else {
                    alert('Видео не найдено!');
                }
            })();
        '''
        self.runJavaScript(js)

    def event(self, event):
        if event.type() == QEvent.KeyPress:
            if event.modifiers() & Qt.ControlModifier and event.key() in (Qt.Key_Equal, Qt.Key_Plus):
                # Только если YouTube
                if "youtube.com" in self.url().toString():
                    self.trigger_pip()
                    return True
        return super().event(event)

class PiPEventFilter(QObject):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.modifiers() & Qt.ControlModifier and event.key() in (Qt.Key_Equal, Qt.Key_Plus):
                url = self.browser.url().toString()
                if "youtube.com" in url:
                    self.browser.page().trigger_pip()
                    return True
        return False

class CustomWebEngineView(QWebEngineView):
    def contextMenuEvent(self, event):
        menu = self.page().createStandardContextMenu()
        menu.exec_(event.globalPos())

class BrowserTab(QWidget):
    youtube_tip_shown = False  # Класс-переменная, чтобы показывать подсказку только один раз за сессию
    def __init__(self, url=None, add_shortcut_callback=None, incognito=False, main_window=None):
        super().__init__()
        self.incognito = incognito
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем тулбар с адресной строкой
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: #43a047;
                border: none;
                padding: 5px;
            }
            QLineEdit {
                background: #a8e063;
                border: 2px solid #43a047;
                border-radius: 15px;
                padding: 5px 15px;
                color: #222;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #a8e063;
            }
        """)
        
        # Кнопки навигации
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("assets/left.svg"))
        back_btn.setIconSize(QSize(24, 24))
        back_btn.setToolTip("Назад")
        forward_btn = QPushButton()
        forward_btn.setIcon(QIcon("assets/right.svg"))
        forward_btn.setIconSize(QSize(24, 24))
        forward_btn.setToolTip("Вперед")
        refresh_btn = QPushButton()
        refresh_btn.setIcon(QIcon("assets/refresh.svg"))
        refresh_btn.setIconSize(QSize(24, 24))
        refresh_btn.setToolTip("Обновить")
        
        for btn in [back_btn, forward_btn, refresh_btn]:
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background: #a8e063;
                    border: none;
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background: #8bc34a;
                }
                QPushButton:pressed {
                    background: #7cb342;
                }
            """)
        
        # Адресная строка
        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background: #a8e063;
                border: 2px solid #43a047;
                border-radius: 15px;
                padding: 5px 15px;
                color: #222;
                font-size: 14px;
                height: 30px;
            }
            QLineEdit:focus {
                border-color: #a8e063;
            }
        """)
        
        # Добавляем виджеты в тулбар
        toolbar.addWidget(back_btn)
        toolbar.addWidget(forward_btn)
        toolbar.addWidget(refresh_btn)
        toolbar.addWidget(self.url_bar)
        
        # Создаем профиль
        if self.incognito:
            profile = QWebEngineProfile()
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        else:
            profile = QWebEngineProfile.defaultProfile()
            profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
            profile.setPersistentStoragePath(os.path.abspath(self.main_window.COOKIES_DIR))
        
        # Создаем страницу с нашим профилем
        page = CustomWebEnginePage(self, add_shortcut_callback=add_shortcut_callback)
        
        self.browser = CustomWebEngineView()
        self.browser.setPage(page)
        self.browser.setStyleSheet("""
            QWebEngineView {
                background: transparent;
                border: none;
            }
        """)
        
        # Подключаем сигналы
        back_btn.clicked.connect(self.browser.back)
        forward_btn.clicked.connect(self.browser.forward)
        refresh_btn.clicked.connect(self.browser.reload)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.browser.urlChanged.connect(self.update_url)
        self.browser.titleChanged.connect(self.update_tab_title)
        self.browser.iconChanged.connect(self.update_tab_icon)
        
        if url is None:
            startpage_path = os.path.abspath("assets/startpage/startpage.html")
            self.browser.setUrl(QUrl.fromLocalFile(startpage_path))
        else:
            self.browser.setUrl(QUrl(url))
            
        layout.addWidget(toolbar)
        layout.addWidget(self.browser)

        # Панель загрузок
        self.download_bar = QWidget()
        self.download_bar.hide()
        self.download_layout = QHBoxLayout()
        self.download_bar.setLayout(self.download_layout)
        self.progress = QProgressBar()
        self.label = QLabel()
        self.open_btn = QPushButton("Открыть")
        self.open_btn.hide()
        self.open_btn.clicked.connect(self.open_downloaded_file)
        self.download_layout.addWidget(self.label)
        self.download_layout.addWidget(self.progress)
        self.download_layout.addWidget(self.open_btn)
        layout.addWidget(self.download_bar)

        profile.downloadRequested.connect(self.handle_download)
        
        self.pip_filter = PiPEventFilter(self.browser)
        self.browser.installEventFilter(self.pip_filter)
        
        # Глобальный шорткат для PiP
        self.pip_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.pip_shortcut.activated.connect(self.try_pip)
        
        self.setLayout(layout)
        self.tab_widget = None  # будет установлен при добавлении во вкладки
    
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.browser.setUrl(QUrl(url))
    
    def update_url(self, url):
        # Показывать пустую строку вместо пути к startpage.html
        startpage_path = os.path.abspath("assets/startpage/startpage.html")
        startpage_url = QUrl.fromLocalFile(startpage_path).toString()
        if url.toString() == startpage_url:
            self.url_bar.setText("")
        else:
            self.url_bar.setText(url.toString())

    def handle_download(self, download: QWebEngineDownloadItem):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", download.path())
        if path:
            download.setPath(path)
            download.accept()
            self.download_bar.show()
            self.label.setText(os.path.basename(path))
            self.progress.setValue(0)
            self.open_btn.hide()
            download.downloadProgress.connect(self.update_download_progress)
            download.finished.connect(lambda: self.download_finished(download))
        else:
            download.cancel()

    def update_download_progress(self, received, total):
        if total > 0:
            self.progress.setValue(int(received * 100 / total))

    def download_finished(self, download):
        self.progress.setValue(100)
        self.open_btn.show()
        self.downloaded_path = download.path()
        # Скрыть панель через 10 секунд
        QTimer.singleShot(10000, self.download_bar.hide)

    def open_downloaded_file(self):
        os.startfile(self.downloaded_path)

    def try_pip(self):
        url = self.browser.url().toString()
        if "youtube.com" in url:
            self.browser.page().trigger_pip()

    def update_tab_title(self, title):
        if self.tab_widget is not None:
            index = self.tab_widget.indexOf(self)
            if index != -1:
                if self.incognito:
                    self.tab_widget.setTabText(index, f"🕵️ {title}")
                    self.tab_widget.setTabIcon(index, QIcon(INCOGNITO_ICON))
                else:
                    self.tab_widget.setTabText(index, title)
        # В инкогнито-режиме не сохраняем историю
        if not self.incognito and self.main_window and self.main_window.HISTORY_FILE:
            url = self.browser.url().toString()
            add_to_history(title, url, self.main_window.HISTORY_FILE)

    def update_tab_icon(self, icon):
        if self.tab_widget is not None:
            index = self.tab_widget.indexOf(self)
            if index != -1:
                self.tab_widget.setTabIcon(index, icon)

class AddLinkDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_t('add_link_title'))
        self.setMinimumWidth(340)
        self.setMinimumHeight(200)
        self.setWindowIcon(QIcon("assets/logotip.png"))
        self.setStyleSheet('''
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a8e063, stop:1 #43a047);
                border-radius: 18px;
            }
            QLabel {
                color: #222;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            QLineEdit {
                background: #e8f5e9;
                border: 2px solid #43a047;
                border-radius: 12px;
                padding: 8px 14px;
                font-size: 16px;
                color: #222;
                margin-bottom: 18px;
            }
            QPushButton {
                background: #43a047;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 22px;
                margin: 0 8px;
            }
            QPushButton:hover {
                background: #a8e063;
                color: #222;
            }
        ''')
        layout = QVBoxLayout(self)
        label1 = QLabel(_t('name_label'))
        self.name_input = QLineEdit()
        label2 = QLabel(_t('url_label'))
        self.url_input = QLineEdit()
        btns = QHBoxLayout()
        ok_btn = QPushButton(_t('ok'))
        cancel_btn = QPushButton(_t('cancel'))
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addWidget(label1)
        layout.addWidget(self.name_input)
        layout.addWidget(label2)
        layout.addWidget(self.url_input)
        layout.addLayout(btns)
    def get_data(self):
        return self.name_input.text().strip(), self.url_input.text().strip()

class ManageLinksDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_t('manage_links_title'))
        self.setWindowIcon(QIcon("assets/logotip.png"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setStyleSheet('''
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a8e063, stop:1 #43a047);
                border-radius: 18px;
            }
            QLineEdit {
                background: #e8f5e9;
                border: 2px solid #43a047;
                border-radius: 12px;
                padding: 8px 14px;
                font-size: 16px;
                color: #222;
                margin-bottom: 0px;
            }
            QPushButton {
                background: #43a047;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 22px;
                margin: 0 8px;
            }
            QPushButton:hover {
                background: #a8e063;
                color: #222;
            }
            QListWidget {
                background: #e8f5e9;
                border-radius: 12px;
                font-size: 16px;
                padding: 8px;
                margin-top: 8px;
            }
            QListWidget::item {
                padding: 10px 0;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background: #a8e063;
                color: #222;
            }
        ''')
        layout = QVBoxLayout()
        add_form = QWidget()
        add_form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(_t('name_placeholder'))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(_t('url_placeholder'))
        add_btn = QPushButton(_t('add'))
        add_btn.clicked.connect(self.add_link)
        add_form_layout.addWidget(self.name_input)
        add_form_layout.addWidget(self.url_input)
        add_form_layout.addWidget(add_btn)
        add_form.setLayout(add_form_layout)
        self.list_widget = QListWidget()
        try:
            with open("settings/quicklinks.json", "r", encoding="utf-8") as f:
                self.links = json.load(f)
                for link in self.links:
                    self.list_widget.addItem(f"{link['name']} - {link['url']}")
        except FileNotFoundError:
            self.links = []
        buttons_layout = QHBoxLayout()
        delete_btn = QPushButton(_t('delete'))
        delete_btn.clicked.connect(self.delete_selected)
        buttons_layout.addWidget(delete_btn)
        layout.addWidget(add_form)
        layout.addWidget(self.list_widget)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    def add_link(self):
        name = self.name_input.text()
        url = self.url_input.text()
        if name and url:
            if any(link['name'] == name or link['url'] == url for link in self.links):
                QMessageBox.warning(self, "Ошибка", "Такой ярлык уже существует!")
                return
            self.links.append({"name": name, "url": url})
            self.list_widget.addItem(f"{name} - {url}")
            self.name_input.clear()
            self.url_input.clear()
            with open("settings/quicklinks.json", "w", encoding="utf-8") as f:
                json.dump(self.links, f, ensure_ascii=False, indent=4)
            generate_startpage()
    def delete_selected(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, 'Подтверждение', 
                                       'Вы уверены, что хотите удалить эту ссылку?',
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.links.pop(current_row)
                self.list_widget.takeItem(current_row)
                with open("settings/quicklinks.json", "w", encoding="utf-8") as f:
                    json.dump(self.links, f, ensure_ascii=False, indent=4)
                generate_startpage()

class HistoryPage(QDialog):
    def __init__(self, history_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_t('history_title'))
        self.setWindowIcon(QIcon("assets/logotip.png"))
        self.resize(700, 500)
        self.history_file = history_file
        self.setStyleSheet('''
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a8e063, stop:1 #43a047);
                border-radius: 18px;
            }
            QLineEdit {
                background: #e8f5e9;
                border: 2px solid #43a047;
                border-radius: 12px;
                padding: 8px 14px;
                font-size: 16px;
                color: #222;
                margin-bottom: 0px;
            }
            QPushButton {
                background: #43a047;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 22px;
                margin: 0 8px;
            }
            QPushButton:hover {
                background: #a8e063;
                color: #222;
            }
            QListWidget {
                background: #e8f5e9;
                border-radius: 12px;
                font-size: 16px;
                padding: 8px;
                margin-top: 8px;
            }
            QListWidget::item {
                padding: 10px 0;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background: #a8e063;
                color: #222;
            }
        ''')
        layout = QVBoxLayout(self)
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(_t('search_history_placeholder'))
        self.search_edit.textChanged.connect(self.filter_history)
        search_layout.addWidget(self.search_edit)
        self.delete_btn = QPushButton(_t('delete_selected'))
        self.delete_btn.clicked.connect(self.delete_selected)
        self.clear_btn = QPushButton(_t('clear_history'))
        self.clear_btn.clicked.connect(self.clear_history)
        search_layout.addWidget(self.delete_btn)
        search_layout.addWidget(self.clear_btn)
        layout.addLayout(search_layout)
        self.list = QListWidget()
        layout.addWidget(self.list)
        self.load_history()
        self.list.itemDoubleClicked.connect(self.open_url)

    def update_texts(self):
        self.setWindowTitle(_t('history_title'))
        self.search_edit.setPlaceholderText(_t('search_history_placeholder'))
        self.delete_btn.setText(_t('delete_selected'))
        self.clear_btn.setText(_t('clear_history'))

    def load_history(self):
        self.list.clear()
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        except Exception:
            self.history = []
        for title, url in reversed(self.history):
            item = QListWidgetItem(f"{title}\n{url}")
            item.setData(1000, url)
            self.list.addItem(item)

    def filter_history(self):
        text = self.search_edit.text().lower()
        self.list.clear()
        for title, url in reversed(self.history):
            if text in title.lower() or text in url.lower():
                item = QListWidgetItem(f"{title}\n{url}")
                item.setData(1000, url)
                self.list.addItem(item)

    def delete_selected(self):
        selected = self.list.selectedItems()
        if not selected:
            return
        urls_to_delete = [item.data(1000) for item in selected]
        self.history = [rec for rec in self.history if rec[1] not in urls_to_delete]
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        self.filter_history()

    def clear_history(self):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle(_t('clear_history'))
        box.setText(_t('clear_history_confirm'))
        yes_btn = box.addButton(_t('yes'), QMessageBox.YesRole)
        no_btn = box.addButton(_t('no'), QMessageBox.NoRole)
        box.setDefaultButton(yes_btn)
        box.exec_()
        if box.clickedButton() == yes_btn:
            self.history = []
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            self.filter_history()

    def open_url(self, item):
        url = item.data(1000)
        self.accept()
        self.parent().open_url_in_new_tab(url)

def add_to_history(title, url, history_file):
    if not url or url.startswith("file://"):
        return
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        history = []
    # Удаляем все старые записи с этим url
    history = [rec for rec in history if rec[1] != url]
    history.append([title, url])
    history = history[-500:]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_profiles_dir():
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)
    return PROFILES_DIR

def get_profile_path(profile_name):
    return os.path.join(get_profiles_dir(), profile_name)

def get_profile_list():
    return [d for d in os.listdir(get_profiles_dir()) if os.path.isdir(os.path.join(get_profiles_dir(), d))]

class ProfileManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор профиля")
        self.setMinimumWidth(400)
        self.setMinimumHeight(420)
        self.setWindowIcon(QIcon("assets/logotip.png"))
        self.setStyleSheet('''
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a8e063, stop:1 #43a047);
                border-radius: 18px;
            }
            QLabel#LogoLabel {
                color: #43a047;
                font-size: 38px;
                font-weight: bold;
                margin-bottom: 18px;
                qproperty-alignment: AlignCenter;
            }
            QLabel#LogoIcon {
                margin-top: 24px;
                margin-bottom: 8px;
            }
            QListWidget {
                background: #e8f5e9;
                border-radius: 12px;
                font-size: 18px;
                padding: 8px;
                margin-bottom: 18px;
            }
            QListWidget::item {
                padding: 10px 0;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background: #a8e063;
                color: #222;
            }
            QPushButton {
                background: #43a047;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 22px;
                margin: 0 6px;
            }
            QPushButton:hover {
                background: #a8e063;
                color: #222;
            }
        ''')
        layout = QVBoxLayout(self)
        logo_icon = QLabel(self)
        logo_icon.setObjectName("LogoIcon")
        logo_icon.setAlignment(Qt.AlignCenter)
        logo_icon.setPixmap(QPixmap("assets/logotip.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo_icon)
        logo = QLabel("Daily Browser", self)
        logo.setObjectName("LogoLabel")
        layout.addWidget(logo)
        self.list = QListWidget()
        for prof in get_profile_list():
            item = QListWidgetItem(prof)
            avatar_path = get_profile_avatar(prof)
            item.setIcon(QIcon(avatar_path))
            self.list.addItem(item)
        layout.addWidget(self.list)
        btns = QHBoxLayout()
        self.add_btn = QPushButton("Добавить профиль")
        self.del_btn = QPushButton("Удалить профиль")
        self.avatar_btn = QPushButton("Выбрать аватарку")
        self.ok_btn = QPushButton("ОК")
        btns.addWidget(self.add_btn)
        btns.addWidget(self.del_btn)
        btns.addWidget(self.avatar_btn)
        btns.addWidget(self.ok_btn)
        layout.addLayout(btns)
        self.add_btn.clicked.connect(self.add_profile)
        self.del_btn.clicked.connect(self.delete_profile)
        self.avatar_btn.clicked.connect(self.set_avatar)
        self.ok_btn.clicked.connect(self.accept)
        self.list.itemDoubleClicked.connect(self.accept)
        self.selected_avatar = None

    def add_profile(self):
        name, ok = QInputDialog.getText(self, "Новый профиль", "Имя профиля:")
        if ok and name and name not in get_profile_list():
            os.makedirs(get_profile_path(name))
            self.list.addItem(name)

    def set_avatar(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите профиль!")
            return
        fname, _ = QFileDialog.getOpenFileName(self, "Выбрать аватарку", "", "Images (*.png *.jpg *.jpeg *.svg)")
        if fname:
            profile_dir = get_profile_path(item.text())
            ext = os.path.splitext(fname)[1]
            avatar_path = os.path.join(profile_dir, "avatar" + ext)
            shutil.copy(fname, avatar_path)

    def delete_profile(self):
        item = self.list.currentItem()
        if item:
            name = item.text()
            if QMessageBox.question(self, "Удалить?", f"Удалить профиль '{name}'?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                shutil.rmtree(get_profile_path(name))
                self.list.takeItem(self.list.row(item))

    def showEvent(self, event):
        super().showEvent(event)
        self.setWindowOpacity(0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(600)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.start()

def get_profile_avatar(profile_name):
    profile_dir = get_profile_path(profile_name)
    for ext in (".png", ".jpg", ".jpeg", ".svg"):
        path = os.path.join(profile_dir, "avatar" + ext)
        if os.path.exists(path):
            return path
    return "assets/user.svg"

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(480, 320)
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.logo_pixmap = QPixmap("assets/logotip.png").scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_logo)
        self.timer.start(16)
        self.title = QLabel("Daily Browser", self)
        self.title.setFont(QFont("Arial", 36, QFont.Bold))
        self.title.setStyleSheet("color: #fff;")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setGeometry(0, 150, 480, 60)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(90, 230, 300, 24)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet('''
            QProgressBar {
                background: #e8f5e9;
                border-radius: 12px;
                border: 2px solid #43a047;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a8e063, stop:1 #43a047);
                border-radius: 12px;
            }
        ''')
        self.setWindowOpacity(0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(600)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.start()
        self.fake_progress = 0
        self.fake_timer = QTimer(self)
        self.fake_timer.timeout.connect(self.update_fake_progress)
        self.fake_timer.start(50)  # 100 шагов по 50мс = 5 секунд
    def rotate_logo(self):
        self.angle = (self.angle + 3) % 360
        self.update()
    def update_fake_progress(self):
        self.fake_progress += 1
        self.progress.setValue(self.fake_progress)
        if self.fake_progress >= 100:
            self.fake_timer.stop()
            self.finish_splash()
    def finish_splash(self):
        splash_anim = QPropertyAnimation(self, b"windowOpacity")
        splash_anim.setDuration(600)
        splash_anim.setStartValue(1)
        splash_anim.setEndValue(0)
        splash_anim.finished.connect(self.close)
        splash_anim.start()
        QTimer.singleShot(600, start_main)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Градиентный фон с закруглениями
        rect = self.rect()
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0, QColor("#a8e063"))
        grad.setColorAt(1, QColor("#43a047"))
        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 32, 32)
        # Тень (можно добавить через QGraphicsDropShadowEffect, если нужно)
        # Вращающийся логотип
        painter.save()
        painter.translate(self.width() // 2, 88)
        painter.rotate(self.angle)
        painter.translate(-self.logo_pixmap.width() // 2, -self.logo_pixmap.height() // 2)
        painter.drawPixmap(0, 0, self.logo_pixmap)
        painter.restore()

class AddProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать профиль")
        self.setMinimumWidth(340)
        self.setMinimumHeight(180)
        self.setWindowIcon(QIcon("assets/logotip.png"))
        self.setStyleSheet('''
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a8e063, stop:1 #43a047);
                border-radius: 18px;
            }
            QLabel {
                color: #222;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            QLineEdit {
                background: #e8f5e9;
                border: 2px solid #43a047;
                border-radius: 12px;
                padding: 8px 14px;
                font-size: 16px;
                color: #222;
                margin-bottom: 18px;
            }
            QPushButton {
                background: #43a047;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 22px;
                margin: 0 8px;
            }
            QPushButton:hover {
                background: #a8e063;
                color: #222;
            }
        ''')
        layout = QVBoxLayout(self)
        label = QLabel("Имя профиля:")
        self.name_input = QLineEdit()
        btns = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addWidget(label)
        layout.addWidget(self.name_input)
        layout.addLayout(btns)
    def get_name(self):
        return self.name_input.text().strip()

def load_language(profile_path):
    settings_file = os.path.join(profile_path, 'settings.json')
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return settings.get('lang', 'ru')
        except Exception:
            pass
    return 'ru'

def save_language(profile_path, lang):
    settings_file = os.path.join(profile_path, 'settings.json')
    try:
        settings = {}
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        settings['lang'] = lang
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

class MainWindow(QMainWindow):
    def __init__(self, incognito_window=False):
        super().__init__()
        self.incognito_window = incognito_window
        if self.incognito_window:
            self.setWindowTitle("Daily Browser — Инкогнито")
            self.setStyleSheet(self.styleSheet() + "\nQMainWindow { border: 2px solid #222; background: #222 !important; }\n")
            self.profile_name = None
            self.profile_path = None
            self.HISTORY_FILE = None
            self.QUICKLINKS_FILE = None
            self.COOKIES_DIR = None
        else:
            global profile_name
            self.profile_name = profile_name
            self.profile_path = get_profile_path(self.profile_name)
            self.HISTORY_FILE = os.path.join(self.profile_path, "settings/history.json")
            self.QUICKLINKS_FILE = os.path.join(self.profile_path, "settings/quicklinks.json")
            self.COOKIES_DIR = os.path.join(self.profile_path, "cookies")
            if not os.path.exists(self.COOKIES_DIR):
                os.makedirs(self.COOKIES_DIR)
            self.setWindowTitle("Daily Browser - v2.0")
        self.setWindowIcon(QIcon("assets/logotip.png"))
        self.setGeometry(100, 100, 1200, 800)
        
        # Устанавливаем стили для главного окна
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #a8e063, stop:1 #43a047
                );
                border-radius: 10px;
                border: 2px solid #1b5e20;
            }
            QWidget#MainContainer {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                margin: 10px;
            }
            QTabWidget::pane {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 0 0 10px 10px;
                margin: 0 10px 10px 10px;
            }
            QTabBar::tab {
                background: #2e7d32;
                color: white;
                padding: 8px 20px;
                border: 1px solid #1b5e20;
                border-radius: 5px;
                margin-right: 2px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #a8e063;
                color: #222;
                border: 1px solid #7cb342;
            }
            QTabBar::tab:hover:!selected {
                background: #8bc34a;
                color: #222;
            }
            QTabBar::tab:first {
                margin-left: 5px;
            }
            QTabBar::tab:last {
                margin-right: 5px;
            }
            QTabBar::tab:only-one {
                margin: 0 5px;
            }
            QPushButton {
                padding: 8px 16px;
                background: #43a047;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #a8e063;
                color: #222;
            }
            QMenu {
                background: #43a047;
                color: white;
                border: 1px solid #1b5e20;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 8px 28px 8px 20px;
                margin-bottom: 6px;
                min-height: 28px;
            }
            QMenu::item:selected {
                background: #a8e063;
                color: #222;
            }
        """)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 0 0 10px 10px;
                margin: 0 10px 10px 10px;
            }
            QTabWidget::tab-bar {
                alignment: left;
                margin-left: 10px;
            }
        """)

        # Кнопки управления
        new_tab_btn = QPushButton()
        new_tab_btn.setIcon(QIcon("assets/plus.svg"))
        new_tab_btn.setIconSize(QSize(24, 24))
        new_tab_btn.setFixedSize(30, 30)
        new_tab_btn.clicked.connect(self.add_new_tab)

        # Кнопка закладок в стиле Chrome
        self.bookmarks_btn = QPushButton()
        self.bookmarks_btn.setIcon(QIcon("assets/3.svg"))
        self.bookmarks_btn.setIconSize(QSize(24, 24))
        self.bookmarks_btn.setFixedSize(30, 30)
        self.bookmarks_btn.setStyleSheet("""
            QPushButton {
                background: #43a047;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #a8e063;
                color: #222;
            }
        """)
        self.update_bookmarks_menu()
        
        # Кнопка истории
        history_btn = QPushButton()
        history_btn.setIcon(QIcon("assets/history.svg"))
        history_btn.setIconSize(QSize(24, 24))
        history_btn.setFixedSize(30, 30)
        history_btn.setStyleSheet("""
            QPushButton {
                background: #43a047;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #a8e063;
                color: #222;
            }
        """)
        history_btn.clicked.connect(self.show_history)

        # Кнопка профиля
        profile_btn = QPushButton()
        if self.incognito_window:
            profile_btn.setIcon(QIcon(INCOGNITO_ICON))
        else:
            profile_btn.setIcon(QIcon(get_profile_avatar(self.profile_name)))
        self.profile_menu = QMenu()
        self.update_profile_menu()
        # === Добавляем переключатель языка ===
        self.add_language_menu()
        profile_btn.setMenu(self.profile_menu)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.addWidget(new_tab_btn)
        top_layout.addWidget(self.bookmarks_btn)
        top_layout.addWidget(history_btn)
        top_layout.addWidget(profile_btn)
        top_layout.addStretch()

        container = QWidget()
        container.setObjectName("MainContainer")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.tabs)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.add_new_tab()

        self.tabs.tabBar().setMinimumWidth(40)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.tabBar().setStyleSheet('''
            QTabBar::tab {
                min-width: 80px;
                max-width: 200px;
            }
        ''')
        self.tabs.currentChanged.connect(self.adjust_tab_widths)

    def add_new_tab(self):
        tab = BrowserTab(add_shortcut_callback=self.add_link, main_window=self)
        index = self.tabs.addTab(tab, "Новая вкладка")
        self.tabs.setCurrentIndex(index)
        tab.tab_widget = self.tabs
        self.adjust_tab_widths()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            self.adjust_tab_widths()

    def add_link(self):
        dialog = AddLinkDialog()
        if dialog.exec_() == QDialog.Accepted:
            name, url = dialog.get_data()
            if name and url:
                try:
                    with open("settings/quicklinks.json", "r", encoding="utf-8") as f:
                        links = json.load(f)
                except FileNotFoundError:
                    links = []
                if any(link['name'] == name or link['url'] == url for link in links):
                    QMessageBox.warning(self, "Ошибка", "Такой ярлык уже существует!")
                    return
                links.append({"name": name, "url": url})
                with open("settings/quicklinks.json", "w", encoding="utf-8") as f:
                    json.dump(links, f, ensure_ascii=False, indent=4)
                generate_startpage()
                self.update_all_tabs()

    def manage_links(self):
        dialog = ManageLinksDialog(self)
        dialog.exec_()
        self.update_all_tabs()

    def update_all_tabs(self):
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, BrowserTab):
                startpage_path = os.path.abspath("assets/startpage/startpage.html")
                widget.browser.setUrl(QUrl.fromLocalFile(startpage_path))

    def adjust_tab_widths(self):
        tabbar = self.tabs.tabBar()
        count = tabbar.count()
        if count == 0:
            return
        total_width = tabbar.width() - 20  # небольшой запас
        max_tab_width = 200
        min_tab_width = 30  # теперь вкладки могут быть очень узкими
        tab_width = max(min_tab_width, min(max_tab_width, total_width // count))
        tabbar.setStyleSheet(f'''
            QTabBar::tab {{
                min-width: {tab_width}px;
                max-width: {tab_width}px;
                padding-left: 6px;
                padding-right: 6px;
            }}
        ''')

    def show_history(self):
        dlg = HistoryPage(self.HISTORY_FILE, self)
        if dlg.exec_() == QDialog.Accepted:
            pass

    def open_url_in_new_tab(self, url):
        tab = BrowserTab(url=url, add_shortcut_callback=self.add_link, main_window=self)
        index = self.tabs.addTab(tab, "Новая вкладка")
        self.tabs.setCurrentIndex(index)
        tab.tab_widget = self.tabs
        self.adjust_tab_widths()

    def add_language_menu(self):
        lang_menu = QMenu(_t('language'), self)
        ru_action = lang_menu.addAction(_t('russian'))
        en_action = lang_menu.addAction(_t('english'))
        ru_action.triggered.connect(lambda: self.set_language('ru'))
        en_action.triggered.connect(lambda: self.set_language('en'))
        self.profile_menu.addMenu(lang_menu)

    def update_profile_menu(self):
        self.profile_menu.clear()
        for prof in get_profile_list():
            act = self.profile_menu.addAction(prof)
            act.setCheckable(True)
            act.setChecked(prof == self.profile_name)
            act.triggered.connect(lambda checked, p=prof: self.switch_profile(p))
        self.profile_menu.addSeparator()
        self.profile_menu.addAction(_t('add_profile'), self.add_profile)
        self.profile_menu.addAction(_t('delete_profile'), self.delete_profile)
        self.profile_menu.addAction(_t('new_incognito_tab'), self.new_incognito_tab)
        self.profile_menu.addAction(_t('new_incognito_window'), self.new_incognito_window)
        self.profile_menu.addSeparator()
        self.add_language_menu()

    def switch_profile(self, new_profile):
        if new_profile == self.profile_name:
            return
        # Перезапуск приложения с новым профилем
        python = sys.executable
        script = sys.argv[0]
        subprocess.Popen([python, script, new_profile])
        QApplication.quit()

    def add_profile(self):
        dlg = AddProfileDialog()
        if dlg.exec_() == QDialog.Accepted:
            name = dlg.get_name()
            if name and name not in get_profile_list():
                os.makedirs(get_profile_path(name))
                self.update_profile_menu()

    def delete_profile(self):
        if len(get_profile_list()) <= 1:
            QMessageBox.warning(self, "Ошибка", "Должен остаться хотя бы один профиль!")
            return
        name, ok = QInputDialog.getText(self, "Удалить профиль", "Имя профиля для удаления:")
        if ok and name in get_profile_list():
            if QMessageBox.question(self, "Удалить?", f"Удалить профиль '{name}'?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                shutil.rmtree(get_profile_path(name))
                if name == self.profile_name:
                    # Если удаляем текущий профиль — перезапуск
                    profiles = get_profile_list()
                    if profiles:
                        self.switch_profile(profiles[0])
                self.update_profile_menu()

    def new_incognito_tab(self):
        tab = BrowserTab(add_shortcut_callback=self.add_link, incognito=True, main_window=self)
        index = self.tabs.addTab(tab, "Инкогнито")
        self.tabs.setCurrentIndex(index)
        tab.tab_widget = self.tabs
        self.adjust_tab_widths()

    def new_incognito_window(self):
        python = sys.executable
        script = sys.argv[0]
        subprocess.Popen([python, script, "--incognito"])

    def closeEvent(self, event):
        if self.incognito_window:
            return super().closeEvent(event)
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle(_t("save_tabs"))
        box.setText(_t("save_tabs_text"))
        yes_btn = box.addButton(_t('yes'), QMessageBox.YesRole)
        no_btn = box.addButton(_t('no'), QMessageBox.NoRole)
        cancel_btn = box.addButton(_t('cancel'), QMessageBox.RejectRole)
        box.setDefaultButton(yes_btn)
        box.exec_()
        clicked = box.clickedButton()
        if clicked == cancel_btn:
            event.ignore()
            return
        if clicked == yes_btn:
            urls = []
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if hasattr(widget, 'browser'):
                    url = widget.browser.url().toString()
                    if url:
                        urls.append(url)
            session_file = os.path.join(self.profile_path, "session.json")
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(urls, f, ensure_ascii=False, indent=2)
        else:
            session_file = os.path.join(self.profile_path, "session.json")
            if os.path.exists(session_file):
                os.remove(session_file)
        super().closeEvent(event)

    def set_language(self, lang):
        global current_lang
        current_lang = lang
        # === Сохраняем язык в настройки профиля ===
        if not self.incognito_window:
            save_language(self.profile_path, lang)
        self.update_profile_menu()
        self.update_bookmarks_menu()
        generate_startpage(lang)
        self.update_all_tabs()
        self.profile_menu.update()
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, HistoryPage):
                widget.update_texts()

    def update_bookmarks_menu(self):
        bookmarks_menu = QMenu()
        bookmarks = []
        try:
            with open("settings/quicklinks.json", "r", encoding="utf-8") as f:
                bookmarks = json.load(f)
        except Exception:
            pass
        for i, link in enumerate(bookmarks):
            action = bookmarks_menu.addAction(link["name"])
            action.triggered.connect(lambda checked, url=link["url"]: self.open_url_in_new_tab(url))
            if i < len(bookmarks) - 1:
                spacer = QAction("", bookmarks_menu)
                spacer.setSeparator(True)
                bookmarks_menu.addAction(spacer)
                spacer_widget = QWidget()
                spacer_widget.setFixedHeight(32)
                spacer_action = QWidgetAction(bookmarks_menu)
                spacer_action.setDefaultWidget(spacer_widget)
                bookmarks_menu.addAction(spacer_action)
        bookmarks_menu.addSeparator()
        manage_action = bookmarks_menu.addAction(_t('manage_bookmarks'))
        manage_action.triggered.connect(self.manage_links)
        add_action = bookmarks_menu.addAction(_t('add_bookmark'))
        add_action.triggered.connect(self.add_link)
        self.bookmarks_btn.setMenu(bookmarks_menu)

def start_main():
    global profile_name, splash, current_lang
    splash.close()
    incognito_window = False
    if "--incognito" in sys.argv:
        incognito_window = True
    if not incognito_window:
        if len(sys.argv) > 1:
            profile_name = sys.argv[1]
        else:
            profiles = get_profile_list()
            if not profiles:
                dlg = AddProfileDialog()
                if dlg.exec_() == QDialog.Accepted:
                    name = dlg.get_name()
                    if name:
                        os.makedirs(get_profile_path(name))
                        profile_name = name
                    else:
                        sys.exit(0)
                else:
                    sys.exit(0)
            elif len(profiles) == 1:
                profile_name = profiles[0]
            else:
                dlg = ProfileManagerDialog()
                if dlg.exec_() == QDialog.Accepted:
                    profile_name = dlg.list.currentItem().text()
                else:
                    sys.exit(0)
        generate_startpage()
        # === Загружаем язык из настроек профиля ===
        profile_path = get_profile_path(profile_name)
        current_lang = load_language(profile_path)
        window = MainWindow()
        # Восстановление вкладок из session.json
        session_file = os.path.join(window.profile_path, "session.json")
        if os.path.exists(session_file):
            reply = QMessageBox.question(window, "Восстановить вкладки?", "Обнаружены сохранённые вкладки. Восстановить их?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        urls = json.load(f)
                    window.tabs.clear()
                    for url in urls:
                        window.open_url_in_new_tab(url)
                    # Удалить пустую первую вкладку, если она есть
                    if window.tabs.count() > len(urls):
                        window.tabs.removeTab(0)
                except Exception:
                    pass
            os.remove(session_file)
    else:
        window = MainWindow(incognito_window=True)
    window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    screen = QApplication.primaryScreen().geometry()
    splash.move(
        screen.center().x() - splash.width() // 2,
        screen.center().y() - splash.height() // 2
    )
    splash.show()
    sys.exit(app.exec_())

import sys, requests, json, os, winsound, datetime, shutil
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, 
                             QPushButton, QComboBox, QMessageBox, QTabWidget, QFormLayout, 
                             QHBoxLayout, QListWidget, QListWidgetItem)
from PyQt6.QtGui import QTextCharFormat, QFont, QIcon

class YazarPress(QWidget):
    def __init__(self):
        super().__init__()
        # AppData Klasör Yapısı
        self.appdata_yolu = os.path.join(os.getenv('LOCALAPPDATA'), "YazarPress")
        if not os.path.exists(self.appdata_yolu):
            os.makedirs(self.appdata_yolu)
        self.ayar_f = os.path.join(self.appdata_yolu, "ayarlar.json")
        self.arsiv_f = os.path.join(self.appdata_yolu, "taslaklar.json")
        
        if os.path.exists("logo.png"):
            self.setWindowIcon(QIcon("logo.png"))
        self.init_ui()
        self.load_a()
        self.refresh_local_list()

    def init_ui(self):
        self.setWindowTitle('YazarPress v2.6')
        self.setGeometry(300, 200, 900, 850)
        ana_duzen = QVBoxLayout(); self.tabs = QTabWidget()
        
        # Sekme 1: Yazı Yazma
        self.t1 = QWidget(); l1 = QVBoxLayout(); f1 = QFormLayout()
        self.e_t = QLineEdit(); f1.addRow("İçerik Başlığı:", self.e_t)
        self.c_tp = QComboBox(); self.c_tp.addItems(["Yazı", "Sayfa"]); f1.addRow("Tür:", self.c_tp)
        self.c_ct = QComboBox(); self.c_ct.addItem("Genel", 1); f1.addRow("Kategori:", self.c_ct)
        self.e_tg = QLineEdit(); f1.addRow("Etiketler:", self.e_tg)
        araclar = QHBoxLayout()
        b_b = QPushButton("Kalın"); b_b.clicked.connect(self.s_b); araclar.addWidget(b_b)
        b_i = QPushButton("İtalik"); b_i.clicked.connect(self.s_i); araclar.addWidget(b_i)
        self.btn_mode = QPushButton("HTML"); self.btn_mode.setCheckable(True); self.btn_mode.toggled.connect(self.toggle_mode); araclar.addWidget(self.btn_mode)
        f1.addRow("Düzenleme:", araclar); self.txt = QTextEdit(); l1.addLayout(f1); l1.addWidget(self.txt)
        butonlar = QHBoxLayout()
        btn_local = QPushButton("Arşive Kaydet"); btn_local.clicked.connect(self.save_local_draft); butonlar.addWidget(btn_local)
        btn_draft = QPushButton("Taslak Gönder"); btn_draft.clicked.connect(lambda: self.send("draft")); butonlar.addWidget(btn_draft)
        btn_pub = QPushButton("Yayınla"); btn_pub.clicked.connect(lambda: self.send("publish")); butonlar.addWidget(btn_pub)
        l1.addLayout(butonlar); self.t1.setLayout(l1)

        # Diğer Sekmeler (Canlı ve Yerel)
        self.t2 = QWidget(); l2 = QVBoxLayout(); self.btn_wp_refresh = QPushButton("Yayınları Listele"); self.btn_wp_refresh.clicked.connect(self.fetch_wp_published); l2.addWidget(self.btn_wp_refresh); self.wp_list = QListWidget(); l2.addWidget(self.wp_list); self.t2.setLayout(l2)
        self.t3 = QWidget(); l3 = QVBoxLayout(); self.local_list = QListWidget(); l3.addWidget(self.local_list); bl = QHBoxLayout(); btn_load = QPushButton("Düzenle"); btn_load.clicked.connect(self.load_selected_draft); bl.addWidget(btn_load); btn_del = QPushButton("Sil"); btn_del.clicked.connect(self.delete_selected_draft); bl.addWidget(btn_del); l3.addLayout(bl); self.t3.setLayout(l3)

        # Sekme 4: Ayarlar (SIFIRLAMA ÖZELLİĞİ EKLENDİ)
        self.t4 = QWidget(); f4 = QFormLayout()
        self.u = QLineEdit(); f4.addRow("Site URL:", self.u)
        self.un = QLineEdit(); f4.addRow("Kullanıcı Adı:", self.un)
        self.pw = QLineEdit(); self.pw.setEchoMode(QLineEdit.EchoMode.Password); f4.addRow("Şifre:", self.pw)
        btn_save = QPushButton("Bilgileri Kaydet"); btn_save.clicked.connect(self.save_a); f4.addRow(btn_save)
        
        # KIRMIZI BUTON: SIFIRLAMA
        self.btn_reset = QPushButton("Tüm Sistem Verilerini Sıfırla")
        self.btn_reset.setStyleSheet("background-color: #c62828; color: white; font-weight: bold; height: 30px;")
        self.btn_reset.clicked.connect(self.sistemi_sifirla)
        f4.addRow(self.btn_reset)
        self.t4.setLayout(f4)

        self.tabs.addTab(self.t1, "Yazı"); self.tabs.addTab(self.t2, "Canlı"); self.tabs.addTab(self.t3, "Arşiv"); self.tabs.addTab(self.t4, "Ayar")
        ana_duzen.addWidget(self.tabs); self.setLayout(ana_duzen)

    def sistemi_sifirla(self):
        cevap = QMessageBox.warning(self, "Kritik Uyarı", "Tüm site ayarlarınız ve yerel taslaklarınız kalıcı olarak silinecektir. Emin misiniz?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if cevap == QMessageBox.StandardButton.Yes:
            try:
                if os.path.exists(self.appdata_yolu):
                    shutil.rmtree(self.appdata_yolu) # AppData klasörünü komple siler
                QMessageBox.information(self, "Başarılı", "Sistem verileri temizlendi. Program kapatılacak.")
                sys.exit() # Temizlik sonrası güvenli çıkış
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Silme işlemi başarısız: {str(e)}")

    def fetch_wp_published(self):
        url = self.u.text().strip().rstrip("/"); self.wp_list.clear()
        try:
            r = requests.get(f"{url}/wp-json/wp/v2/posts?status=publish", auth=(self.un.text(), self.pw.text()), timeout=15)
            if r.status_code == 200:
                for p in r.json(): self.wp_list.addItem(f"[{p['date']}] - {p['title']['rendered']}")
                winsound.MessageBeep(winsound.MB_OK)
        except: pass

    def save_local_draft(self):
        data = {"title": self.e_t.text(), "content": self.txt.toHtml(), "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
        arsiv = []
        if os.path.exists(self.arsiv_f):
            with open(self.arsiv_f, "r", encoding="utf-8") as f: arsiv = json.load(f)
        arsiv.append(data)
        with open(self.arsiv_f, "w", encoding="utf-8") as f: json.dump(arsiv, f, ensure_ascii=False, indent=4)
        self.refresh_local_list(); winsound.MessageBeep(winsound.MB_OK)

    def refresh_local_list(self):
        self.local_list.clear()
        if os.path.exists(self.arsiv_f):
            with open(self.arsiv_f, "r", encoding="utf-8") as f:
                arsiv = json.load(f)
                for d in arsiv: self.local_list.addItem(f"{d['date']} - {d['title']}")

    def load_selected_draft(self):
        row = self.local_list.currentRow()
        if row != -1:
            with open(self.arsiv_f, "r", encoding="utf-8") as f:
                arsiv = json.load(f); self.e_t.setText(arsiv[row]['title']); self.txt.setHtml(arsiv[row]['content']); self.tabs.setCurrentIndex(0)

    def delete_selected_draft(self):
        row = self.local_list.currentRow()
        if row != -1:
            with open(self.arsiv_f, "r", encoding="utf-8") as f: arsiv = json.load(f)
            arsiv.pop(row)
            with open(self.arsiv_f, "w", encoding="utf-8") as f: json.dump(arsiv, f, ensure_ascii=False, indent=4)
            self.refresh_local_list()

    def toggle_mode(self, checked):
        if checked: self.txt.setPlainText(self.txt.toHtml())
        else: self.txt.setHtml(self.txt.toPlainText())

    def send(self, status):
        url = self.u.text().strip().rstrip("/")
        tur = "posts" if self.c_tp.currentIndex() == 0 else "pages"
        content = self.txt.toPlainText() if self.btn_mode.isChecked() else self.txt.toHtml()
        p = {"title": self.e_t.text(), "content": content, "status": status}
        try:
            r = requests.post(f"{url}/wp-json/wp/v2/{tur}", json=p, auth=(self.un.text(), self.pw.text()), timeout=20)
            if r.status_code == 201: winsound.MessageBeep(winsound.MB_OK); QMessageBox.information(self, "Başarılı", "İçerik gönderildi.")
        except: pass

    def save_a(self):
        try:
            d = {"u": self.u.text(), "un": self.un.text(), "pw": self.pw.text()}
            with open(self.ayar_f, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Başarılı", "Bilgiler kaydedildi.")
        except: pass

    def load_a(self):
        if os.path.exists(self.ayar_f):
            try:
                with open(self.ayar_f, "r", encoding="utf-8") as f:
                    d = json.load(f); self.u.setText(d.get("u", "")); self.un.setText(d.get("un", "")); self.pw.setText(d.get("pw", ""))
            except: pass

    def s_b(self):
        f = QTextCharFormat(); f.setFontWeight(QFont.Weight.Bold if self.txt.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal); self.txt.mergeCurrentCharFormat(f)

    def s_i(self):
        f = QTextCharFormat(); f.setFontItalic(not self.txt.fontItalic()); self.txt.mergeCurrentCharFormat(f)

if __name__ == '__main__':
    app = QApplication(sys.argv); ex = YazarPress(); ex.show(); sys.exit(app.exec())
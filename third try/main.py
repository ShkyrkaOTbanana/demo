import sys
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMessageBox, QFrame, QLabel, QFileDialog, QWidget
import mysql.connector
from mysql.connector import Error

class DB:
    def connect_db(self):
        try:
            connection = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="root",
                database="demo22"
            )
            return connection
        except Error as e:
            print(e)
            return None

class CardEdit(QFrame):
    def __init__(self):
        super().__init__()
        uic.loadUi("card_edit.ui", self)
        self.main_frame.setFixedSize(500, 237)
        self.cancel_btn.clicked.connect(self.cancel)
        self.select_btn.clicked.connect(self.select_photo)
        self.oncreate()
        self.save_btn.clicked.connect(self.save)

    def cancel(self):
        self.close()

    def select_photo(self):
        file_name = QFileDialog.getOpenFileName(self, "Выбор фото", "./", "*.png *.jpg *.jpeg")
        self.photo_path = file_name[0]
        pixmap = QPixmap(self.photo_path)
        self.photo_label.setPixmap(pixmap.scaled(269, 237))

    def oncreate(self):
        self.db = DB()
        conn = self.db.connect_db()
        cur = conn.cursor()

        cur.execute("select * from category_name")
        for row in cur.fetchall():
            self.cb_name.addItem(row[1], row[0])

        cur.execute("select * from type_name")
        for row in cur.fetchall():
            self.cb_type_name.addItem(row[1], row[0])

        cur.execute("select * from manufacturer_name")
        for row in cur.fetchall():
            self.cb_manufacturer.addItem(row[1], row[0])

        cur.execute("select * from measure_name")
        for row in cur.fetchall():
            self.cb_measure.addItem(row[1], row[0])

        cur.execute("select * from supplier_name")
        for row in cur.fetchall():
            self.cb_supplier.addItem(row[1], row[0])

        cur.close()
        conn.close()

    def save(self):
        text_cb_name = self.cb_name.currentData()
        text_cb_type_name = self.cb_type_name.currentData()
        text_cb_manufacturer = self.cb_manufacturer.currentData()
        text_cb_measure = self.cb_measure.currentData()
        text_cb_supplier = self.cb_supplier.currentData()
        text_description_edit = self.description_edit.text()
        text_price_edit = int(self.price_edit.text())
        text_remain_edit = int(self.remain_edit.text())
        text_discont_edit = int(self.discont_edit.text())
        text_photo = getattr(self, "photo_path", None)

        self.db = DB()
        conn = self.db.connect_db()
        cur = conn.cursor()

        cur.execute("insert into tovar (id_tovar, type_name, measure, price, supplier, manufacturer, category, discont, remain, description, photo) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (f"K345R4444{+text_remain_edit}", text_cb_type_name, text_cb_measure, text_price_edit, text_cb_supplier, text_cb_manufacturer, text_cb_name, text_discont_edit, text_remain_edit, text_description_edit, text_photo))
        conn.commit()

        cur.close()
        conn.close()

        self.close()

class Card(QFrame):
    def __init__(self):
        super().__init__()
        uic.loadUi('card.ui', self)
        self.delete_btn.clicked.connect(self.delete_card)
        self.edit_btn.clicked.connect(self.edit_card)
        self.main_frame.setFixedSize(500, 237)

    def delete_card(self):
        self.close()

    def edit_card(self):
        self.editcard = CardEdit()
        self.editcard.show()

class TableWindwow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("table.ui", self)

        self.exit_btn.clicked.connect(self.go_back)
        self.card_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.oncreate()
        self.cb_sort.currentTextChanged.connect(self.load_cards)
        self.cb_how.currentTextChanged.connect(self.load_cards)
        self.load_cards()
        self.add_tovar.clicked.connect(self.open_edit)
        self.sort_btn.clicked.connect(self.load_cards)

    def oncreate(self):
        items = ["DESC", "ASC"]
        self.cb_how.addItems(items)
        items2 = ["type_name", "measure", "price", "supplier", "manufacturer", "category", "discont", "remain", "description", "photo"]
        self.cb_sort.addItems(items2)

    def open_edit(self):
        self.editcard = CardEdit()
        self.editcard.show()

    def go_back(self):
        self.loginform = LoginWindow()
        self.loginform.show()
        self.close()

    def load_cards(self):
        QWidget().setLayout(self.card_layout)
        self.card_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        text_cb_sort = self.cb_sort.currentText()
        text_cb_how = self.cb_how.currentText()

        self.db = DB()
        conn = self.db.connect_db()

        cur = conn.cursor()

        query = f"""select tn.name, mn.name, t.price, sn.name, mnn.name, cn.name, t.discont, t.remain, t.description, t.photo
                 from tovar t
                 left join type_name tn on t.type_name = tn.id_name
                 left join measure_name mn on t.measure = mn.id_name
                 left join supplier_name sn on t.supplier = sn.id_name
                 left join manufacturer_name mnn on t.manufacturer = mnn.id_name
                 left join category_name cn on t.category = cn.id_name
                 order by {text_cb_sort} {text_cb_how}"""

        cur.execute(query)

        result = cur.fetchall()

        layout = self.card_layout

        for row in result:
            card = Card()

            card.type_name_label.setText(f"Категория: {row[0]}")  # type
            card.measure_label.setText(f"Единица измерения: {row[1]}")  # measure
            card.price_label.setText(f"Цена: {row[2]} ₽")  # price
            card.supplier_label.setText(f"Поставщик: {row[3]}")  # supplier
            card.manufacturer_label.setText(f"Производитель: {row[4]}")  # manufacturer
            card.name_label.setText(f"Наименование: {row[5]}")  # category
            card.discount_label.setText(f"Действующая скидка: {row[6]}")  # discount
            card.remain_label.setText(f"Количество на складе: {row[7]}")  # remain
            card.desc_label.setText(f"Описание товара: {row[8]}")  # description

            pixmap = QPixmap(str(row[9]))
            card.photo_label.setPixmap(pixmap.scaled(269, 237))

            layout.addWidget(card)

        cur.close()
        conn.close()

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("enter.ui", self)

        self.enter_btn.clicked.connect(self.enter)

    def enter(self):
        self.db = DB()
        conn = self.db.connect_db()
        cursor = conn.cursor()

        login = self.login_edit.text()
        password = self.password_edit.text()

        cursor.execute("select fio, role from users where login = %s and password = %s", (login, password))

        result = cursor.fetchall()

        if result:
            self.tableform = TableWindwow()
            self.tableform.show()
            for row in result:
                self.tableform.user_label.setText(f"Пользователь: {row[0]}")
            self.close()

        else:
            QMessageBox.warning(self, "Ошибка", "Ошибка")

        cursor.close()
        conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    app.exec()
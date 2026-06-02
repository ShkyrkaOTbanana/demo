import PyQt5
import sys
import mysql.connector
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFrame, QScrollArea, QVBoxLayout, QWidget
from mysql.connector import Error


class DB:
    def connect_to_db(self):
        try:
            connection = mysql.connector.connect(
                host="127.0.0.1",
                port=3306,
                user="root",
                passwd="root",
                database="final",
            )
            return connection
        except Error as e:
            print(e)

class CardForm(QFrame):
    def __init__(self):
        super().__init__()
        uic.loadUi("card.ui", self)

        self.setFixedSize(1230, 266)
        self.verticalFrame_3.setFixedSize(300, 269)
        self.verticalFrame_2.setFixedSize(630, 300)
        self.verticalFrame.setFixedSize(280, 250)



class TableForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("table.ui", self)

        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("Компания продажи строительных материалов")

        self.exit_btn.clicked.connect(self.exit)

        self.oncreate()
        self.card_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.cb_what.currentTextChanged.connect(self.load_cards)
        self.cb_how.currentTextChanged.connect(self.load_cards)
        self.load_cards()

    def oncreate(self):
        items_what = ["кол-во товаров", "цену", "скидку"]
        self.cb_what.addItems(items_what)
        items_how = ["возрастанию", "убыванию"]
        self.cb_how.addItems(items_how)

        self.db = DB()
        conn = self.db.connect_to_db()
        cur = conn.cursor()

        cur.execute("select * from manufacturer_name")

        result = cur.fetchall()

        items_manufacturer = ["все производители"]

        for row in result:
            items_manufacturer.append(row[1])

        cur.close()
        conn.close()

        self.cb_manufacturer.addItems(items_manufacturer)


    def load_cards(self):
        QWidget().setLayout(self.card_layout)
        self.card_layout = QVBoxLayout(self.scrollAreaWidgetContents)


        if self.cb_what.currentText() == "кол-во товаров":
            what_sort = "remain"
        elif self.cb_what.currentText() == "цену":
            what_sort = "price"
        elif self.cb_what.currentText() == "скидку":
            what_sort = "discont"

        if self.cb_how.currentText() == "возрастанию":
            how_sort = "DESC"
        elif self.cb_how.currentText() == "убыванию":
            how_sort = "ASC"


        self.db = DB()
        conn = self.db.connect_to_db()
        cur = conn.cursor()

        query = f"""select 
                        t.id_tovar,
                        t.articul,
                        tn.name,
                        mn.name,
                        t.price,
                        sn.name,
                        mnn.name,
                        ctn.name,
                        t.discont,
                        t.remain,
                        t.description,
                        t.photo
                    from tovar as t
                    left join tovar_name as tn on t.tovar_name = tn.id_name
                    left join measure_name as mn on t.measure_name = mn.id_name
                    left join supplier_name as sn on t.supplier_name = sn.id_name
                    left join manufacturer_name as mnn on t.manufacturer_name = mnn.id_name
                    left join category_tovar_name as ctn on t.category_tovar_name = ctn.id_name
                    order by {what_sort} {how_sort}"""

        cur.execute(query)

        result = cur.fetchall()

        layout = self.card_layout

        for row in result:
            card = CardForm()
            card.label_10.setText(f"Категория товара: {row[7]} |")
            card.label_9.setText(f"Наименование товара: {row[2]}")
            card.label_3.setText(f"Описание товара: {row[10]}")
            card.label_5.setText(f"Производитель: {row[6]} ")
            card.label_6.setText(f"Поставщик: {row[5]}")
            card.label_7.setText(f"Цена: {row[4]}")
            card.label_8.setText(f"Единица измерения: {row[3]}")
            card.label_4.setText(f"Количество на складе: {row[1]}")
            card.label_2.setText(f"Действующая скидка: {row[8]}")
            card.id_card = str(row[0])

            pixmap = QPixmap(str(row[11]))
            card.photo_label.setPixmap(pixmap.scaled(300, 269))

            layout.addWidget(card)

        cur.close()
        conn.close()



    def exit(self):
        self.close()
        self.login_form = LoginForm()
        self.login_form.show()


class LoginForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)

        self.enter_btn.clicked.connect(self.enter)
        self.quest_btn.clicked.connect(self.quest)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("Компания продажи строительных материалов")

    def quest(self):
        self.table = TableForm()
        self.table.show()
        self.close()
        self.table.user_label.setText("Пользователь: гость")
        self.table.label.hide()
        self.table.cb_what.hide()
        self.table.cb_how.hide()
        self.table.label_2.hide()
        self.table.cb_table.hide()
        self.table.label_3.hide()


    def enter(self):
        self.db = DB()
        conn = self.db.connect_to_db()
        cur = conn.cursor()

        login = self.login_edit.text()
        password = self.password_edit.text()

        cur.execute("select role, fio from users where login = %s and password = %s", (login,password))

        result = cur.fetchall()

        if result:
            self.table = TableForm()
            self.table.show()
            self.close()
            for row in result:
                self.table.user_label.setText(f'Пользователь: {row[1]}')
                if row[0] == "3":
                    self.table.label.hide()
                    self.table.cb_what.hide()
                    self.table.cb_how.hide()
                    self.table.label_2.hide()
                    self.table.cb_table.hide()
                    self.table.label_3.hide()

        else:
            QMessageBox.warning(self, "err", "err")


        cur.close()
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginForm()
    window.show()
    sys.exit(app.exec())

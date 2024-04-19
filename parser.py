import re

from bs4 import BeautifulSoup
from selenium import webdriver
import sqlite3 as db
import time





class parsing:

    def get_source_html(self, url="https://priem.gubkin.ru/#/education-catalog"):

        driver = webdriver.Chrome()

        driver.maximize_window()

        try:
            driver.get(url=url)
            time.sleep(3)

            with open("index.html", "w", encoding="utf8") as file:
                file.write(driver.page_source)


        except Exception as _ex:
            print(_ex)
        finally:
            driver.close()
            driver.quit()

    def get_html_items(self, file_path="index.html"):

        def input_name(data, add=False):
            if add:
                add = 0
            else:
                add = 1
            n = len(data)
            if n == 4:
                datas[data[0]] = add
            elif n == 5:
                datas[" ".join(data[0:2])] = add
            elif n == 6:
                datas[" ".join(data[0:3])] = add

        with open(file_path, encoding="utf8") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        items_matcard = soup.find_all("mat-card", class_="mat-card mat-focus-indicator education-catalog-list__item columns ng-star-inserted")
        items = []
        for item in items_matcard:
            datas = {}

            facultet = item.find("div").find_all("u", recursive=False)
            for fac in facultet:
                datas['facultet'] = fac.text.strip()

            napravlenie = item.find("div").find("strong").text
            datas['napravlenie'] = napravlenie.strip()

            name = item.find("div").find("h3").find("u").text
            datas['name'] = name.strip()

            mesta = item.find('div', class_="ng-star-inserted", recursive=False).text
            mesta = mesta.strip().split()
            if len(mesta) == 4:
                datas['mesta_b'] = mesta[-1]
            elif len(mesta) > 4:
                datas['mesta_b'] = mesta[3]
                datas['mesta_cel'] = mesta[-3]
            mesta = item.find_all("div", class_=False, recursive=False)
            mesta = mesta[-1].find("div", class_="ng-star-inserted", recursive=False)
            if mesta is not None:
                mesta = mesta.text.strip().split()
                if len(mesta) == 10:
                    datas['RF'] = mesta[5]
                    datas['nRF'] = mesta[-1]
                elif len(mesta) == 5:
                    datas['RF'] = mesta[-1]
                    datas['nRF'] = 0
            else:
                datas['RF'] = 0
                datas['nRF'] = 0

            # group = item.find("div").find("div").find("u").text
            # vremya = item.find("div").find("div", class_="tag").text

            subjects = item.find("div", class_="exam-column").find_all("div", {"class": ["exam-column__item ng-star-inserted", "ng-star-inserted"]}, recursive=False)
            for sub in subjects:
                data = sub.text
                data = data.strip().split()
                input_name(data)

            add_subjects = item.find("div", class_="exam-column").find("div", class_="exam-column condition-exams ng-star-inserted")
            if add_subjects is not None:
                add_subjects = add_subjects.find_all("div", class_="exam-column__item ng-star-inserted")
                for sub in add_subjects:
                    data = sub.text
                    data = data.strip().split()
                    input_name(data, add=True)

            prohod = item.find("div", class_="year-rating ng-star-inserted").text.strip().split()
            if prohod is not None:
                for i in range(3, 3-len(prohod), -1):
                    datas[f"202{i}"] = prohod[3-i]

            items.append(datas)

        with open("items.txt", "w", encoding='utf8') as file:
            for item in items:
                file.write(f"{item}\n")

        return "[INFO] Urls collected successfully"

    def download_to_database(self, db_name='gubkin3v', items_path="items.txt"):
        conn = db.connect(db_name+'.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE '+db_name+' ( id INTEGER NOT NULL, '
                                               'facultet TEXT NOT NULL, '
                                               'napravlenie TEXT NOT NULL, '
                                               'name TEXT NOT NULL, '
                                               '"mesta_b" INTEGER DEFAULT 0, '
                                               '"mesta_cel" INTEGER DEFAULT 0, '
                                               '"RF" INTEGER, '
                                               '"nRF" INTEGER, '
                                               '"Math" BOOLEN, '
                                               '"Physic" BOOLEN, '
                                               '"Infa" BOOLEN, '
                                               '"Russian" BOOLEN, '
                                               '"Chemistry" BOOLEN, '
                                               '"Geography" BOOLEN, '
                                               '"Obschestvo" BOOLEN, '
                                               '"History" BOOLEN, '
                                               '"Foreingh" BOOLEN, '
                                               '"PE" BOOLEN, '
                                               '"year_2021" INTEGER DEFAULT 0, '
                                               '"year_2022" INTEGER DEFAULT 0, '
                                               '"year_2023" INTEGER DEFAULT 0, '
                                               'PRIMARY KEY (id) )')

        dt_subj = {"facultet": "facultet", "napravlenie": "napravlenie", "name": "name",
                   "mesta_b": "mesta_b", "mesta_cel": "mesta_cel", "RF": "RF", "nRF": "nRF",
                   "Математика": "Math", "Физика": "Physic", "Информатика и ИКТ": "Infa",
                   "География": "Geography",
                   "Русский язык": "Russian", "Химия": "Chemistry", "Обществознание": "Obschestvo",
                   "История": "History", "Иностранный язык": "Foreingh", "Физ. подготовка": "PE",
                   "2021": "year_2021", "2022": "year_2022", "2023": "year_2023"}
        with open(items_path, encoding='utf8') as file:
            lines = file.readlines()
            for line in lines:
                dt = eval(line)
                keys = ''
                for key in dt.keys():
                    keys = keys + f'"{dt_subj[key]}"' + ','
                keys = keys[0:-1]
                question_marks = ','.join(list('?' * len(dt)))
                values = tuple(dt.values())
                cursor.execute('INSERT INTO '+db_name+' ('+keys+') VALUES ('+question_marks+')', values)

        conn.commit()
        conn.close()


def main():
    P = parsing()
    #P.get_source_html()   #получение html документа
    #P.get_html_items()    #парсинг html документа
    P.download_to_database()   #сохранение в БД


if __name__ == '__main__':
    main()
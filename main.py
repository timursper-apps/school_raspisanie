import sqlite3, customtkinter as ct, pandas as pd, requests, webbrowser as wb, os
from CTkMessagebox import CTkMessagebox as mb
from CTkTable import *
from tkinter import *
from tkhtmlview import HTMLLabel
version = "1.3"

activated = False

connection = sqlite3.connect("timetable.db")
cursor = connection.cursor()

tgusername = "timursper_community"
linkForAds = f"https://vk.com/{tgusername}"

keyconn = sqlite3.connect("keys.db")
keycurs = keyconn.cursor()

keycurs.execute("""
    CREATE TABLE IF NOT EXISTS keys (
                key TEXT
    )
""")
keyconn.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS calls (
        номерУрока INTEGER,
        время TEXT          
    )
""")
connection.commit()

root = ct.CTk()
root.title(f"Школьное расписание {version}")
root.geometry("460x400")
#pws.apply_style(root, "aero")

days = ['понедельник', 'вторник', 'среда', 'четврерг', 'пятница', 'суббота']

def callsSchedule():
    callsr = ct.CTk()
    callsr.title("Менеджер расписания звонков")
    callsr.geometry("550x150")
    callsr.resizable(False, False)

    tip = ct.CTkLabel(callsr, text="Добавление нового урока", font=("Arial", 18, "bold"))
    tip.place(x=0, y=0)

    def addCall():
        try:
            cursor.execute("INSERT INTO calls (номерУрока, время) VALUES (?, ?)", (idOfLesson.get(), timeOfLesson.get(),))
            connection.commit()
        except:
            mb(title="Ошибка!", message="При добавлении звонка произошла ошибка!", icon="cancel")
        else:
            mb(title="Успешно!", message="Звонок добавлен в расписание!", icon="check")
    
    def checkCalls():
        callstt = ct.CTk()
        callstt.title("Расписание звонков")

        cursor.execute("SELECT * FROM calls")
        callsttvalue = cursor.fetchall()

        table = CTkTable(callstt, column=2, values=callsttvalue)
        table.pack()

        callstt.mainloop()
    
    def remCall():
        try:
            cursor.execute("DELETE FROM calls WHERE номерУрока = ?", (int(idOfLesson.get())))
            connection.commit()
        except:
            mb(title="Ошибка!", message="При удалении звонка произошла ошибка!", icon="cancel")
        else:
            mb(title="Успешно!", message="Звонок удален из расписания!", icon="check")

    def expToExcelCalls():
        try:
            data = pd.read_sql("SELECT * FROM calls", connection)
            data.to_excel("звонки.xlsx", index=False)
        except:
            mb(title="Ошибка!", message="При экспорте произошла ошибка!", icon="cancel")
        else:
            mb(title="Успешно!", message="Звонки экспортированы в звонки.xlsx", icon="check")
    
    def expToHTMLCalls():
        try:
            data = pd.read_sql("SELECT * FROM calls", connection)
            data.to_html("звонки.html", index=False)
        except:
            mb(title="Ошибка!", message="При экспорте произошла ошибка!", icon="cancel")
        else:
            mb(title="Успешно!", message="Звонки экспортированы в звонки.html", icon="check")

    idOfLesson = ct.CTkEntry(callsr, placeholder_text="№", width=30)
    idOfLesson.place(x=0, y=25)

    timeOfLesson = ct.CTkEntry(callsr, placeholder_text="Время проведения", width=180)
    timeOfLesson.place(x=30, y=25)

    addLesson = ct.CTkButton(callsr, text="+", width=30, command=addCall)
    addLesson.place(x=210, y=25)

    remLesson = ct.CTkButton(callsr, text="-", width=30, command=remCall)
    remLesson.place(x=240, y=25)

    checkCallsSchedule = ct.CTkButton(callsr, text="Просмотреть расписание звонков", command=checkCalls)
    checkCallsSchedule.place(y=55)

    expToExcel = ct.CTkButton(callsr, text="Экспорт в MS Excel", command=expToExcelCalls).place(y=85)
    expToHTML = ct.CTkButton(callsr, text="Экспорт в HTML", command=expToHTMLCalls).place(x=140, y=85)

    callsr.mainloop()

def createDayFunc():
    global dayName
    try:
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {dayName.get().lower()} (
                       № INTEGER,
                       Время TEXT,
                       Предмет TEXT,
                       Учитель TEXT,
                       Кабинет TEXT
            )""")
    except sqlite3.OperationalError:
        mb(title="Ошибка!", message="Ошибка могла возникнуть при:\n1.Неправильном заполнении имени дня\n2. Создание уже существующего дня", icon="cancel")
    else:
        mb(message="День был успешно создан", icon="check", option_1="Отлично!")

def delDay():
        global dayName
        try:
            cursor.execute(f"""DROP TABLE {dayName.get().lower()}""")
            connection.commit()
        except sqlite3.OperationalError:
            mb(title="Ошибка!", message="Ошибка могла возникнуть при удалении несуществующего дня", icon="cancel")
        else:
            mb(message="День был успешно удалён!", icon="check", option_1="Отлично!")

def operationsWithDay():
        global dayName, cabinets, teachers, calls
   
        addNewLesson = ct.CTk()
        addNewLesson.title("Добавление нового урока")
        addNewLesson.geometry("750x150")

        cursor.execute(f"SELECT * FROM {dayName.get().lower()}")
        lessons = cursor.fetchall()

        tip = ct.CTkLabel(addNewLesson, text="Добавление нового урока", font=("Arial", 18, "bold"))
        tip.place(x=0, y=0)

        idOfLesson = ct.CTkEntry(addNewLesson, placeholder_text="№", width=30)
        idOfLesson.place(x=0, y=25)

        nameOfLesson = ct.CTkEntry(addNewLesson, placeholder_text="Введите название предмета", width=190)
        nameOfLesson.place(x=30, y=25)

        

        def add():
            try:
                cursor.execute(f"INSERT INTO {dayName.get().lower()} (№, Время, Предмет, Учитель, Кабинет) VALUES (?, ?, ?, ?, ?)", (int(idOfLesson.get()), timeOfLesson.get(), nameOfLesson.get(), teacherLesson.get(), classLesson.get(),))
                connection.commit()
            except:
                mb(title="Ошибка!", message="Проверьте правильность заполнения формы!", icon="cancel")
            else:
                mb(message="Урок был успешно добавлен!", icon="check", option_1="Отлично!")
                idOfLesson.delete(0, ct.END)
                nameOfLesson.delete(0, ct.END)
                timeOfLesson.delete(0, ct.END)

        def rem():
            try:
                cursor.execute(f"DELETE FROM {dayName.get().lower()} WHERE № = ?", (int(idOfLesson.get()),))
                connection.commit()
            except:
                mb(title="Ошибка!", message="Проверьте правильность заполнения формы!", icon="cancel")
            else:
                cursor.execute(f"SELECT * from {dayName.get().lower()}")
                mb(message="Урок был успешно удалён!", icon="check", option_1="Отлично!")

        def window():
            try:
                cursor.execute(f"INSERT INTO {dayName.get().lower()} (№, Время, Предмет, Учитель) VALUES (?, ?, ?, ?)", (int(idOfLesson.get()), "Нет", "урока", " ",))
                connection.commit()
            except:
                mb(title="Ошибка!", message="Проверьте правильность заполнения формы!", icon="cancel")
            else:
                mb(message="В расписании установлено окно!", icon="check", option_1="Отлично!")

        timeOfLesson = ct.CTkComboBox(addNewLesson, values=calls, width=180)
        timeOfLesson.place(x=220, y=25)
        timeOfLesson.set("Выберите урок")

        teacherLesson = ct.CTkComboBox(addNewLesson, values=teachers, width=160)
        teacherLesson.place(x=400, y=25)
        teacherLesson.set("Выберите учителя")

        classLesson = ct.CTkComboBox(addNewLesson, values=cabinets, width=160)
        classLesson.place(x=560, y=25)
        classLesson.set("Выберите кабинет")

        addLesson = ct.CTkButton(addNewLesson, text="+", width=20, command=add)
        addLesson.place(x=0, y=55)

        remLesson = ct.CTkButton(addNewLesson, text="-", width=20, command=rem)
        remLesson.place(x=20, y=55)

        windowLesson = ct.CTkButton(addNewLesson, text="Окно", width=50, command=window)
        windowLesson.place(x=40, y=55)

        openDayTimetable = ct.CTkButton(addNewLesson, text="Открыть расписание дня", command=checktt)
        openDayTimetable.place(y=80)

        if lessons == []:
            mb(title="Предупреждение!", message="В данном дне отстутствуют уроки. Время для их добавления!", icon="warning")

        addNewLesson.mainloop()
        mb(title="Ошибка!", message="Произошла ошибка при открытии! Проверьте существование дня!", icon="cancel")
    

def checktt():
    global dayName

    if not activated:
        ad = mb(title="Реклама", message="Заходите в ВК автора!", option_1="Перейти", cancel_button="None")
        if ad.get() == "Перейти":
            wb.open_new_tab(linkForAds)

    cursor.execute(f"SELECT * FROM {dayName.get().lower()}")
    timetable = cursor.fetchall()

    if timetable == []:
        mb(title="Ошибка!", message="Данный день не содержит в себе уроков!", icon="cancel")
        return
    else:
        timetablescr = ct.CTk()
        timetablescr.title(f"Расписание за {dayName.get().lower()}")

        table = CTkTable(master=timetablescr, column=5, values=timetable)
        table.pack()

        timetablescr.mainloop()

def expToExcel():
    global dayName
    if activated:
        try:
            data = pd.read_sql(f"SELECT * FROM {dayName.get().lower()}", connection)
            data.to_excel(f"{dayName.get()}.xlsx", index=False)
        except:
            mb(title="Ошибка!", message="Произошла ошибка! Проверьте существование дня в вашем расписании!", icon="cancel")
        else:
            mb(title="Экспортировано в Excel", message=f"Расписание за {dayName.get().lower()} было экспортировано в файл {dayName.get()}.xlsx.", icon="check", option_1="Отлично!")
    else:
        mb(title="Ошибка!", message="Активируйте лицензию!", icon="cancel")

def expToHTML():
    global dayName
    if activated:
        try:
            data = pd.read_sql(f"SELECT * FROM {dayName.get().lower()}", connection)
            data.to_html(f"{dayName.get()}.html", index=False)
        except:
            mb(title="Ошибка!", message="Произошла ошибка! Проверьте существование дня в вашем расписании!", icon="cancel")
        else:
            mb(title="Экспортировано в Excel", message=f"Расписание за {dayName.get().lower()} было экспортировано в файл {dayName.get()}.html.", icon="check", option_1="Отлично!")
    else:
        mb(title="Ошибка!", message="Активируйте лицензию!", icon="cancel")

def expTocsv():
    global dayName
    if activated:
        try:
            data = pd.read_sql(f"SELECT * FROM {dayName.get().lower()}", connection)
            data.to_csv(f"{dayName.get()}.csv", index=False)
        except:
            mb(title="Ошибка!", message="Произошла ошибка! Проверьте существование дня в вашем расписании!", icon="cancel")
        else:
            mb(title="Экспортировано в CSV", message=f"Расписание за {dayName.get().lower()} было экспортировано в файл {dayName.get()}.csv.", icon="check", option_1="Отлично!")
    else:
        mb(title="Ошибка!", message="Активируйте лицензию!", icon="cancel")

def copyTimetable():
    if activated:
        global dayName
        try:
            data = pd.read_sql(f"SELECT * FROM {dayName.get().lower()}", connection)
            data.to_clipboard(index=False)
        except:
            mb(title="Ошибка!", message="Произошла ошибка! Проверьте существование дня в вашем расписании!", icon="cancel")
        else:
            mb(title="Скопировано", message=f"Расписание за {dayName.get().lower()} было скопировано. Вы можете вставить расписание в \"Блокнот\"", icon="check", option_1="Отлично!")
    else:
        mb(title="Ошибка!", message="Активируйте лицензию!", icon="cancel")

def activateLic():
    global key, activated
    if not activated:
        keycurs.execute("SELECT * FROM keys")
        keysList = keycurs.fetchall()

        keysOneList = []
        for i in range(len(keysList)):
            for y in range(len(keysList[i])):
                keysOneList.append(keysList[i][y])

        if key.get() in keysOneList:  
            activated = True
            mb(title="Лицензия активирована!", message="Лицензия была успешно активирована!\nТеперь вам доступен экспорт и просмотр расписания!", icon="check", option_1="Отлично!")
        else:
            mb(title="Ошибка!", message="Произошла ошибка! Проверьте наличие установленной актуальной БД ключей или правильность ключа!", icon="cancel")
    else:
        mb(title="Ошибка!", message="Ваша лицензия уже активирована!", icon="cancel")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
               nameOfClass TEXT
    )
""")
connection.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    (
               teacher TEXT
    )
""")
connection.commit()

cursor.execute("SELECT * FROM classes")
cabinetsWithoutFilter = cursor.fetchall()
cabinets = []

for x in range(len(cabinetsWithoutFilter)):
    for y in range(len(cabinetsWithoutFilter[x])):
        cabinets.append(cabinetsWithoutFilter[x][y])

cursor.execute("SELECT * FROM teachers")
teachersWithoutFilter = cursor.fetchall()
teachers = []

for x in range(len(teachersWithoutFilter)):
    for y in range(len(teachersWithoutFilter[x])):
        teachers.append(teachersWithoutFilter[x][y])

cursor.execute("SELECT * FROM calls")
callsWithoutFilter = cursor.fetchall()
calls = []

for x in range(len(callsWithoutFilter)):
    calls.append(str(callsWithoutFilter[x]).replace("(","").replace(")","").replace("'", "").replace(",",":"))

print(calls)

def addCabinet():
    global cabinets

    if not activated:
        ad = mb(title="Реклама", message="Заходите в ВК автора!", option_1="Перейти", cancel_button="None")
        if ad.get() == "Перейти":
            wb.open_new_tab(linkForAds)

    cabMan = ct.CTk()
    cabMan.title("Менеджер кабинетов")
    cabMan.resizable(False, False)
    cabMan.geometry("550x150")

    tip = ct.CTkLabel(cabMan, text="Добавление кабинета", font=("Arial", 15, "bold"))
    tip.place(x=0, y=0)

    def showCabinets():
        sc = ct.CTk()
        sc.title("Все кабинеты")
        sc.resizable(False, False)

        cursor.execute("SELECT * FROM classes")
        table = CTkTable(sc, column=1, values=cursor.fetchall())
        table.pack()

        sc.mainloop()

    def addCab():
        if not activated:
            ad = mb(title="Реклама", message="Заходите в ВК автора!", option_1="Перейти")
            if ad.get() == "Перейти":
                wb.open_new_tab(linkForAds)
        try:
            cabinets.append(nameOfCab.get())
            cursor.execute("INSERT INTO classes (nameOfClass) VALUES (?)", (nameOfCab.get(),))
            connection.commit()
        except:
            mb(title="Ошибка!", message="Произошла ошибка при добавлении кабинета! Проверьте правильность введённых данных!", icon="cancel")
        else:
            mb(title="Добавлено!", message="Кабинет был добавлен!", icon="check")
    
    def remCab():
        if not activated:
            ad = mb(title="Реклама", message="Заходите в ВК автора!", option_1="Перейти")
            if ad.get() == "Перейти":
                wb.open_new_tab(linkForAds)
        try:
            cabinets.remove(nameOfCab.get())
            cursor.execute("DELETE FROM classes WHERE nameOfClass = ?", (nameOfCab.get(),))
            connection.commit()
        except:
            mb(title="Ошибка!", message="Произошла ошибка при удалении кабинета! Проверьте правильность введённых данных!", icon="cancel")
        else:
            mb(title="Удалено!", message="Кабинет был удален!", icon="check")

    nameOfCab = ct.CTkEntry(cabMan, placeholder_text="Введите название кабинета", width=180)
    nameOfCab.place(x=0,y=25)

    addCabButton = ct.CTkButton(cabMan, text="+", width=20, command=addCab).place(x=180, y=25)
    remCabButton = ct.CTkButton(cabMan, text="-", width=20, command=remCab).place(x=200, y=25)

    showTeachersBtn = ct.CTkButton(cabMan, text="Показать кабинеты", command=showCabinets).place(x=0, y=55)
    
    cabMan.mainloop()

def addTeacher():
    global teachers

    if not activated:
        ad = mb(title="Реклама", message="Заходите в ВК автора!", option_1="Перейти", cancel_button="None")
        if ad.get() == "Перейти":
            wb.open_new_tab(linkForAds)

    teachMan = ct.CTk()
    teachMan.title("Менеджер учителей")
    teachMan.resizable(False, False)
    teachMan.geometry("550x110")

    def showTeachers():
        st = ct.CTk()
        st.title("Все учителя")
        st.resizable(False, False)

        cursor.execute("SELECT * FROM teachers")
        table = CTkTable(st, column=1, values=cursor.fetchall())
        table.pack()

        st.mainloop()

    def addTeacherToDB():
        try:
            teachers.append(nameOfTeacher.get())
            cursor.execute("INSERT INTO teachers (teacher) VALUES (?)", (nameOfTeacher.get(),))
            connection.commit()
        except:
            mb(title="Ошибка!", message="Произошла ошибка при добавлении учителя! Проверьте правильность введённых данных!", icon="cancel")
        else:
            mb(title="Добавлено!", message="Учитель был добавлен!", icon="check")
    
    def remTeacher():
        try:
            teachers.remove(nameOfTeacher.get())
            cursor.execute("DELETE FROM teachers WHERE teacher = ?", (nameOfTeacher.get(),))
            connection.commit()
        except:
            mb(title="Ошибка!", message="Произошла ошибка при удалении учителя! Проверьте правильность введённых данных!", icon="cancel")
        else:
            mb(title="Удалено!", message="Учитель был удален!", icon="check")

    tip = ct.CTkLabel(teachMan, text="Добавление учителя", font=("Arial", 15, "bold"))
    tip.place(x=0, y=0)

    nameOfTeacher = ct.CTkEntry(teachMan, placeholder_text="Введите название кабинета", width=180)
    nameOfTeacher.place(x=0,y=25)

    addTeacherButton = ct.CTkButton(teachMan, text="+", width=20, command=addTeacherToDB).place(x=180, y=25)
    remTeacherButton = ct.CTkButton(teachMan, text="-", width=20, command=remTeacher).place(x=200, y=25)

    showTeachersBtn = ct.CTkButton(teachMan, text="Показать учителей", command=showTeachers).place(x=0, y=55)
    teachMan.mainloop()

def publishTimetable():
    if activated:
        pub = ct.CTk()
        pub.title("Публикация расписания")
        pub.resizable(False, False)
        pub.geometry("300x100")

        urlOfTimetable = ct.CTkEntry(pub, placeholder_text="Введите POST-страницу сайта для публикации")
        urlOfTimetable.pack(fill="x")

        nameOfFile = ct.CTkEntry(pub, placeholder_text="Введите название .html файла с расписанием")
        nameOfFile.pack(fill="x")

        def publish():
            timetable = open(nameOfFile.get(), 'rb')
            url = urlOfTimetable.get()
            files = {nameOfFile.get() : timetable}
            publ = requests.post(url, files=files)
            timetable.close()
            print(publ.text)

        publButton = ct.CTkButton(pub, text="Опубликовать", command=publish).pack(fill="x")

        pub.mainloop()

def checkTimetableByTeacher():
    day = dayName.get()
    teacher = ""

    selTeach = ct.CTk()
    selTeach.title("Просмотр расписания")

    def showTT():
        teacher = teacherName.get()
        cursor.execute(f"SELECT №, Время, Предмет, Кабинет FROM {day} WHERE Учитель = ?", (teacher,))
        tt = CTkTable(selTeach, values=cursor.fetchall()).grid(rowspan = 4, row=1, column=0)
    
    teacherName = ct.CTkComboBox(selTeach, values=teachers)
    teacherName.grid(row=0, column=0)

    showTimetable = ct.CTkButton(selTeach, text="Показать", width=100, command=showTT).grid(row=0, column=1)

    selTeach.mainloop()

dayName = ct.CTkComboBox(root, values=days, width=170)
dayName.place(x=125,y=0)

tip = ct.CTkLabel(root, text="Перед созданием расписания", font=("Arial", 15, "bold")).place(y=28)
addClass = ct.CTkButton(root, text="Добавить кабинеты", command=addCabinet, width=210).place(y=56)
addTeachers = ct.CTkButton(root, text="Добавить учителей", command=addTeacher, width=210).place(y=84)

tip = ct.CTkLabel(root, text="Работа с расписанием", font=("Arial", 15, "bold")).place(x=250, y=28)
checkTtByTeacher = ct.CTkButton(root, text="Просмотр расписания учителя", width=210, command=checkTimetableByTeacher).place(x=250, y=56)
openDay = ct.CTkButton(root, text="Изменить расписание на день", command=operationsWithDay, width=210).place(x=250, y=84)
callsScheduleB = ct.CTkButton(root, text="Расписание звонков", command=callsSchedule, width=210).place(x=250, y=112)
checkTimeTable = ct.CTkButton(root, text="Посмотреть расписание", command=checktt, width=210).place(x=250, y=140)

tip = ct.CTkLabel(root, text="Экспорт расписания", font=("Arial", 15, "bold")).place(x=0, y=200)
exportToExcel = ct.CTkButton(root, text="Экспорт в MS Excel", command=expToExcel, width=210).place(x=0, y=228)
exportToHTML = ct.CTkButton(root, text="Экспорт в HTML", command=expToHTML, width=210).place(x=0, y=256)
copyTT = ct.CTkButton(root, text="Скопировать в буфер обмена", command=copyTimetable, width=210).place(x=0, y=284)
exportToCSV = ct.CTkButton(root, text="Экспорт в CSV", command=expTocsv, width=210).place(x=0, y=312)
publisToSite = ct.CTkButton(root, text="Опубликовать на сайт", command=publishTimetable, width=210).place(x=0, y=340)

tip = ct.CTkLabel(root, text="Активация лицензии", font=("Arial", 15, "bold")).place(x=250, y=200)
key = ct.CTkEntry(root, placeholder_text="Введите ключ", width=210)
key.place(x=250, y=228)
freeKey = ct.CTkButton(root, text="Бесплатный ключ (только win)", command=lambda : os.system("start прочее/ключиАктивации.xlsx"), width=210).place(x=250, y=256)
activateBtn = ct.CTkButton(root, text="Активировать", width=210, command=activateLic).place(x=250, y=284)

menu = Menu(root)
menu.add_command(label="О разработчике", command=lambda : wb.open("https://github.com/timursper-apps"))

root.config(menu=menu)
root.mainloop()

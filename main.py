"""
ЕСЛИ В БД timetable ОТСУТСТВУЮТ ТАБЛИЦЫ понедельник, вторник, среда, ..., суббота, то требуется их создать:

№ INTEGER, Время TEXT, Предмет TEXT, Учитель TEXT, Кабинет TEXT
"""
import sqlite3, customtkinter as ct, pandas as pd, webbrowser as wb
from CTkMessagebox import CTkMessagebox as mb
from CTkTable import *
from tkinter import *
import config as cfg
version = "1.5"

activated = True

connection = sqlite3.connect("data/timetable.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS calls (
        номерУрока INTEGER,
        время TEXT          
    )
""")
connection.commit()

root = ct.CTk()
root.title(f"ИС «Школьное Расписание». v{version} ({cfg.schoolName})")
root.geometry("460x350")
root.resizable(False, False)
#pws.apply_style(root, "aero")

days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']

def callsSchedule():
    callsr = ct.CTk()
    callsr.title("Менеджер расписания звонков")
    callsr.geometry("550x150")
    callsr.resizable(False, False)

    tip = ct.CTkLabel(callsr, text="Добавление нового звонка", font=("Arial", 18, "bold"))
    tip.place(x=0, y=0)

    def addCall():
        try:
            cursor.execute("INSERT INTO calls (время) VALUES (?)", (timeOfLesson.get(),))
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

        table = CTkTable(callstt, column=1, values=callsttvalue, write=True)
        table.pack()

        callstt.mainloop()
    
    def remCall():
        try:
            cursor.execute("DELETE FROM calls WHERE время = ?", (timeOfLesson.get()))
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

    timeOfLesson = ct.CTkEntry(callsr, placeholder_text="Время проведения", width=180)
    timeOfLesson.place(x=0, y=25)

    addLesson = ct.CTkButton(callsr, text="+", width=30, command=addCall)
    addLesson.place(x=180, y=25)

    remLesson = ct.CTkButton(callsr, text="-", width=30, command=remCall)
    remLesson.place(x=210, y=25)

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

def checktt():
    global dayName

    

    cursor.execute(f"SELECT * FROM {dayName.get().lower()} ORDER BY № ASC")
    timetable = cursor.fetchall()

    if timetable == []:
        mb(title="Ошибка!", message="Данный день не содержит в себе уроков!", icon="cancel")
        return
    else:
        timetablescr = ct.CTk()
        timetablescr.title(f"Расписание на {dayName.get().lower()}")

        table = CTkTable(master=timetablescr, column=5, values=timetable)
        table.pack()

        timetablescr.mainloop()

def expToExcel():
    global dayName
    if activated:
        try:
            data = pd.read_sql(f"SELECT * FROM {dayName.get().lower()} ORDER BY № ASC", connection)
            data[3] = f"Составлено при помощи «УСОБ. Расписание {version}»"
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
            data = pd.read_sql(f"SELECT * FROM {dayName.get().lower()} ORDER BY № ASC", connection)
            data.to_html(f"{dayName.get()}.html", index=False)

            htmlreport = open(f"{dayName.get()}.html", "r", encoding="utf-8")
            file = htmlreport.read()
            file += f"<hr>Составлено при помощи <a href='https://yop.my1.ru/timetable.html'>«УСОБ. Расписание {version}»</a>"
            file = file.replace("<table", "<div contenteditable='true'><table").replace("</table>", "</table></div>")
            htmlreport.close()

            htmlrep = open(f"{dayName.get()}.html", "w", encoding="utf-8")
            htmlrep.write(file)
            htmlrep.close()
        except:
            mb(title="Ошибка!", message="Произошла ошибка! Проверьте существование дня в вашем расписании!", icon="cancel")
        else:
            mb(title="Экспортировано в HTML", message=f"Расписание за {dayName.get().lower()} было экспортировано в файл {dayName.get()}.html.", icon="check", option_1="Отлично!")
    else:
        mb(title="Ошибка!", message="Активируйте лицензию!", icon="cancel")

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
    calls.append(str(callsWithoutFilter[x]).replace("(","").replace(")","").replace("'", "").replace(",",""))

print(calls)

cursor.execute("""CREATE TABLE IF NOT EXISTS lessons (
                    предмет TEXT
               )
               """)
connection.commit()

cursor.execute("SELECT * FROM lessons")
lessonsWithoutFilter = cursor.fetchall()
lessons = []

if lessonsWithoutFilter != []:
    for x in range(len(lessonsWithoutFilter)):
        for y in range(len(lessonsWithoutFilter[x])):
            lessons.append(lessonsWithoutFilter[x][y])

def addCabinet():
    global cabinets

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
        try:
            cabinets.append(nameOfCab.get())
            cursor.execute("INSERT INTO classes (nameOfClass) VALUES (?)", (nameOfCab.get(),))
            connection.commit()
        except:
            mb(title="Ошибка!", message="Произошла ошибка при добавлении кабинета! Проверьте правильность введённых данных!", icon="cancel")
        else:
            mb(title="Добавлено!", message="Кабинет был добавлен!", icon="check")
    
    def remCab():
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

def addLesson():
    global lessons

    lessonMaster = ct.CTk()
    lessonMaster.title("Добавление предметов")
    lessonMaster.geometry("360x56")
    lessonMaster.resizable(False, False)
    
    def add():
        try:
            cursor.execute("INSERT INTO lessons(Предмет) VALUES (?)", (name.get(),))
            connection.commit()

            lessons.append(name.get())
        except:
            mb(title="Ошибка!", message="Во время добавления предмета произошла неизвестная ошибка", icon="cancel")
        else:
            mb(title="Готово!", message="Предмет добавлен в БД!", icon="check")
    def rem():
        try:
            cursor.execute("INSERT INTO lessons (предмет) VALUES (?)", (name.get(),))
            connection.commit()
            lessons.remove(name.get())
        except:
            mb(title="Ошибка!", message="Во время удаления предмета произошла неизвестная ошибка", icon="cancel")
        else:
            mb(title="Готово!", message="Предмет удален из БД!", icon="check")

    def checkLessons():
        cl = ct.CTk()
        
        for l in lessons:
            lesson = ct.CTkEntry(cl)
            lesson.pack()
            lesson.insert(END, l)

        cl.mainloop()

    def exp(format: str):
        df = pd.DataFrame(lessons)
        try:
            if format == "xlsx":
                df.to_excel(f"предметы.xlsx")
            else:
                df.to_html(f"предметы.html")
        except:
            mb(title="Ошибка!", message="Произошла неизвестная ошибка при сохранении отчёта", icon="cancel")
        else:
            mb(title="Успешно!", message=f"Отчёт сохранён в файле предметы.{format}")

    name = ct.CTkEntry(lessonMaster, placeholder_text="Название предмета", width=180)
    name.place(x=0, y=0)

    addBtn = ct.CTkButton(lessonMaster, text="+", width=20, command=add).place(x=180, y=0)
    remBtn = ct.CTkButton(lessonMaster, text="-", width=20, command=rem).place(x=200, y=0)
    lessonsBtn = ct.CTkButton(lessonMaster, text="Все предметы", command=checkLessons).place(x=220, y=0)

    exportToExc = ct.CTkButton(lessonMaster, text="Экспорт в MS Excel", command=lambda form = "xlsx" : exp(form)).place(x=0, y=28)
    exportToHtml = ct.CTkButton(lessonMaster, text="Экспорт в HTML", command=lambda form = "html" : exp(form)).place(x=140, y=28)

    lessonMaster.mainloop()

def operationsWithDay():
        global dayName, cabinets, teachers, calls, lessons
   
        addNewLesson = ct.CTk()
        addNewLesson.title("Добавление нового урока")
        addNewLesson.geometry("750x150")

        cursor.execute(f"SELECT * FROM {dayName.get().lower()}")
        lessons2 = cursor.fetchall()

        def add():
            try:
                cursor.execute(f"INSERT INTO {dayName.get().lower()} (№, Время, Предмет, Учитель, Кабинет) VALUES (?, ?, ?, ?, ?)", (int(idOfLesson.get()), timeOfLesson.get(), nameOfLesson.get(), teacherLesson.get(), classLesson.get(),))
                connection.commit()
            except sqlite3.OperationalError:
                mb(title="Ошибка!", message="Проверьте правильность заполнения формы!", icon="cancel")
            else:
                mb(message="Урок был успешно добавлен!", icon="check", option_1="Отлично!")
                idOfLesson.delete(0, ct.END)

        def rem():
            try:
                cursor.execute(f"DELETE FROM {dayName.get().lower()} WHERE № = ?", (int(idOfLesson.get()),))
                connection.commit()
            except sqlite3.OperationalError:
                mb(title="Ошибка!", message="Проверьте правильность заполнения формы!", icon="cancel")
            else:
                cursor.execute(f"SELECT * from {dayName.get().lower()}")
                mb(message="Урок был успешно удалён!", icon="check", option_1="Отлично!")

        def window():
            try:
                cursor.execute(f"INSERT INTO {dayName.get().lower()} (№, Время, Предмет, Учитель) VALUES (?, ?, ?, ?)", (int(idOfLesson.get()), "Нет", "урока", " ",))
                connection.commit()
            except sqlite3.OperationalError:
                mb(title="Ошибка!", message="Проверьте правильность заполнения формы!", icon="cancel")
            else:
                mb(message="В расписании установлено окно!", icon="check", option_1="Отлично!")

        tip = ct.CTkLabel(addNewLesson, text="Добавление нового урока", font=("Arial", 18, "bold"))
        tip.place(x=0, y=0)

        idOfLesson = ct.CTkEntry(addNewLesson, placeholder_text="№", width=30)
        idOfLesson.place(x=0, y=25)

        nameOfLesson = ct.CTkComboBox(addNewLesson, values=lessons, width=190)
        nameOfLesson.place(x=30, y=25)
        nameOfLesson.set("Выберите предмет")

        timeOfLesson = ct.CTkComboBox(addNewLesson, values=calls, width=180)
        timeOfLesson.place(x=220, y=25)
        timeOfLesson.set("Выберите время проведения")

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

        if lessons2 == []:
            mb(title="Предупреждение!", message="В данном дне отстутствуют уроки. Время для их добавления!", icon="warning")

        addNewLesson.mainloop()

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

def cancelLesson():
    cancelMaster = ct.CTk()
    cancelMaster.title("Отмена уроков")
    cancelMaster.geometry("280x56")

    checkrsp = ct.CTkButton(cancelMaster, text="Посмотреть расписание", command=checktt).place(x=0, y=0)
    
    def cancelfunc():
        try:
            cursor.execute(f"""
            UPDATE {dayName.get()}
            SET Предмет = ?
            WHERE № = ?
            """, ("Урок отменен", int(idLesson.get()),))

            connection.commit()

            cursor.execute(f"""
            UPDATE {dayName.get()}
            SET Учитель = ?
            WHERE № = ?
            """, ("", int(idLesson.get()),))

            connection.commit()

            cursor.execute(f"""
            UPDATE {dayName.get()}
            SET Кабинет = ?
            WHERE № = ?
            """, ("", int(idLesson.get()),))

            connection.commit()
        except:
            mb(title="Ошибка!", message="При отмене урока произошла неизвестная ошибка", icon="cancel")
        else:
            mb(title="Успешно!", message="Вы успешно отменили урок!", icon="check")

    idLesson = ct.CTkEntry(cancelMaster, placeholder_text="№ урока")
    idLesson.place(x=0, y=28)

    cancel = ct.CTkButton(cancelMaster, text="Отменить", command=cancelfunc).place(x=140, y=28)

    cancelMaster.mainloop()

def replaceLesson():
    replaceMaster = ct.CTk()
    replaceMaster.title("Замена уроков")
    replaceMaster.geometry("550x84")

    checkrsp = ct.CTkButton(replaceMaster, text="Посмотреть расписание", command=checktt).place(x=0, y=0)
    
    def replacefunc():
        try:
            cursor.execute(f"""UPDATE {dayName.get()}
                            SET Предмет = ?
                           WHERE № = ?""", (replaceLessonName.get(), idLesson.get()))
            
            connection.commit()

            cursor.execute(f"""UPDATE {dayName.get()}
                            SET Учитель = ?
                           WHERE № = ?""", (teacherLesson.get(), idLesson.get()))
            
            connection.commit()

            cursor.execute(f"""UPDATE {dayName.get()}
                            SET Кабинет = ?
                           WHERE № = ?""", (replaceCabinet.get(), int(idLesson.get())))
            connection.commit()
        except:
            mb(title="Ошибка!", message="При замене урока произошла неизвестная ошибка", icon="cancel")
        else:
            mb(title="Успешно!", message="Вы успешно заменили урок!", icon="check")
            id = int(idLesson.get())
            idLesson.delete(0, END)
            idLesson.insert(END, id + 1)

    lessonsLocal = []

    for lesson in lessons:
        lessonsLocal.append(lesson)

    lessonsLocal.append("Урок отменен")

    idLesson = ct.CTkEntry(replaceMaster, placeholder_text="№", width=50)
    idLesson.place(x=0, y=28)

    teacherLesson = ct.CTkComboBox(replaceMaster, values=teachers, width=180)
    teacherLesson.place(x=50, y=28)
    teacherLesson.set("Замещающий педагог")

    replaceLessonName = ct.CTkComboBox(replaceMaster, values=lessons, width=160)
    replaceLessonName.place(x=230, y=28)
    replaceLessonName.set("Замещающий урок")

    replaceCabinet = ct.CTkComboBox(replaceMaster, values=cabinets, width=160)
    replaceCabinet.place(x=390, y=28)
    replaceCabinet.set("Замещающий класс")

    replace = ct.CTkButton(replaceMaster, text="Заменить", command=replacefunc).place(x=0, y=56)

    replaceMaster.mainloop()

dayName = ct.CTkComboBox(root, values=days, width=170)
dayName.place(x=125,y=0)

tip = ct.CTkLabel(root, text="Перед созданием расписания", font=("Arial", 15, "bold")).place(y=28)
addClass = ct.CTkButton(root, text="Добавить кабинеты", command=addCabinet, width=210).place(y=56)
addTeachers = ct.CTkButton(root, text="Добавить учителей", command=addTeacher, width=210).place(y=84)
addLessons = ct.CTkButton(root, text="Добавить предметы", command=addLesson, width=210).place(y=112)

tip = ct.CTkLabel(root, text="Работа с расписанием", font=("Arial", 15, "bold")).place(x=250, y=28)
checkTtByTeacher = ct.CTkButton(root, text="Просмотр расписания учителя", width=210, command=checkTimetableByTeacher).place(x=250, y=56)
openDay = ct.CTkButton(root, text="Изменить расписание на день", command=operationsWithDay, width=210).place(x=250, y=84)
callsScheduleB = ct.CTkButton(root, text="Расписание звонков", command=callsSchedule, width=210).place(x=250, y=112)
checkTimeTable = ct.CTkButton(root, text="Посмотреть расписание", command=checktt, width=210).place(x=250, y=140)

tip = ct.CTkLabel(root, text="Экспорт расписания", font=("Arial", 15, "bold")).place(x=0, y=200)
exportToExcel = ct.CTkButton(root, text="Экспорт в MS Excel", command=expToExcel, width=210).place(x=0, y=228)
exportToHTML = ct.CTkButton(root, text="Экспорт в HTML", command=expToHTML, width=210).place(x=0, y=256)

tip = ct.CTkLabel(root, text="Замены в расписании", font=("Arial", 15, "bold")).place(x=250, y=200)
cancelLessonB = ct.CTkButton(root, text="Отменить урок", command=cancelLesson, width=210).place(x=250, y=228)
replaceLessonB = ct.CTkButton(root, text="Заменить урок", command=replaceLesson, width=210).place(x=250, y=256)

if __name__ == "__main__":
    supportAuthor = mb(root, title="Поддержите орган", message=f"Переходите в сообщество {cfg.organName}", option_1="Перейти", cancel_button="None")

    if supportAuthor.get() == "Перейти":
        wb.open(cfg.organLink)

    root.mainloop()

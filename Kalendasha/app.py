from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime, timedelta
import calendar
import pytz
import uuid

app = Flask(__name__)

DATA_FILE = "data/students.json"
DATA_SLOTS_FILE = "data/slots.json"
TEMPLATE_WEEK_FILE = "data/template_week.json"
DATA_PAYMENTS_FILE = "data/payments.json"
DATA_BALANCES_FILE = "data/balances.json"
DATA_TRIAL_STUDENTS_FILE = "data/trial_students.json"

# Словарь часовых поясов
TIMEZONE_MAPPING = {
    'КЛД': 'Europe/Kaliningrad',
    'МСК': 'Europe/Moscow',
    'МСК+1': 'Europe/Samara',
    'ЕКБ': 'Asia/Yekaterinburg',
    'ОМС': 'Asia/Omsk',
    'НСК': 'Asia/Novosibirsk',
    'ИРК': 'Asia/Irkutsk',
    'ЯКТ': 'Asia/Yakutsk',
    'ВЛД': 'Asia/Vladivostok',
    'МГД': 'Asia/Magadan',
    'КАМ': 'Asia/Kamchatka',
    'КРД': 'Europe/Moscow',
    'КЗН': 'Europe/Moscow',
    'UTC+0': 'UTC',
    'UTC+1': 'Etc/GMT-1',
    'UTC+2': 'Etc/GMT-2',
    'UTC+3': 'Etc/GMT-3',
    'UTC+4': 'Etc/GMT-4',
    'UTC+5': 'Etc/GMT-5',
    'UTC+6': 'Etc/GMT-6',
    'UTC+7': 'Etc/GMT-7',
    'UTC+8': 'Etc/GMT-8',
    'UTC+9': 'Etc/GMT-9',
    'UTC+10': 'Etc/GMT-10',
    'UTC+11': 'Etc/GMT-11',
    'UTC+12': 'Etc/GMT-12'
}

# Функции для пробных учеников
def load_trial_students():
    try:
        if not os.path.exists(DATA_TRIAL_STUDENTS_FILE):
            return []
        with open(DATA_TRIAL_STUDENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_trial_students(trial_students):
    try:
        os.makedirs("data", exist_ok=True)
        with open(DATA_TRIAL_STUDENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(trial_students, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении пробных учеников: {e}")

# Функции для учеников
def load_students():
    try:
        if not os.path.exists(DATA_FILE):
            return []
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_students(students):
    try:
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(students, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении учеников: {e}")

# Функции для слотов (расписание)
def load_slots():
    try:
        if not os.path.exists(DATA_SLOTS_FILE):
            return []
        with open(DATA_SLOTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_slots(slots):
    try:
        os.makedirs("data", exist_ok=True)
        with open(DATA_SLOTS_FILE, "w", encoding="utf-8") as f:
            json.dump(slots, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении слотов: {e}")

# Функции для шаблона недели
def load_template_week():
    try:
        if not os.path.exists(TEMPLATE_WEEK_FILE):
            return []
        with open(TEMPLATE_WEEK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_template_week(template):
    try:
        os.makedirs("data", exist_ok=True)
        with open(TEMPLATE_WEEK_FILE, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении шаблона недели: {e}")

# Функции для работы с оплатами
def load_payments():
    try:
        if not os.path.exists(DATA_PAYMENTS_FILE):
            return []
        with open(DATA_PAYMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_payments(payments):
    try:
        os.makedirs("data", exist_ok=True)
        with open(DATA_PAYMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(payments, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении платежей: {e}")

def load_balances():
    try:
        if not os.path.exists(DATA_BALANCES_FILE):
            return {}
        with open(DATA_BALANCES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_balances(balances):
    try:
        os.makedirs("data", exist_ok=True)
        with open(DATA_BALANCES_FILE, "w", encoding="utf-8") as f:
            json.dump(balances, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении балансов: {e}")

# Функции для работы с часовыми поясами
def convert_time_for_user(time_str, from_timezone='МСК', to_timezone='МСК'):
    """Конвертирует время между часовыми поясами"""
    try:
        # Парсим время
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        # Создаем datetime объект с произвольной датой
        today = datetime.now().date()
        dt = datetime.combine(today, time_obj)
        
        # Получаем часовые пояса
        from_tz = pytz.timezone(TIMEZONE_MAPPING.get(from_timezone, 'Europe/Moscow'))
        to_tz = pytz.timezone(TIMEZONE_MAPPING.get(to_timezone, 'Europe/Moscow'))
        
        # Локализуем время исходного пояса
        dt_localized = from_tz.localize(dt)
        
        # Конвертируем в целевой пояс
        dt_converted = dt_localized.astimezone(to_tz)
        
        return dt_converted.strftime('%H:%M')
    except Exception as e:
        print(f"Ошибка конвертации времени: {e}")
        return time_str

# НОВАЯ ФУНКЦИЯ - проверка пересечения уроков с учетом длительности
def check_time_conflicts(slots):
    """Проверяет пересечения уроков с учетом их длительности"""
    conflicts = set()
    
    # Группируем уроки по датам
    lessons_by_date = {}
    for slot in slots:
        date_key = slot.get('date', 'template')
        if date_key not in lessons_by_date:
            lessons_by_date[date_key] = []
        lessons_by_date[date_key].append(slot)
    
    # Проверяем каждую дату
    for date_key, date_lessons in lessons_by_date.items():
        for i, lesson1 in enumerate(date_lessons):
            for j, lesson2 in enumerate(date_lessons):
                if i >= j:  # Избегаем дублирования проверок
                    continue
                
                # Получаем время начала и длительность
                time1_str = lesson1['time']
                time2_str = lesson2['time']
                duration1 = lesson1.get('lesson_duration', 60)
                duration2 = lesson2.get('lesson_duration', 60)
                
                # Конвертируем в минуты от начала дня
                time1_minutes = time_to_minutes(time1_str)
                time2_minutes = time_to_minutes(time2_str)
                
                # Вычисляем время окончания
                end1_minutes = time1_minutes + duration1
                end2_minutes = time2_minutes + duration2
                
                # Проверяем пересечение (не касание)
                if (time1_minutes < end2_minutes and time2_minutes < end1_minutes):
                    # Исключаем случай точного стыка
                    if not (end1_minutes == time2_minutes or end2_minutes == time1_minutes):
                        conflicts.add(lesson1.get('id'))
                        conflicts.add(lesson2.get('id'))
    
    return conflicts

def time_to_minutes(time_str):
    """Конвертирует время в минуты от начала дня"""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    except:
        return 0

# Функции для месячного календаря
def get_month_calendar(year, month):
    """Получить календарь месяца с полными датами"""
    cal = calendar.monthcalendar(year, month)
    month_data = []
    
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                date_obj = datetime(year, month, day)
                week_data.append({
                    'day': day,
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'display_date': date_obj.strftime('%d.%m'),
                    'weekday': date_obj.strftime('%A'),
                    'weekday_ru': get_weekday_ru(date_obj.weekday()),
                    'is_today': date_obj.date() == datetime.now().date()
                })
        month_data.append(week_data)
    
    return month_data

def get_week_dates(year, week_number):
    """Получить даты для конкретной недели"""
    # ИСПРАВЛЯЕМ: Правильно вычисляем первый день недели
    # Создаем дату для 4 января указанного года (это всегда в первой неделе ISO)
    jan_4 = datetime(year, 1, 4)
    
    # Находим понедельник первой недели
    first_monday = jan_4 - timedelta(days=jan_4.weekday())
    
    # Находим нужную неделю
    target_week_start = first_monday + timedelta(weeks=week_number - 1)
    
    week_dates = []
    days_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    for i in range(7):
        date = target_week_start + timedelta(days=i)
        week_dates.append({
            "date": date.strftime("%d.%m"),
            "full_date": date.strftime("%Y-%m-%d"),
            "day_name": days_names[i],
            "day_short": date.strftime("%a"),
            "is_today": date.date() == datetime.now().date()
        })
    
    return week_dates
def get_current_week_number():
    """Получить номер текущей недели"""
    today = datetime.now()
    return today.isocalendar()[1]

def get_weekday_ru(weekday_num):
    """Конвертация номера дня недели в русское название"""
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    return days[weekday_num]

def get_lessons_for_date(date_str, slots):
    """Получить все занятия для конкретной даты"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekday_ru = get_weekday_ru(date_obj.weekday())
    
    lessons = []
    for slot in slots:
        # Проверяем разовые занятия с конкретной датой
        if slot.get('date') == date_str:
            lessons.append(slot)
        # Проверяем регулярные занятия по дням недели (без конкретной даты)
        elif not slot.get('date') and slot['day'] == weekday_ru:
            lessons.append(slot)
    
    # Сортируем по времени
    lessons.sort(key=lambda x: x['time'])
    return lessons

def get_student_lessons_for_date(date_str, slots, student_name, user_timezone='МСК'):
    """Получить занятия ученика для конкретной даты с конвертацией времени"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekday_ru = get_weekday_ru(date_obj.weekday())
    
    lessons = []
    for slot in slots:
        if slot['student'] != student_name:
            continue
            
        # Проверяем разовые занятия с конкретной датой
        if slot.get('date') == date_str:
            converted_time = convert_time_for_user(slot['time'], 'МСК', user_timezone)
            lessons.append({
                'time': converted_time,
                'subject': slot.get('subject', 'Урок'),
                'status': slot.get('status', 'scheduled')
            })
        # Проверяем регулярные занятия по дням недели (без конкретной даты)
        elif not slot.get('date') and slot['day'] == weekday_ru:
            converted_time = convert_time_for_user(slot['time'], 'МСК', user_timezone)
            lessons.append({
                'time': converted_time,
                'subject': slot.get('subject', 'Урок'),
                'status': slot.get('status', 'scheduled')
            })
    
    # Сортируем по времени
    lessons.sort(key=lambda x: x['time'])
    return lessons

def get_student_week_schedule(student_name, user_timezone='МСК'):
    """Получить недельное расписание для ученика (для виджета)"""
    slots = load_slots()
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    # Группируем по времени с учетом часового пояса
    times_converted = {}
    for slot in slots:
        if slot['student'] != student_name:
            continue
            
        original_time = slot['time']
        converted_time = convert_time_for_user(original_time, 'МСК', user_timezone)
        times_converted[converted_time] = original_time
    
    times = sorted(times_converted.keys())
    
    data = {}
    for time in times:
        data[time] = {}
        for day in days_of_week:
            data[time][day] = []
    
    for slot in slots:
        if slot['student'] != student_name:
            continue
            
        day_full = slot['day']
        original_time = slot['time']
        converted_time = convert_time_for_user(original_time, 'МСК', user_timezone)
        subject = slot.get('subject', 'Урок')
        status = slot.get('status', 'scheduled')
        
        if status == 'scheduled' and converted_time in data:
            data[converted_time][day_full].append(subject)
    
    return {
        'days': days_of_week,
        'times': times,
        'data': data
    }

def generate_slot_id():
    """Генерирует уникальный ID для занятия"""
    return str(uuid.uuid4())[:8]

def ensure_slot_ids():
    """Добавляет ID к занятиям, у которых их нет"""
    slots = load_slots()
    modified = False
    
    for slot in slots:
        if 'id' not in slot:
            slot['id'] = generate_slot_id()
            slot['status'] = 'scheduled'
            modified = True
    
    if modified:
        save_slots(slots)

def get_day_short(full_day):
    day_mapping = {
        "Понедельник": "Пн",
        "Вторник": "Вт", 
        "Среда": "Ср",
        "Четверг": "Чт",
        "Пятница": "Пт",
        "Суббота": "Сб",
        "Воскресенье": "Вс"
    }
    return day_mapping.get(full_day, full_day)



# ИСПРАВЛЕННАЯ ФУНКЦИЯ - получения реальных уроков ученика (для виджета)
def get_student_real_schedule_for_widget(student_name, user_timezone='МСК'):
    """Получить реальное расписание ученика с учетом всех уроков"""
    slots = load_slots()
    today = datetime.now().date()
    
    # Получаем уроки на ближайшие 4 недели
    schedule_days = []
    
    for i in range(28):  # 4 недели
        check_date = today + timedelta(days=i)
        date_str = check_date.strftime('%Y-%m-%d')
        
        lessons = get_student_lessons_for_date(date_str, slots, student_name, user_timezone)
        
        if lessons:  # Только дни с уроками
            schedule_days.append({
                'date': check_date.strftime('%d.%m'),
                'full_date': date_str,
                'day_name': get_weekday_ru(check_date.weekday()),
                'day_short': get_weekday_ru(check_date.weekday())[:2],
                'is_today': check_date == today,
                'lessons': lessons
            })
    
    return schedule_days

# НОВЫЕ ФУНКЦИИ ДЛЯ ПРАВИЛЬНОЙ СТАТИСТИКИ ВИДЖЕТОВ
def get_student_widget_stats(student_name):
    """Получить статистику ученика для виджетов"""
    slots = load_slots()
    today = datetime.now().date()
    current_month = today.month
    current_year = today.year
    
    # Инициализируем счетчики
    completed_lessons = 0           # Проведено уроков (всего)
    cancelled_lessons = 0           # Отменено уроков (всего)
    planned_this_month = 0          # Запланировано в этом месяце (только регулярные)
    
    for slot in slots:
        if slot['student'] != student_name:
            continue
            
        status = slot.get('status', 'scheduled')
        is_from_template = slot.get('from_template', False)  # Регулярный урок из шаблона
        
        # Проведенные уроки (все)
        if status == 'completed':
            completed_lessons += 1
        
        # Отмененные уроки (все)
        elif status == 'cancelled':
            cancelled_lessons += 1
        
        # Запланированные регулярные уроки в этом месяце
        elif status == 'scheduled' and is_from_template:
            # Проверяем, что урок в текущем месяце
            lesson_date = None
            
            if slot.get('date'):
                # Разовый урок с конкретной датой
                try:
                    lesson_date = datetime.strptime(slot['date'], '%Y-%m-%d').date()
                except:
                    continue
            else:
                # Регулярный урок - ищем ближайшую дату в этом месяце
                weekday_name = slot['day']
                weekday_num = get_weekday_num(weekday_name)
                
                if weekday_num is not None:
                    # Проверяем все дни текущего месяца
                    for day in range(1, 32):
                        try:
                            check_date = datetime(current_year, current_month, day).date()
                            if check_date.weekday() == weekday_num:
                                lesson_date = check_date
                                break
                        except ValueError:
                            continue
            
            if lesson_date and lesson_date.month == current_month and lesson_date.year == current_year:
                planned_this_month += 1
    
    return {
        'completed_lessons': completed_lessons,
        'cancelled_lessons': cancelled_lessons,
        'planned_this_month': planned_this_month
    }

def get_student_payment_stats(student_name):
    """Получить финансовую статистику ученика"""
    balance = get_student_balance(student_name)
    
    # Запас уроков (оплачено вперед)
    lesson_price = balance.get('lesson_price', 0)
    current_balance = balance.get('balance', 0)
    
    if lesson_price > 0 and current_balance > 0:
        lessons_in_stock = int(current_balance / lesson_price)
    else:
        lessons_in_stock = 0
    
    # Ожидают оплаты (проведенные, но неоплаченные)
    slots = load_slots()
    unpaid_lessons = 0
    
    for slot in slots:
        if slot['student'] != student_name:
            continue
            
        # Проведенные, но неоплаченные уроки
        if slot.get('status') == 'completed' and not slot.get('is_paid', False):
            # Исключаем пробные уроки
            if slot.get('lesson_type') != 'trial':
                unpaid_lessons += 1
    
    return {
        'lessons_in_stock': lessons_in_stock,
        'unpaid_lessons': unpaid_lessons,
        'lesson_price': lesson_price
    }

def get_weekday_num(day_name_ru):
    """Получить номер дня недели (0-6) по русскому названию"""
    days_mapping = {
        "Понедельник": 0,
        "Вторник": 1,
        "Среда": 2,
        "Четверг": 3,
        "Пятница": 4,
        "Суббота": 5,
        "Воскресенье": 6
    }
    return days_mapping.get(day_name_ru)

# ИСПРАВЛЕННАЯ ФУНКЦИЯ - детальная статистика для оплат
def get_month_student_detailed_stats(year, month):
    """Получить детальную статистику по каждому ученику за месяц"""
    students = load_students()
    slots = load_slots()
    
    # Получаем все дни месяца
    month_calendar = get_month_calendar(year, month)
    all_month_dates = []
    for week in month_calendar:
        for day in week:
            if day:
                all_month_dates.append(day['date'])
    
    student_stats = {}
    
    for student in students:
        student_name = student['name']
        
        # Счетчики для ученика
        regular_planned = 0     # Запланированные регулярные уроки (из шаблона)
        total_completed = 0     # Все проведенные уроки (включая внеплановые)
        regular_cancelled = 0   # Отмененные регулярные уроки (без внеплановых)
        
        # Проходим по всем дням месяца
        for date_str in all_month_dates:
            date_lessons = get_lessons_for_date(date_str, slots)
            
            for lesson in date_lessons:
                if lesson['student'] != student_name:
                    continue
                
                status = lesson.get('status', 'scheduled')
                is_from_template = lesson.get('from_template', False)  # Регулярный урок из шаблона
                is_one_time = lesson.get('date') is not None  # Разовый урок (имеет конкретную дату)
                
                # Подсчет проведенных уроков (ВСЕ - регулярные + внеплановые)
                if status == 'completed':
                    total_completed += 1
                
                # Подсчет запланированных регулярных уроков (только из шаблона)
                if is_from_template and not is_one_time:
                    if status in ['scheduled', 'completed']:  # Запланированные и уже проведенные
                        regular_planned += 1
                
                # Подсчет отмененных регулярных уроков (только из шаблона, без внеплановых)
                if is_from_template and not is_one_time and status == 'cancelled':
                    regular_cancelled += 1
        
        student_stats[student_name] = {
            'regular_planned': regular_planned,      # Запланированные регулярные
            'total_completed': total_completed,      # Все проведенные
            'regular_cancelled': regular_cancelled   # Отмененные регулярные
        }
    
    return student_stats

# ИСПРАВЛЕННАЯ ФУНКЦИЯ - автоматическое обновление статусов уроков
def auto_update_lesson_statuses():
    """Автоматически обновляет статусы уроков на основе даты, времени и длительности урока"""
    slots = load_slots()
    today = datetime.now()
    modified = False
    
    print(f"[AUTO_UPDATE] Проверяем уроки на дату и время: {today}")
    
    for slot in slots:
        # Пропускаем уроки, которые уже отменены, перенесены или завершены
        if slot.get('status') in ['cancelled', 'moved', 'completed']:
            continue
        
        # Определяем дату и время урока
        lesson_datetime = None
        
        if slot.get('date'):
            # Разовый урок с конкретной датой
            try:
                lesson_date = datetime.strptime(slot['date'], '%Y-%m-%d').date()
                lesson_time = datetime.strptime(slot['time'], '%H:%M').time()
                lesson_datetime = datetime.combine(lesson_date, lesson_time)
            except:
                continue
        else:
            # Регулярный урок - ищем ближайшую прошедшую дату с таким днем недели
            weekday_name = slot['day']
            weekday_num = get_weekday_num(weekday_name)
            
            if weekday_num is not None:
                # Проверяем последние 7 дней
                for days_back in range(1, 8):
                    check_date = today.date() - timedelta(days=days_back)
                    if check_date.weekday() == weekday_num:
                        try:
                            lesson_time = datetime.strptime(slot['time'], '%H:%M').time()
                            lesson_datetime = datetime.combine(check_date, lesson_time)
                            break
                        except:
                            continue
        
        # Если удалось определить время урока
        if lesson_datetime:
            # Получаем длительность урока (по умолчанию 60 минут)
            lesson_duration = slot.get('lesson_duration', 60)
            lesson_end_time = lesson_datetime + timedelta(minutes=lesson_duration)
            
            # Если урок уже должен был закончиться
            if lesson_end_time < today and slot.get('status') == 'scheduled':
                print(f"[AUTO_UPDATE] Автоматически завершаем урок: {slot.get('id')} для {slot['student']} (начало: {lesson_datetime}, длительность: {lesson_duration} мин)")
                
                slot['status'] = 'completed'
                slot['auto_completed_at'] = today.isoformat()
                modified = True
                
                # Автоматически списываем оплату при завершении урока
                success, message = process_lesson_payment(slot['student'], slot.get('id'))
                if success:
                    slot['is_paid'] = True
                    print(f"[AUTO_UPDATE] Автоматически списана оплата: {message}")
                else:
                    print(f"[AUTO_UPDATE] Ошибка списания оплаты: {message}")
    
    if modified:
        save_slots(slots)
        print(f"[AUTO_UPDATE] Обновлено уроков: {sum(1 for slot in slots if slot.get('auto_completed_at'))}")
        
        # Обновляем балансы всех учеников
        students = load_students()
        for student in students:
            update_student_balance_with_completed_lessons(student['name'])
    
    return modified

# ИСПРАВЛЕННАЯ ФУНКЦИЯ - обработка платежа за урок
def process_lesson_payment(student_name, lesson_id):
    """Списать средства за проведенный урок (кроме пробных)"""
    # Проверяем, не является ли урок пробным
    slots = load_slots()
    lesson_slot = None
    for slot in slots:
        if slot.get('id') == lesson_id:
            lesson_slot = slot
            break
    
    # Если урок пробный, не списываем деньги
    if lesson_slot and lesson_slot.get('lesson_type') == 'trial':
        return True, "Пробный урок завершен (бесплатно)"
    
    balances = load_balances()
    payments = load_payments()
    
    # ИСПРАВЛЯЕМ: Создаем баланс если его нет
    if student_name not in balances:
        students = load_students()
        student = next((s for s in students if s['name'] == student_name), None)
        if student:
            balances[student_name] = {
                "balance": 0,
                "lesson_price": student.get('lesson_price', 0),
                "total_paid": 0,
                "total_spent": 0,
                "lessons_taken": 0,
                "created_at": datetime.now().isoformat()
            }
        else:
            return False, "Ученик не найден в системе"
    
    student_balance = balances[student_name]
    lesson_price = student_balance.get("lesson_price", 0)
    
    # ИСПРАВЛЯЕМ: Разрешаем уход в минус (создание долга)
    print(f"[PAYMENT] Списываем {lesson_price} руб. с баланса {student_balance['balance']} руб. для {student_name}")
    
    # Списываем средства (может уйти в минус)
    student_balance["balance"] -= lesson_price
    student_balance["total_spent"] += lesson_price
    student_balance["lessons_taken"] += 1
    
    # Создаем запись о расходе
    expense = {
        "id": generate_slot_id(),
        "student_name": student_name,
        "amount": -lesson_price,
        "type": "expense",
        "description": f"Оплата урока {lesson_id}",
        "lesson_id": lesson_id,
        "date": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat()
    }
    
    payments.append(expense)
    save_payments(payments)
    save_balances(balances)
    
    return True, f"Урок оплачен. Остаток на балансе: {student_balance['balance']} руб."

def count_completed_lessons(student_name):
    """Подсчитать количество проведенных уроков ученика"""
    slots = load_slots()
    completed_count = 0
    
    for slot in slots:
        if slot['student'] == student_name and slot.get('status') == 'completed':
            completed_count += 1
    
    return completed_count

def update_student_balance_with_completed_lessons(student_name):
    """Обновить баланс ученика с учетом проведенных уроков"""
    balances = load_balances()
    
    if student_name not in balances:
        return
    
    # Подсчитываем проведенные уроки
    completed_lessons = count_completed_lessons(student_name)
    
    # Обновляем в балансе
    balances[student_name]['lessons_taken'] = completed_lessons
    
    save_balances(balances)

# Функции для работы с балансом
def add_payment(student_name, amount, description="Пополнение баланса", payment_date=None):
    """Добавить платеж ученика"""
    payments = load_payments()
    balances = load_balances()
    
    if payment_date is None:
        payment_date = datetime.now()
    elif isinstance(payment_date, str):
        try:
            payment_date = datetime.strptime(payment_date, '%Y-%m-%d')
        except:
            payment_date = datetime.now()
    
    # Создаем запись о платеже
    payment = {
        "id": generate_slot_id(),
        "student_name": student_name,
        "amount": amount,
        "type": "payment",  # payment или expense
        "description": description,
        "date": payment_date.isoformat(),
        "created_at": datetime.now().isoformat()
    }
    
    payments.append(payment)
    save_payments(payments)
    
    # Обновляем баланс ученика
    if student_name not in balances:
        # ИСПРАВЛЯЕМ: Берем стоимость урока из данных ученика
        students = load_students()
        student = next((s for s in students if s['name'] == student_name), None)
        lesson_price = student.get('lesson_price', 0) if student else 0
        
        balances[student_name] = {
            "balance": 0,
            "lesson_price": lesson_price,
            "total_paid": 0,
            "total_spent": 0,
            "lessons_taken": 0,
            "created_at": datetime.now().isoformat()
        }
    
    balances[student_name]["balance"] += amount
    balances[student_name]["total_paid"] += amount
    save_balances(balances)
    
    return payment
def get_student_balance(student_name):
    """Получить баланс ученика"""
    balances = load_balances()
    
    # ИСПРАВЛЯЕМ: Если баланса нет, создаем его
    if student_name not in balances:
        students = load_students()
        student = next((s for s in students if s['name'] == student_name), None)
        lesson_price = student.get('lesson_price', 0) if student else 0
        
        balances[student_name] = {
            "balance": 0,
            "lesson_price": lesson_price,
            "total_paid": 0,
            "total_spent": 0,
            "lessons_taken": 0,
            "created_at": datetime.now().isoformat()
        }
        save_balances(balances)
    
    return balances.get(student_name, {
        "balance": 0,
        "lesson_price": 0,
        "total_paid": 0,
        "total_spent": 0,
        "lessons_taken": 0
    })

def get_student_payment_history(student_name, limit=None):
    """Получить историю платежей ученика"""
    payments = load_payments()
    student_payments = [p for p in payments if p["student_name"] == student_name]
    
    # Сортируем по дате (новые первыми)
    student_payments.sort(key=lambda x: x["date"], reverse=True)
    
    if limit:
        student_payments = student_payments[:limit]
    
    return student_payments

def reset_student_balance(student_name):
    """Обнулить баланс ученика"""
    balances = load_balances()
    payments = load_payments()
    
    if student_name in balances:
        balances[student_name]['balance'] = 0
        balances[student_name]['total_paid'] = 0
        balances[student_name]['total_spent'] = 0
        balances[student_name]['lessons_taken'] = 0
        save_balances(balances)
        
        # НОВОЕ: Также удаляем все записи о платежах этого ученика
        new_payments = [p for p in payments if p["student_name"] != student_name]
        save_payments(new_payments)
        
        return True
    return False

def get_financial_overview():
    """Получить общий финансовый обзор по всем ученикам"""
    students = load_students()
    balances = load_balances()
    
    total_prepaid = 0  # Общая стоимость оплаченных вперед уроков
    total_debt = 0     # Общая стоимость долгов
    total_balance = 0  # Общий баланс всех учеников
    
    for student in students:
        student_balance = balances.get(student['name'], {})
        balance_amount = student_balance.get('balance', 0)
        
        total_balance += balance_amount
        
        if balance_amount > 0:
            # Положительный баланс = оплачено вперед
            total_prepaid += balance_amount
        elif balance_amount < 0:
            # Отрицательный баланс = долг
            total_debt += abs(balance_amount)
    
    return {
        'total_prepaid': total_prepaid,
        'total_debt': total_debt,
        'total_balance': total_balance,
        'students_with_positive_balance': len([s for s in students if balances.get(s['name'], {}).get('balance', 0) > 0]),
        'students_with_negative_balance': len([s for s in students if balances.get(s['name'], {}).get('balance', 0) < 0])
    }

def lesson_exists_in_schedule(day, time, student, subject):
    """Проверить, существует ли уже урок в расписании"""
    slots = load_slots()
    
    for slot in slots:
        if (slot['day'] == day and 
            slot['time'] == time and 
            slot['student'] == student and 
            slot['subject'] == subject and
            not slot.get('date')):  # Только регулярные уроки, не разовые
            return True
    return False



# ИСПРАВЛЕННАЯ ФУНКЦИЯ - обновление урока в шаблоне
def update_template_lesson(index, lesson_data):
    """Обновить урок в шаблоне недели"""
    template = load_template_week()
    
    if 0 <= index < len(template):
        template[index] = {
            "day": lesson_data.get("day"),
            "time": lesson_data.get("time"),
            "student": lesson_data.get("student"),
            "subject": lesson_data.get("subject"),
            "start_date": lesson_data.get("start_date", ""),
            "end_date": lesson_data.get("end_date", ""),
            "lesson_type": lesson_data.get("lesson_type", "regular"),
            "lesson_duration": lesson_data.get("lesson_duration", 60)
        }
        save_template_week(template)
        return True
    
    return False

# ИСПРАВЛЕННАЯ ФУНКЦИЯ - добавление урока в шаблон
def add_template_lesson(lesson_data):
    """Добавить новый урок в шаблон недели"""
    template = load_template_week()
    
    new_lesson = {
        "day": lesson_data.get("day"),
        "time": lesson_data.get("time"),
        "student": lesson_data.get("student"),
        "subject": lesson_data.get("subject"),
        "start_date": lesson_data.get("start_date", ""),
        "end_date": lesson_data.get("end_date", ""),
        "lesson_type": lesson_data.get("lesson_type", "regular"),
        "lesson_duration": lesson_data.get("lesson_duration", 60)
    }
    
    # Проверяем дублирование в шаблоне
    for existing in template:
        if (existing['day'] == new_lesson['day'] and
            existing['time'] == new_lesson['time'] and
            existing['student'] == new_lesson['student']):
            return False  # дубликат найден
    
    template.append(new_lesson)
    save_template_week(template)
    return True

# НОВЫЕ ФУНКЦИИ ДЛЯ УЛУЧШЕННОГО ВИДЖЕТА
def get_student_week_calendar_for_api(student_name, year, week, user_timezone='МСК'):
    """Получить данные недельного календаря для API"""
    slots = load_slots()
    week_dates = get_week_dates(year, week)
    
    # Формируем данные для каждого дня недели
    week_data = []
    
    for i, date_info in enumerate(week_dates):
        lessons = get_student_lessons_for_date(date_info['full_date'], slots, student_name, user_timezone)
        
        day_data = {
            'day_name': date_info['day_name'],
            'day_short': date_info['day_name'][:2],
            'date': date_info['date'],
            'full_date': date_info['full_date'],
            'is_today': date_info['is_today'],
            'lessons': lessons
        }
        
        week_data.append(day_data)
    
    # Информация о неделе
    week_start = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w")
    week_end = week_start + timedelta(days=6)
    
    # ИСПРАВЛЯЕМ: Правильные русские названия месяцев
    month_names = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
        7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    }
    
    start_month = month_names.get(week_start.month, "")
    end_month = month_names.get(week_end.month, "")
    
    if week_start.month == week_end.month:
        title = f"с {week_start.day} по {week_end.day} {end_month}"
    else:
        title = f"с {week_start.day} {start_month} по {week_end.day} {end_month}"
    
    return {
        'week_data': week_data,
        'week_info': {
            'year': year,
            'week': week,
            'start_date': week_start.strftime('%d.%m'),
            'end_date': week_end.strftime('%d.%m'),
            'title': title
        },
        'navigation': {
            'prev_week': week - 1 if week > 1 else 52,
            'prev_year': year if week > 1 else year - 1,
            'next_week': week + 1 if week < 52 else 1,
            'next_year': year if week < 52 else year + 1
        }
    }

# ИСПРАВЛЕННАЯ ФУНКЦИЯ - перенос урока
def move_lesson_to_date(lesson_id, new_date, new_time=None):
    """Перенести урок на другую дату"""
    slots = load_slots()
    
    for slot in slots:
        if slot.get('id') == lesson_id:
            old_date = slot.get('date', 'регулярный')
            old_time = slot.get('time', '')
            
            # Обновляем дату
            slot['date'] = new_date
            
            # Обновляем время если указано
            if new_time:
                slot['time'] = new_time
                
            # Сохраняем длительность урока при переносе
            if 'lesson_duration' not in slot:
                slot['lesson_duration'] = 60  # По умолчанию 60 минут для старых уроков
            
            # ИСПРАВЛЯЕМ: При переносе проведенного урока сбрасываем статус
            if slot.get('status') == 'completed':
                slot['status'] = 'scheduled'
                slot['moved_from_completed'] = True
            
            # Добавляем информацию о переносе
            slot['moved'] = True
            slot['moved_from'] = f"{old_date} {old_time}"
            slot['moved_at'] = datetime.now().isoformat()
            
            # Если это был регулярный урок, убираем день недели
            if 'day' in slot:
                slot['original_day'] = slot['day']
                del slot['day']
            
            save_slots(slots)
            return True, f"Урок перенесен на {new_date}"
    
    return False, "Урок не найден"
# НОВАЯ ФУНКЦИЯ - полная очистка расписания
def clear_all_lessons():
    """Очистить все занятия"""
    try:
        save_slots([])
        return True, "Все занятия удалены"
    except Exception as e:
        return False, f"Ошибка при очистке: {e}"

# ИСПРАВЛЕННАЯ ФУНКЦИЯ - применение шаблона с учетом периодов
def apply_template_to_schedule_with_periods():
    """Применить шаблон недели с учетом указанных периодов"""
    template = load_template_week()
    slots = load_slots()
    
    added_count = 0
    today = datetime.now().date()
    
    for template_lesson in template:
        start_date = template_lesson.get('start_date')
        end_date = template_lesson.get('end_date')
        
        # Определяем период действия урока
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            except:
                start_date_obj = today  # Если дата некорректная, начинаем с сегодня
        else:
            start_date_obj = today
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            except:
                end_date_obj = today + timedelta(days=365)  # Если дата некорректная, на год вперед
        else:
            end_date_obj = today + timedelta(days=365)  # По умолчанию на год вперед
        
        # Находим все даты в указанном периоде для нужного дня недели
        day_name = template_lesson['day']
        target_weekday = get_weekday_num(day_name)
        
        current_date = start_date_obj
        while current_date <= end_date_obj:
            if current_date.weekday() == target_weekday:
                # Проверяем, нет ли уже урока на эту дату
                existing_lesson = False
                for existing_slot in slots:
                    if (existing_slot.get('date') == current_date.strftime('%Y-%m-%d') and
                        existing_slot['time'] == template_lesson['time'] and
                        existing_slot['student'] == template_lesson['student']):
                        existing_lesson = True
                        break
                
                if not existing_lesson:
                    # Создаем новый урок
                    new_slot = {
                        "id": generate_slot_id(),
                        "date": current_date.strftime('%Y-%m-%d'),
                        "time": template_lesson['time'],
                        "student": template_lesson['student'],
                        "subject": template_lesson['subject'],
                        "status": "scheduled",
                        "from_template": True,
                        "lesson_type": template_lesson.get('lesson_type', 'regular'),
                        "template_period": f"{start_date} - {end_date}",
                        "lesson_duration": template_lesson.get('lesson_duration', 60)
                    }
                    slots.append(new_slot)
                    added_count += 1
            
            current_date += timedelta(days=1)
    
    if added_count > 0:
        save_slots(slots)
    
    return added_count

# НОВАЯ ФУНКЦИЯ - полное удаление всех данных ученика
def delete_student_completely(student_name):
    """Полное удаление ученика и всех его данных"""
    # 1. Удаляем из расписания
    slots = load_slots()
    new_slots = [slot for slot in slots if slot['student'] != student_name]
    save_slots(new_slots)
    
    # 2. Удаляем из шаблона недели
    template = load_template_week()
    new_template = [lesson for lesson in template if lesson['student'] != student_name]
    save_template_week(new_template)
    
    # 3. Удаляем балансы
    balances = load_balances()
    if student_name in balances:
        del balances[student_name]
        save_balances(balances)
    
    # 4. Удаляем платежи
    payments = load_payments()
    new_payments = [payment for payment in payments if payment['student_name'] != student_name]
    save_payments(new_payments)
    
    # 5. Удаляем данные пробных уроков если есть
    trial_students = load_trial_students()
    new_trial_students = [trial for trial in trial_students if trial['student_name'] != student_name]
    save_trial_students(new_trial_students)
    
    print(f"[DELETE_STUDENT] Полностью удален ученик {student_name} и все его данные")

# Инициализация при запуске
def initialize_app():
    """Инициализация приложения при запуске"""
    print("Инициализация Календаши...")
    
    # Убеждаемся, что папка data существует
    os.makedirs("data", exist_ok=True)
    
    # Создаем пустые файлы, если их нет
    for filename in [DATA_FILE, DATA_SLOTS_FILE, TEMPLATE_WEEK_FILE, DATA_PAYMENTS_FILE, DATA_BALANCES_FILE, DATA_TRIAL_STUDENTS_FILE]:
        if not os.path.exists(filename):
            if filename == DATA_BALANCES_FILE:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
            else:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump([], f)
    
    # Добавляем ID к существующим слотам
    ensure_slot_ids()
    
    # ИСПРАВЛЯЕМ: Обновляем статусы уроков и списываем оплату
    print("Проверяем статусы уроков...")
    auto_update_lesson_statuses()
    
    # Обновляем балансы всех учеников
    students = load_students()
    for student in students:
        # Создаем баланс, если его нет
        balances = load_balances()
        if student['name'] not in balances:
            balances[student['name']] = {
                "balance": 0,
                "lesson_price": student.get('lesson_price', 0),
                "total_paid": 0,
                "total_spent": 0,
                "lessons_taken": 0,
                "created_at": datetime.now().isoformat()
            }
            save_balances(balances)
        
        # Обновляем количество проведенных уроков
        update_student_balance_with_completed_lessons(student['name'])
    
    print("Календаша готова к работе! 🎓✨")

# Маршруты Flask
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/ученики")
def ucheniki():
    students = load_students()
    return render_template("ucheniki.html", students=students)

@app.route("/ученики/добавить", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        # Обработка кастомного класса
        class_value = request.form.get("class", "").strip()
        custom_class = request.form.get("custom_class", "").strip()
        
        if class_value == "Другое" and custom_class:
            class_value = custom_class
        
        # Добавляем сохранение стоимости урока
        lesson_price = request.form.get("lesson_price", "0")
        try:
            lesson_price = float(lesson_price)
        except (ValueError, TypeError):
            lesson_price = 0
        
        student = {
            "name": request.form.get("name", "").strip(),
            "class": class_value,
            "city": request.form.get("city", "").strip(),
            "timezone": request.form.get("timezone", "МСК"),
            "parent_name": request.form.get("parent_name", "").strip(),
            "contact": request.form.get("contact", "").strip(),
            "notes": request.form.get("notes", "").strip(),
            "lesson_price": lesson_price
        }
        
        if student["name"]:
            students = load_students()
            students.append(student)
            save_students(students)
            
            # Создаем начальный баланс для ученика
            balances = load_balances()
            balances[student["name"]] = {
                "balance": 0,
                "lesson_price": lesson_price,
                "total_paid": 0,
                "total_spent": 0,
                "lessons_taken": 0,
                "created_at": datetime.now().isoformat()
            }
            save_balances(balances)
            
            return redirect(url_for("ucheniki"))
    
    return render_template("add_student.html")

@app.route("/ученики/редактировать/<int:index>", methods=["GET", "POST"])
def edit_student(index):
    students = load_students()
    
    if index < 0 or index >= len(students):
        return redirect(url_for("ucheniki"))
    
    student = students[index]
    
    if request.method == "POST":
        # Обработка кастомного класса
        class_value = request.form.get("class", "").strip()
        custom_class = request.form.get("custom_class", "").strip()
        
        if class_value == "Другое" and custom_class:
            class_value = custom_class
        
        # Получаем новую стоимость урока
        lesson_price = request.form.get("lesson_price", "0")
        try:
            lesson_price = float(lesson_price)
        except (ValueError, TypeError):
            lesson_price = student.get('lesson_price', 0)
        
        old_name = student["name"]
        new_name = request.form.get("name", "").strip()
        
        # Обновляем данные ученика
        student.update({
            "name": new_name,
            "class": class_value,
            "city": request.form.get("city", "").strip(),
            "timezone": request.form.get("timezone", "МСК"),
            "parent_name": request.form.get("parent_name", "").strip(),
            "contact": request.form.get("contact", "").strip(),
            "notes": request.form.get("notes", "").strip(),
            "lesson_price": lesson_price
        })
        
        save_students(students)
        
        # Если имя изменилось, обновляем все связанные данные
        if old_name != new_name:
            # Обновляем слоты
            slots = load_slots()
            for slot in slots:
                if slot['student'] == old_name:
                    slot['student'] = new_name
            save_slots(slots)
            
            # Обновляем шаблон недели
            template = load_template_week()
            for lesson in template:
                if lesson['student'] == old_name:
                    lesson['student'] = new_name
            save_template_week(template)
            
            # Обновляем балансы
            balances = load_balances()
            if old_name in balances:
                balances[new_name] = balances.pop(old_name)
                balances[new_name]['lesson_price'] = lesson_price
                save_balances(balances)
            
            # Обновляем платежи
            payments = load_payments()
            for payment in payments:
                if payment['student_name'] == old_name:
                    payment['student_name'] = new_name
            save_payments(payments)
        else:
            # Просто обновляем цену урока в балансах
            balances = load_balances()
            if old_name in balances:
                balances[old_name]['lesson_price'] = lesson_price
                save_balances(balances)
        
        return redirect(url_for("ucheniki"))
    
    return render_template("edit_student.html", student=student, index=index)

@app.route("/ученики/удалить/<int:index>", methods=["POST"])
def delete_student(index):
    students = load_students()
    if 0 <= index < len(students):
        student_name = students[index]["name"]
        # ИСПРАВЛЯЕМ: Полное удаление всех данных ученика
        delete_student_completely(student_name)
        students.pop(index)
        save_students(students)
    return redirect(url_for("ucheniki"))
# ИСПРАВЛЕННЫЙ МАРШРУТ РАСПИСАНИЯ с запоминанием режима
@app.route("/расписание")
@app.route("/расписание/<view_type>")
@app.route("/расписание/<view_type>/<int:year>/<int:period>")
def raspisanie(view_type=None, year=None, period=None):
    # ИСПРАВЛЯЕМ: Автоматически обновляем статусы уроков
    auto_update_lesson_statuses()
    
    today = datetime.now()
    
    # НОВОЕ: Если view_type не указан, используем текущую неделю по умолчанию
    if view_type is None:
        view_type = "week"
        # ИСПРАВЛЯЕМ: Перенаправляем на текущую неделю
        current_year = today.year
        current_week = today.isocalendar()[1]
        return redirect(url_for("raspisanie", view_type="week", year=current_year, period=current_week))
    
    if view_type == "week":
        if year is None or period is None:
            # ИСПРАВЛЯЕМ: Показываем текущую неделю
            year, period = today.year, today.isocalendar()[1]
        
        # Навигация по неделям
        prev_week = period - 1 if period > 1 else 52
        prev_year = year if period > 1 else year - 1
        next_week = period + 1 if period < 52 else 1
        next_year = year if period < 52 else year + 1
        
        # Получаем данные недели
        week_dates = get_week_dates(year, period)
        slots = load_slots()
        
        # НОВОЕ: Проверяем конфликты времени с учетом длительности
        conflicts = check_time_conflicts(slots)
        
        # Добавляем занятия к каждому дню
        for date_info in week_dates:
            date_lessons = get_lessons_for_date(date_info['full_date'], slots)
            # Добавляем информацию о конфликтах
            for lesson in date_lessons:
                lesson['has_conflict'] = lesson.get('id') in conflicts
            date_info['lessons'] = date_lessons
        
        # ИСПРАВЛЯЕМ: Правильные русские названия месяцев для недели
        week_start = datetime.strptime(f"{year}-W{period:02d}-1", "%Y-W%W-%w")
        week_end = week_start + timedelta(days=6)
        
        month_names = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
            7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        
        start_month = month_names.get(week_start.month, "")
        end_month = month_names.get(week_end.month, "")
        
        if week_start.month == week_end.month:
            week_info = f"с {week_start.day} по {week_end.day} {end_month}"
        else:
            week_info = f"с {week_start.day} {start_month} по {week_end.day} {end_month}"
        
        # НОВОЕ: Определяем месяц для переключателя (берем месяц середины недели)
        mid_week = week_start + timedelta(days=3)
        month_from_week = mid_week.month
        
        return render_template("raspisanie.html",
                             view_type="week",
                             week_dates=week_dates,
                             week_info=week_info,
                             year=year,
                             week=period,
                             month_from_week=month_from_week,
                             prev_year=prev_year,
                             prev_week=prev_week,
                             next_year=next_year,
                             next_week=next_week)
    else:  # month view
        if year is None or period is None:
            year, period = today.year, today.month
        
        # Навигация по месяцам
        if period == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, period - 1
        
        if period == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, period + 1
        
        # Получаем календарь месяца
        month_calendar = get_month_calendar(year, period)
        slots = load_slots()
        
        # НОВОЕ: Проверяем конфликты времени с учетом длительности
        conflicts = check_time_conflicts(slots)
        
        # Добавляем занятия к каждому дню
        for week in month_calendar:
            for day in week:
                if day:
                    date_lessons = get_lessons_for_date(day['date'], slots)
                    # Добавляем информацию о конфликтах
                    for lesson in date_lessons:
                        lesson['has_conflict'] = lesson.get('id') in conflicts
                    day['lessons'] = date_lessons
        
        # Название месяца
        month_names = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        month_name = month_names.get(period, "Месяц")
        
        # НОВОЕ: Определяем текущую неделю месяца для переключателя
        current_week_of_month = today.isocalendar()[1]
        
        return render_template("raspisanie.html",
                             view_type="month",
                             month_calendar=month_calendar,
                             year=year,
                             month=period,
                             month_name=month_name,
                             current_week_of_month=current_week_of_month,
                             prev_year=prev_year,
                             prev_month=prev_month,
                             next_year=next_year,
                             next_month=next_month)

# НОВЫЙ МАРШРУТ - очистка расписания
@app.route("/админ/очистить-расписание", methods=["POST"])
def clear_schedule():
    """Полная очистка расписания"""
    success, message = clear_all_lessons()
    if success:
        return f"<script>alert('{message}'); window.location.href='/расписание';</script>"
    else:
        return f"<script>alert('Ошибка: {message}'); window.location.href='/расписание';</script>"

# НОВЫЙ МАРШРУТ - перенос урока
@app.route("/api/lesson/<lesson_id>/move", methods=["POST"])
def move_lesson_api(lesson_id):
    """API для переноса урока"""
    data = request.get_json()
    new_date = data.get('new_date')
    new_time = data.get('new_time')
    
    if not new_date:
        return jsonify({"success": False, "error": "Новая дата не указана"}), 400
    
    success, message = move_lesson_to_date(lesson_id, new_date, new_time)
    
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "error": message}), 400

# НОВЫЙ МАРШРУТ - добавление пробного урока
@app.route("/добавить-пробный-урок", methods=["POST"])
def add_trial_lesson_route():
    """Добавить пробный урок с данными потенциального ученика"""
    try:
        data = request.get_json()
        
        date = data.get('date')
        time = data.get('time')
        student_name = data.get('student_name', '').strip()
        subject = data.get('subject', 'Пробный урок')
        lesson_duration = int(data.get('lesson_duration', 60))
        
        # Данные потенциального ученика
        student_data = {
            'parent_name': data.get('parent_name', '').strip(),
            'student_contact': data.get('student_contact', '').strip(),
            'parent_contact': data.get('parent_contact', '').strip()
        }
        
        if not date or not time or not student_name:
            return jsonify({"success": False, "error": "Заполните обязательные поля"}), 400
        
        # Создаем пробный урок
        trial_lesson = create_trial_lesson(date, time, student_name, subject, lesson_duration, student_data)
        
        return jsonify({
            "success": True, 
            "message": f"Пробный урок с {student_name} добавлен на {date} в {time}",
            "lesson_id": trial_lesson["id"]
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/шаблон-недели", methods=["GET", "POST"])
def shablon_nedeli():
    students = load_students()
    template = load_template_week()
    
    if request.method == "POST":
        # Проверяем, какое действие выполняется
        if 'edit_index' in request.form:
            # Редактирование существующего урока
            try:
                edit_index = int(request.form.get('edit_index'))
                
                # Получаем длительность урока для редактирования
                edit_lesson_duration = request.form.get("edit_lesson_duration", "60")
                try:
                    edit_lesson_duration = int(edit_lesson_duration)
                    if edit_lesson_duration < 10:
                        edit_lesson_duration = 60
                    elif edit_lesson_duration > 300:
                        edit_lesson_duration = 300
                except (ValueError, TypeError):
                    edit_lesson_duration = 60

                lesson_data = {
                    "day": request.form.get("edit_day"),
                    "time": request.form.get("edit_time"),
                    "student": request.form.get("edit_student"),
                    "subject": request.form.get("edit_subject"),
                    "start_date": request.form.get("edit_start_date", ""),
                    "end_date": request.form.get("edit_end_date", ""),
                    "lesson_type": request.form.get("edit_lesson_type", "regular"),
                    "lesson_duration": edit_lesson_duration
                }
                update_template_lesson(edit_index, lesson_data)
            except (ValueError, IndexError):
                pass
        else:
            # Добавление нового урока
            subject = request.form.get("subject")
            if subject == "Другое":
                subject = request.form.get("custom_subject", "Урок")
            
            # Получаем длительность урока
            lesson_duration = request.form.get("lesson_duration", "60")
            try:
                lesson_duration = int(lesson_duration)
                if lesson_duration < 10:
                    lesson_duration = 60
                elif lesson_duration > 300:
                    lesson_duration = 300
            except (ValueError, TypeError):
                lesson_duration = 60

            lesson_data = {
                "day": request.form.get("day"),
                "time": request.form.get("time"),
                "student": request.form.get("student_name"),
                "subject": subject,
                "start_date": request.form.get("start_date", ""),
                "end_date": request.form.get("end_date", ""),
                "lesson_type": request.form.get("lesson_type", "regular"),
                "lesson_duration": lesson_duration
            }
            
            # Добавляем урок в шаблон (с проверкой дублирования)
            add_template_lesson(lesson_data)
        
        return redirect(url_for("shablon_nedeli"))
    
    return render_template("shablon_nedeli.html", students=students, template=template)

@app.route("/шаблон-недели/удалить/<int:index>", methods=["POST"])
def delete_template_lesson(index):
    template = load_template_week()
    if 0 <= index < len(template):
        lesson_to_delete = template[index]
        
        # Удаляем урок из шаблона
        template.pop(index)
        save_template_week(template)
        
        # Удаляем связанные уроки из расписания
        slots = load_slots()
        new_slots = []
        for slot in slots:
            # Удаляем уроки из расписания, которые созданы из этого шаблона
            if (slot.get('from_template') and 
                slot['student'] == lesson_to_delete['student'] and
                slot['time'] == lesson_to_delete['time'] and
                slot['subject'] == lesson_to_delete['subject']):
                continue  # Пропускаем (удаляем) этот урок
            new_slots.append(slot)
        
        save_slots(new_slots)
        
    return redirect(url_for("shablon_nedeli"))

# ИСПРАВЛЕННЫЙ МАРШРУТ - применение шаблона с учетом периодов
@app.route("/применить-шаблон", methods=["POST"])
def apply_template_week():
    """Применить шаблон недели к основному расписанию с учетом периодов"""
    added_count = apply_template_to_schedule_with_periods()
    
    if added_count > 0:
        return f"<script>alert('Добавлено {added_count} занятий с учетом указанных периодов!'); window.location.href='/шаблон-недели';</script>"
    else:
        return f"<script>alert('Новые занятия не добавлены (возможно, все уроки уже существуют)'); window.location.href='/шаблон-недели';</script>"

@app.route("/добавить-занятие", methods=["GET", "POST"])
def add_slot():
    students = load_students()
    
    if request.method == "POST":
        subject = request.form.get("subject")
        if subject == "Другое":
            subject = request.form.get("custom_subject", "Урок")
        
        # Создаем разовое занятие с конкретной датой
        # Получаем длительность урока
        lesson_duration = request.form.get("lesson_duration", "60")
        try:
            lesson_duration = int(lesson_duration)
            if lesson_duration < 10:
                lesson_duration = 60
            elif lesson_duration > 300:
                lesson_duration = 300
        except (ValueError, TypeError):
            lesson_duration = 60

        new_slot = {
            "id": generate_slot_id(),
            "date": request.form.get("specific_date"),  # Конкретная дата
            "time": request.form.get("time"),
            "student": request.form.get("student_name"),
            "subject": subject,
            "status": "scheduled",
            "from_template": False,
            "lesson_duration": lesson_duration
        }
        
        slots = load_slots()
        slots.append(new_slot)
        save_slots(slots)
        
        return redirect(url_for("raspisanie"))
    
    return render_template("add_slot.html", students=students)

# Остальные маршруты остаются без изменений...
# (здесь продолжаются все остальные маршруты без изменений - оплата, виджеты, API и т.д.)

@app.route("/оплата")
@app.route("/оплата/<int:year>/<int:month>")
def oplata(year=None, month=None):
    # ИСПРАВЛЯЕМ: Автоматически обновляем статусы и балансы
    auto_update_lesson_statuses()
    
    # Устанавливаем текущий месяц, если не указан
    if year is None or month is None:
        today = datetime.now()
        year, month = today.year, today.month
    
    # Навигация по месяцам
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1
    
    # Загружаем данные
    students = load_students()
    balances = load_balances()
    
    # Обновляем балансы с учетом проведенных уроков
    for student in students:
        update_student_balance_with_completed_lessons(student['name'])
    
    # Перезагружаем балансы после обновления
    balances = load_balances()
    
    # Получаем финансовый обзор
    financial_overview = get_financial_overview()
    
    # ИСПРАВЛЯЕМ - получаем правильную детальную статистику
    student_detailed_stats = get_month_student_detailed_stats(year, month)
    
    # Название месяца
    month_names = {
        1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
        5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
        9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    }
    current_month_name = month_names.get(month, "Месяц")
    
    return render_template("oplata.html", 
                         students=students,
                         balances=balances,
                         financial_overview=financial_overview,
                         student_detailed_stats=student_detailed_stats,
                         current_month_name=current_month_name,
                         current_year=year,
                         prev_year=prev_year, 
                         prev_month=prev_month,
                         next_year=next_year, 
                         next_month=next_month)

@app.route("/добавить-платеж", methods=["POST"])
def add_payment_route():
    student_name = request.form.get("student_name")
    amount = float(request.form.get("amount", 0))
    description = request.form.get("description", "Пополнение баланса")
    payment_date = request.form.get("payment_date")
    
    if student_name and amount > 0:
        add_payment(student_name, amount, description, payment_date)
    
    return redirect(url_for("oplata"))

# НОВЫЙ МАРШРУТ - обнуление баланса
@app.route("/обнулить-баланс/<student_name>", methods=["POST"])
def reset_balance_route(student_name):
    success = reset_student_balance(student_name)
    if success:
        return f"<script>alert('Баланс ученика {student_name} обнулен!'); window.location.href='/оплата';</script>"
    else:
        return f"<script>alert('Ошибка при обнулении баланса'); window.location.href='/оплата';</script>"

@app.route("/api/payment_history/<student_name>")
def get_payment_history_api(student_name):
    """API для получения истории платежей ученика"""
    payments = get_student_payment_history(student_name)
    return jsonify({
        "student_name": student_name,
        "payments": payments
    })

# Остальные маршруты (виджеты, API и т.д.) остаются без изменений...

@app.route("/виджет/<student_name>")
def student_widget_schedule(student_name):
    """Виджет для ученика (без финансовой информации)"""
    students = load_students()
    student = next((s for s in students if s['name'] == student_name), None)
    
    if not student:
        return "Ученик не найден", 404
    
    user_timezone = student.get('timezone', 'МСК')
    
    # Получаем реальное расписание ученика
    schedule_days = get_student_real_schedule_for_widget(student_name, user_timezone)
    
    # Получаем статистику для ученика
    stats = get_student_widget_stats(student_name)
    payment_stats = get_student_payment_stats(student_name)
    
    return render_template("student_widget_schedule.html",
                         student_name=student_name,
                         user_timezone=user_timezone,
                         schedule_days=schedule_days,
                         # Статистика для ученика (4 поля)
                         completed_lessons=stats['completed_lessons'],
                         cancelled_lessons=stats['cancelled_lessons'],
                         planned_this_month=stats['planned_this_month'],
                         lessons_in_stock=payment_stats['lessons_in_stock'])

@app.route("/виджет-родитель/<student_name>")
def parent_widget_schedule(student_name):
    """Виджет для родителей (с финансовой информацией)"""
    students = load_students()
    student = next((s for s in students if s['name'] == student_name), None)
    
    if not student:
        return "Ученик не найден", 404
    
    user_timezone = student.get('timezone', 'МСК')
    
    # Получаем реальное расписание ученика
    schedule_days = get_student_real_schedule_for_widget(student_name, user_timezone)
    
    # Получаем статистику для родителей
    stats = get_student_widget_stats(student_name)
    payment_stats = get_student_payment_stats(student_name)
    
    return render_template("parent_widget_schedule.html",
                         student_name=student_name,
                         user_timezone=user_timezone,
                         schedule_days=schedule_days,
                         # Статистика для родителей (6 полей)
                         completed_lessons=stats['completed_lessons'],
                         cancelled_lessons=stats['cancelled_lessons'],
                         planned_this_month=stats['planned_this_month'],
                         lessons_in_stock=payment_stats['lessons_in_stock'],
                         unpaid_lessons=payment_stats['unpaid_lessons'],
                         lesson_price=payment_stats['lesson_price'])

@app.route("/виджет/<student_name>/api/week/<int:year>/<int:week>")
def widget_week_api(student_name, year, week):
    """API для получения данных недели для виджета"""
    students = load_students()
    student = next((s for s in students if s['name'] == student_name), None)
    
    if not student:
        return jsonify({"error": "Ученик не найден"}), 404
    
    user_timezone = student.get('timezone', 'МСК')
    
    try:
        week_data = get_student_week_calendar_for_api(student_name, year, week, user_timezone)
        return jsonify(week_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/lesson/<lesson_id>/cancel", methods=["POST"])
def cancel_lesson_api(lesson_id):
    """API для отмены урока"""
    slots = load_slots()
    
    for slot in slots:
        if slot.get('id') == lesson_id:
            if slot.get('status') == 'scheduled':
                slot['status'] = 'cancelled'
                slot['cancelled_at'] = datetime.now().isoformat()
                save_slots(slots)
                return jsonify({"success": True, "message": "Урок отменен"})
            else:
                return jsonify({"success": False, "error": f"Урок уже имеет статус: {slot.get('status')}"}), 400
    
    return jsonify({"success": False, "error": "Урок не найден"}), 404

@app.route("/api/lesson/<lesson_id>/restore", methods=["POST"])
def restore_lesson_api(lesson_id):
    """API для восстановления отмененного урока"""
    slots = load_slots()
    
    for slot in slots:
        if slot.get('id') == lesson_id:
            if slot.get('status') == 'cancelled':
                slot['status'] = 'scheduled'
                slot['restored_at'] = datetime.now().isoformat()
                # Удаляем отметку об отмене
                if 'cancelled_at' in slot:
                    del slot['cancelled_at']
                save_slots(slots)
                return jsonify({"success": True, "message": "Урок восстановлен"})
            else:
                return jsonify({"success": False, "error": f"Урок не отменен, текущий статус: {slot.get('status')}"}), 400
    
    return jsonify({"success": False, "error": "Урок не найден"}), 404

# Обработка ошибок
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html'), 500

# Запуск приложения
if __name__ == "__main__":
    initialize_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
    
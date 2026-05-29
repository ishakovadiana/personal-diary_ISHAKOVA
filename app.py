from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

DATA_FILE = 'entries.json'

def load_entries():
    """Загружает записи из JSON-файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_entries(entries):
    """Сохраняет записи в JSON-файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

# Загружаем записи при старте
entries = load_entries()

@app.route('/')
def index():
    """Главная страница — список всех записей"""
    return render_template('index.html', entries=entries)

@app.route('/entry/<int:entry_id>')
def view_entry(entry_id):
    """Страница одной записи"""
    for entry in entries:
        if entry['id'] == entry_id:
            return render_template('detail.html', entry=entry)
    return "Запись не найдена", 404

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    """Добавление новой записи"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if title and content:
            # Генерируем новый ID
            new_id = max([e['id'] for e in entries], default=0) + 1
            
            new_entry = {
                'id': new_id,
                'title': title,
                'content': content,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            entries.append(new_entry)
            save_entries(entries)
            return redirect(url_for('index'))
    
    return render_template('add.html')

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    """Редактирование записи"""
    for entry in entries:
        if entry['id'] == entry_id:
            if request.method == 'POST':
                entry['title'] = request.form.get('title', '').strip()
                entry['content'] = request.form.get('content', '').strip()
                save_entries(entries)
                return redirect(url_for('index'))
            return render_template('edit.html', entry=entry)
    return "Запись не найдена", 404

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """Удаление записи"""
    for i, entry in enumerate(entries):
        if entry['id'] == entry_id:
            entries.pop(i)
            save_entries(entries)
            break
    return redirect(url_for('index'))

@app.route('/search')
def search():
    """Поиск по заголовкам"""
    query = request.args.get('q', '').lower()
    if query:
        filtered_entries = [e for e in entries if query in e['title'].lower()]
    else:
        filtered_entries = entries
    return render_template('index.html', entries=filtered_entries)

@app.route('/filter/week')
def filter_week():
    """Фильтр: записи за последние 7 дней"""
    week_ago = datetime.now() - timedelta(days=7)
    filtered_entries = []
    for entry in entries:
        try:
            entry_date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M')
            if entry_date >= week_ago:
                filtered_entries.append(entry)
        except:
            pass
    return render_template('index.html', entries=filtered_entries)

if __name__ == '__main__':
    app.run(debug=True)
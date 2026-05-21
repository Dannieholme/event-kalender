from flask import Flask, render_template, session, request
from datetime import datetime
import sqlite3
from werkzeug.utils import redirect

app = Flask(__name__)
app.secret_key = "123nfaw912kcanw149askd"
adminUsername = "admin"
adminPassword = "Sysser3498?"

def get_db():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db()

    events = conn.execute("""
        SELECT * FROM events
        ORDER BY datetime ASC
    """).fetchall()

    conn.close()
    events = [dict(event) for event in events]

    for event in events:
        dt = datetime.fromisoformat(event['datetime'])
        event['formatted_datetime'] = dt.strftime("%d-%m-%Y kl. %H:%M")

    return render_template('index.html', events=events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == adminUsername and password == adminPassword:
            session['logged_in'] = True
            return redirect('/admin')

        else:
            error = 'Forkert Brugernavn eller Adgangskode'
            return render_template('login.html', error=error)

    return render_template("login.html")
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
@app.route('/admin')
def admin():
    if 'logged_in' in session:
        conn = get_db()
        events = conn.execute("""
        SELECT * FROM events
        ORDER BY datetime ASC
        """).fetchall()
        conn.close()

        events = [dict(event) for event in events]


        for event in events:
            dt = datetime.fromisoformat(event['datetime'])
            event['formatted_datetime'] = dt.strftime("%d-%m-%Y kl. %H:%M")

        return render_template('admin.html', events=events)
    else:
        return redirect('/login')

@app.route('/admin/opret', methods=['GET', 'POST'])
def opret():
    if 'logged_in' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['Titel']
        location = request.form['Lokation']
        event_datetime = request.form['Dato']
        if not title.strip() or not location.strip() or not event_datetime.strip():
            return "Udfyld alle felter", 400
        conn = get_db()
        conn.execute("""
            INSERT INTO events (title, location, datetime)
            VALUES (?, ?, ?)
        """, (title, location, event_datetime))
        conn.commit()
        conn.close()
        return redirect('/admin')
    return render_template('opret.html')
@app.route('/admin/delete/<int:event_id>', methods=['POST'])
def delete(event_id):
    if 'logged_in' not in session:
        return redirect('/login')
    else:
        conn = get_db()
        conn.execute("""
        DELETE FROM events
        WHERE id = ?
        """, (event_id,))
        conn.commit()
        conn.close()
        return redirect('/admin')

@app.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):

    conn = get_db()
    event = conn.execute("""
    SELECT * FROM events WHERE id = ?
    """, (event_id,)).fetchone()
    conn.close()
    if event:
        return render_template('event.html', event=event)
    else:
        return "Event findes ikke", 404

@app.route('/admin/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'logged_in' not in session:
        return redirect('/login')
    conn = get_db()
    if request.method == 'POST':
        title = request.form['Titel']
        location = request.form['Lokation']
        event_datetime = request.form['Dato']
        if not title.strip() or not location.strip():
            return "Udfyld alle felter", 400
        conn.execute("""
            UPDATE events
            SET title = ?, location = ?, datetime = ?
            WHERE id = ?
        """, (title, location, event_datetime, event_id))

        conn.commit()
        conn.close()
        return redirect('/admin')


    event = conn.execute("""
    SELECT * FROM events WHERE id = ?
    """, (event_id,)).fetchone()
    conn.close()
    if not event:
        return "Event findes ikke", 404

    event = dict(event)
    return render_template('edit.html', event=event)



if __name__ == "__main__":
    app.run()

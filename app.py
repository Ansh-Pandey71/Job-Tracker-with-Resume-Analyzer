from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, hashlib, secrets, os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

DB = 'joblens.db'

# ── DB INIT ──────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                email      TEXT UNIQUE NOT NULL,
                password   TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token      TEXT PRIMARY KEY,
                user_id    INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS jobs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                company    TEXT NOT NULL,
                role       TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'Applied',
                date       TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        ''')

init_db()

# ── HELPERS ──────────────────────────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id):
    token = secrets.token_hex(32)
    expires = (datetime.utcnow() + timedelta(days=7)).isoformat()
    with get_db() as conn:
        conn.execute('INSERT INTO sessions (token, user_id, expires_at) VALUES (?,?,?)',
                     (token, user_id, expires))
    return token

def get_user_from_token(token):
    if not token:
        return None
    with get_db() as conn:
        row = conn.execute(
            'SELECT u.* FROM users u JOIN sessions s ON u.id=s.user_id '
            'WHERE s.token=? AND s.expires_at > datetime("now")', (token,)
        ).fetchone()
    return row

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user  = get_user_from_token(token)
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(user, *args, **kwargs)
    return decorated

def job_to_dict(j):
    return {
        'id':      j['id'],
        'company': j['company'],
        'role':    j['role'],
        'status':  j['status'],
        'date':    j['date'] or '',
    }

# ── AUTH ROUTES ──────────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data     = request.get_json()
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    try:
        with get_db() as conn:
            conn.execute('INSERT INTO users (email, password) VALUES (?,?)',
                         (email, hash_password(password)))
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 409

    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()

    token = create_token(user['id'])
    return jsonify({'token': token, 'email': email}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE email=? AND password=?',
                            (email, hash_password(password))).fetchone()

    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_token(user['id'])
    return jsonify({'token': token, 'email': email}), 200


@app.route('/api/logout', methods=['POST'])
@token_required
def logout(user):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    with get_db() as conn:
        conn.execute('DELETE FROM sessions WHERE token=?', (token,))
    return jsonify({'message': 'Logged out'}), 200


@app.route('/api/me', methods=['GET'])
@token_required
def me(user):
    with get_db() as conn:
        total     = conn.execute('SELECT COUNT(*) FROM jobs WHERE user_id=?', (user['id'],)).fetchone()[0]
        interview = conn.execute("SELECT COUNT(*) FROM jobs WHERE user_id=? AND status='Interview'", (user['id'],)).fetchone()[0]
        selected  = conn.execute("SELECT COUNT(*) FROM jobs WHERE user_id=? AND status='Selected'", (user['id'],)).fetchone()[0]
    return jsonify({
        'email':      user['email'],
        'created_at': user['created_at'],
        'stats': {'applied': total, 'interview': interview, 'selected': selected}
    })

# ── JOBS ROUTES ──────────────────────────────────────────────────────────

@app.route('/api/jobs', methods=['GET'])
@token_required
def get_jobs(user):
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM jobs WHERE user_id=? ORDER BY created_at DESC', (user['id'],)
        ).fetchall()
    return jsonify([job_to_dict(r) for r in rows])


@app.route('/api/jobs', methods=['POST'])
@token_required
def add_job(user):
    data    = request.get_json()
    company = (data.get('company') or '').strip()
    role    = (data.get('role') or '').strip()
    status  = data.get('status', 'Applied')
    date    = data.get('date') or datetime.utcnow().strftime('%Y-%m-%d')

    if not company or not role:
        return jsonify({'error': 'Company and role are required'}), 400
    if status not in ('Applied', 'Interview', 'Selected'):
        return jsonify({'error': 'Invalid status'}), 400

    with get_db() as conn:
        cur = conn.execute(
            'INSERT INTO jobs (user_id, company, role, status, date) VALUES (?,?,?,?,?)',
            (user['id'], company, role, status, date)
        )
        job_id = cur.lastrowid
        job    = conn.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()

    return jsonify(job_to_dict(job)), 201


@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@token_required
def delete_job(user, job_id):
    with get_db() as conn:
        row = conn.execute('SELECT * FROM jobs WHERE id=? AND user_id=?',
                           (job_id, user['id'])).fetchone()
        if not row:
            return jsonify({'error': 'Job not found'}), 404
        conn.execute('DELETE FROM jobs WHERE id=?', (job_id,))
    return jsonify({'message': 'Deleted'}), 200


@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
@token_required
def update_job(user, job_id):
    data   = request.get_json()
    status = data.get('status')
    if status not in ('Applied', 'Interview', 'Selected'):
        return jsonify({'error': 'Invalid status'}), 400
    with get_db() as conn:
        row = conn.execute('SELECT * FROM jobs WHERE id=? AND user_id=?',
                           (job_id, user['id'])).fetchone()
        if not row:
            return jsonify({'error': 'Job not found'}), 404
        conn.execute('UPDATE jobs SET status=? WHERE id=?', (status, job_id))
        job = conn.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
    return jsonify(job_to_dict(job))

# ── SERVE FRONTEND ───────────────────────────────────────────────────────

@app.route('/')
@app.route('/login')
def serve_login():
    return send_from_directory('templates', 'login.html')

@app.route('/register')
def serve_register():
    return send_from_directory('templates', 'register.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory('templates', 'index.html')

# ── RUN ──────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)

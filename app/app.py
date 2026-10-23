from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Stockage des tâches en mémoire (pour environnement de démo / lab).
# En production, remplacer par une base de données persistante (ex: PostgreSQL + SQLAlchemy).
# ---------------------------------------------------------------------------
tasks = []
task_id_counter = 1

# ============================================================
# TEMPLATES HTML
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestionnaire de Tâches - DevOps Todo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .add-task {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }
        .add-task form { display: flex; gap: 10px; }
        .add-task input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .add-task input:focus { outline: none; border-color: #667eea; }
        .add-task button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .add-task button:hover { transform: translateY(-2px); }
        .tasks-list { padding: 30px; }
        .task-item {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.3s;
            animation: slideIn 0.3s ease;
        }
        .task-item:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateX(5px);
        }
        .task-content { flex: 1; display: flex; align-items: center; gap: 15px; }
        .task-checkbox { width: 24px; height: 24px; cursor: pointer; }
        .task-text { font-size: 16px; color: #333; }
        .task-text.completed { text-decoration: line-through; color: #999; }
        .task-date { font-size: 12px; color: #999; margin-left: 10px; }
        .task-actions { display: flex; gap: 10px; }
        .delete-btn {
            background: #ff4757; color: white; border: none;
            padding: 5px 15px; border-radius: 5px; cursor: pointer;
            transition: background 0.3s;
        }
        .delete-btn:hover { background: #ff3838; }
        .edit-btn {
            background: #ffa502; color: white; border: none;
            padding: 5px 15px; border-radius: 5px; cursor: pointer;
            transition: background 0.3s;
        }
        .edit-btn:hover { background: #ff9500; }
        .stats {
            background: #f8f9fa; padding: 20px 30px;
            display: flex; justify-content: space-between;
            border-top: 1px solid #e0e0e0;
        }
        .stats div { text-align: center; }
        .stats-number { font-size: 24px; font-weight: bold; color: #667eea; }
        .stats-label { font-size: 12px; color: #666; margin-top: 5px; }
        .empty-state { text-align: center; padding: 40px; color: #999; }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to   { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 Gestionnaire de Tâches</h1>
            <p>Organisez vos tâches efficacement</p>
        </div>

        <div class="add-task">
            <form method="POST" action="/add">
                <input type="text" name="task" placeholder="Ajouter une nouvelle tâche..." required maxlength="200">
                <button type="submit">➕ Ajouter</button>
            </form>
        </div>

        <div class="tasks-list">
            {% if tasks %}
                {% for task in tasks %}
                <div class="task-item">
                    <div class="task-content">
                        <form method="POST" action="/toggle/{{ task.id }}" style="margin: 0;">
                            <input type="checkbox" class="task-checkbox" onchange="this.form.submit()" {% if task.completed %}checked{% endif %}>
                        </form>
                        <div>
                            <span class="task-text {% if task.completed %}completed{% endif %}">{{ task.title }}</span>
                            <span class="task-date">{{ task.date }}</span>
                        </div>
                    </div>
                    <div class="task-actions">
                        <form method="GET" action="/edit/{{ task.id }}" style="margin: 0;">
                            <button type="submit" class="edit-btn">✏️ Modifier</button>
                        </form>
                        <form method="POST" action="/delete/{{ task.id }}" style="margin: 0;">
                            <button type="submit" class="delete-btn">🗑️ Supprimer</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <p>✨ Aucune tâche pour le moment</p>
                    <p>Ajoutez votre première tâche ci-dessus !</p>
                </div>
            {% endif %}
        </div>

        <div class="stats">
            <div>
                <div class="stats-number">{{ total_tasks }}</div>
                <div class="stats-label">Total des tâches</div>
            </div>
            <div>
                <div class="stats-number">{{ completed_tasks }}</div>
                <div class="stats-label">Tâches complétées</div>
            </div>
            <div>
                <div class="stats-number">{{ pending_tasks }}</div>
                <div class="stats-label">Tâches en cours</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

EDIT_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modifier la tâche</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex; justify-content: center; align-items: center; padding: 20px;
        }
        .container {
            max-width: 500px; width: 100%; background: white;
            border-radius: 20px; padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #667eea; margin-bottom: 20px; text-align: center; }
        input {
            width: 100%; padding: 12px; border: 2px solid #e0e0e0;
            border-radius: 10px; font-size: 16px; margin-bottom: 20px;
        }
        input:focus { outline: none; border-color: #667eea; }
        button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 10px;
            cursor: pointer; font-size: 16px; margin-right: 10px;
        }
        a {
            text-decoration: none; padding: 12px 30px;
            background: #999; color: white; border-radius: 10px; display: inline-block;
        }
        .buttons { text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✏️ Modifier la tâche</h1>
        <form method="POST" action="/update/{{ task.id }}">
            <input type="text" name="task" value="{{ task.title }}" required maxlength="200">
            <div class="buttons">
                <button type="submit">💾 Enregistrer</button>
                <a href="/">❌ Annuler</a>
            </div>
        </form>
    </div>
</body>
</html>
"""

ABOUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>À propos - DevOps Todo App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex; justify-content: center; align-items: center; padding: 20px;
        }
        .container {
            max-width: 600px; width: 100%; background: white;
            border-radius: 20px; padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #667eea; margin-bottom: 20px; }
        p { color: #555; line-height: 1.6; margin-bottom: 15px; }
        .badge {
            display: inline-block; background: #f0f0f0;
            border-radius: 5px; padding: 4px 10px;
            font-size: 13px; margin: 3px; color: #444;
        }
        a {
            display: inline-block; margin-top: 20px; padding: 10px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; text-decoration: none; border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 À propos du projet</h1>
        <p>
            <strong>DevOps Todo App</strong> est une API REST construite avec Flask
            et déployée via un pipeline CI/CD complet sur Kubernetes (AWS EC2).
        </p>
        <p><strong>Stack technique :</strong></p>
        <p>
            <span class="badge">Python / Flask</span>
            <span class="badge">Docker</span>
            <span class="badge">Kubernetes</span>
            <span class="badge">GitHub Actions</span>
            <span class="badge">Terraform</span>
            <span class="badge">Ansible</span>
            <span class="badge">AWS EC2</span>
        </p>
        <p>
            Ce projet illustre l'automatisation complète du cycle de développement :
            du code source jusqu'au déploiement en production.
        </p>
        <a href="/">← Retour à l'application</a>
    </div>
</body>
</html>
"""

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task['completed'])
    pending_tasks = total_tasks - completed_tasks
    return render_template_string(
        HTML_TEMPLATE,
        tasks=tasks[::-1],
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks
    )


@app.route('/about')
def about():
    return render_template_string(ABOUT_TEMPLATE)


@app.route('/health')
def health():
    """Endpoint de santé utilisé par les liveness/readiness probes Kubernetes."""
    return jsonify({'status': 'ok', 'tasks_count': len(tasks)}), 200


@app.route('/add', methods=['POST'])
def add_task():
    global task_id_counter
    title = request.form.get('task', '').strip()
    if title:
        tasks.append({
            'id': task_id_counter,
            'title': title[:200],
            'completed': False,
            'date': datetime.now().strftime('%d/%m/%Y %H:%M')
        })
        task_id_counter += 1
    return redirect(url_for('index'))


@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return redirect(url_for('index'))


@app.route('/edit/<int:task_id>')
def edit_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        return render_template_string(EDIT_TEMPLATE, task=task)
    return redirect(url_for('index'))


@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    new_title = request.form.get('task', '').strip()
    for task in tasks:
        if task['id'] == task_id:
            if new_title:
                task['title'] = new_title[:200]
            break
    return redirect(url_for('index'))


# ============================================================
# API REST (JSON)
# ============================================================

@app.route('/api/tasks')
def api_tasks():
    """Retourne la liste complète des tâches en JSON."""
    return jsonify(tasks), 200


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def api_get_task(task_id):
    """Retourne une tâche spécifique par son ID."""
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        return jsonify(task), 200
    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/stats')
def api_stats():
    """Retourne les statistiques globales des tâches."""
    return jsonify({
        'total': len(tasks),
        'completed': sum(1 for t in tasks if t['completed']),
        'pending': sum(1 for t in tasks if not t['completed'])
    }), 200


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)

import pytest
from app import app


@pytest.fixture
def client():
    """Client de test Flask avec isolation des données."""
    app.config['TESTING'] = True
    # Réinitialiser les tâches avant chaque test pour garantir l'isolation
    import app as app_module
    app_module.tasks.clear()
    app_module.task_id_counter = 1
    with app.test_client() as client:
        yield client


# ============================================================
# Tests des pages HTML
# ============================================================

def test_home_page_returns_200(client):
    """La page d'accueil doit retourner un HTTP 200."""
    response = client.get('/')
    assert response.status_code == 200


def test_about_page_returns_200(client):
    """La page 'À propos' doit retourner un HTTP 200."""
    response = client.get('/about')
    assert response.status_code == 200


def test_home_page_contains_title(client):
    """La page d'accueil doit contenir le titre de l'application."""
    response = client.get('/')
    assert b'Gestionnaire' in response.data


# ============================================================
# Tests de l'endpoint de santé
# ============================================================

def test_health_endpoint(client):
    """L'endpoint /health doit retourner status ok."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'


# ============================================================
# Tests de l'API REST
# ============================================================

def test_api_tasks_returns_empty_list(client):
    """L'API doit retourner une liste vide au démarrage."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert response.get_json() == []


def test_api_stats_initial(client):
    """Les stats doivent être à zéro au démarrage."""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] == 0
    assert data['completed'] == 0
    assert data['pending'] == 0


def test_api_task_not_found(client):
    """Une tâche inexistante doit retourner 404."""
    response = client.get('/api/tasks/999')
    assert response.status_code == 404


# ============================================================
# Tests CRUD des tâches
# ============================================================

def test_add_task(client):
    """Ajouter une tâche doit la rendre visible sur la page d'accueil."""
    response = client.post('/add', data={'task': 'Déployer sur Kubernetes'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Kubernetes' in response.data


def test_add_task_appears_in_api(client):
    """Une tâche ajoutée doit apparaître dans l'API /api/tasks."""
    client.post('/add', data={'task': 'Configurer Terraform'})
    response = client.get('/api/tasks')
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['title'] == 'Configurer Terraform'
    assert data[0]['completed'] is False


def test_add_empty_task_ignored(client):
    """Une tâche vide ne doit pas être ajoutée."""
    client.post('/add', data={'task': '   '})
    response = client.get('/api/tasks')
    assert response.get_json() == []


def test_toggle_task(client):
    """Basculer le statut d'une tâche doit la marquer comme complétée."""
    client.post('/add', data={'task': 'Tâche à compléter'})
    response = client.get('/api/tasks')
    task_id = response.get_json()[0]['id']

    client.post(f'/toggle/{task_id}')
    response = client.get('/api/tasks')
    assert response.get_json()[0]['completed'] is True


def test_delete_task(client):
    """Supprimer une tâche doit la retirer de la liste."""
    client.post('/add', data={'task': 'Tâche à supprimer'})
    response = client.get('/api/tasks')
    task_id = response.get_json()[0]['id']

    client.post(f'/delete/{task_id}')
    response = client.get('/api/tasks')
    assert response.get_json() == []


def test_update_task(client):
    """Mettre à jour une tâche doit modifier son titre."""
    client.post('/add', data={'task': 'Ancien titre'})
    response = client.get('/api/tasks')
    task_id = response.get_json()[0]['id']

    client.post(f'/update/{task_id}', data={'task': 'Nouveau titre'})
    response = client.get('/api/tasks')
    assert response.get_json()[0]['title'] == 'Nouveau titre'


def test_stats_after_operations(client):
    """Les statistiques doivent refléter l'état réel des tâches."""
    client.post('/add', data={'task': 'Tâche 1'})
    client.post('/add', data={'task': 'Tâche 2'})
    response = client.get('/api/tasks')
    task_id = response.get_json()[0]['id']
    client.post(f'/toggle/{task_id}')

    stats = client.get('/api/stats').get_json()
    assert stats['total'] == 2
    assert stats['completed'] == 1
    assert stats['pending'] == 1

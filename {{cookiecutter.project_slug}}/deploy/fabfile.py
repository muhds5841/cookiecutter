from fabric import Connection, task


@task
def deploy(ctx, env="production", version=None):
    """Deploy aplikacji na serwer produkcyjny przez SSH."""
    conn = Connection("ssh.example.com")

    # Pobierz najnowszą wersję z repozytorium
    with conn.cd("/opt/tts-project"):
        conn.run("git pull")

        # Aktualizacja zależności
        conn.run("poetry install --no-dev")

        # Budowanie i uruchamianie kontenerów
        conn.run("docker-compose -f docker-compose.prod.yml build")
        conn.run("docker-compose -f docker-compose.prod.yml up -d")

        # Wykonanie migracji, jeśli potrzebne
        # conn.run('docker-compose -f docker-compose.prod.yml exec web python manage.py migrate')

        # Czyszczenie nieużywanych obrazów
        conn.run("docker system prune -af")

#!/usr/bin/env python3
"""Deploy a successful GitLab pipeline's immutable Docker Hub image on the LAN."""

import argparse
import datetime
import gzip
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.request


PROJECT = Path(__file__).resolve().parents[1]
PRIVATE = PROJECT / '.deployment'
DROPIN = Path('/etc/systemd/system/thrdlabapp.service.d/20-container.conf')
SERVICE = 'thrdlabapp.service'
REPOSITORY = 'sergemmikh/thrdlabapp-devsecops-diploma'
API = 'https://gitlab.com/api/v4/projects/86156932'
APP_KEYS = {
    'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'SECRET_KEY', 'DEBUG',
    'ALLOWED_HOSTS', 'CSRF_TRUSTED_ORIGINS', 'EM_HOST', 'EM_HOST_USER',
    'EM_HOST_PASSWORD', 'EM_PORT', 'EM_USE_TLS',
}
SECRETS = []
COUNTS = '''import os, json, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from django.apps import apps
labels = ('users.User', 'users.Person', 'furnace_booking.Laboratory',
          'furnace_booking.Furnace', 'furnace_booking.Equipment',
          'furnace_booking.BookingOfFurnace',
          'furnace_booking.BookingOfEquipment', 'news.Articles')
print(json.dumps({label: apps.get_model(label).objects.count() for label in labels}))
'''


def read_env(path):
    """Read the single-line dotenv format used by python-decouple; never eval it."""
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key, value = key.strip(), value.strip()
        if key.startswith('export '):
            key = key[7:].strip()
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        values[key] = value
    return values


def redact(message):
    for secret in SECRETS:
        if secret:
            message = message.replace(secret, '[REDACTED]')
    return message


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(redact((result.stdout + result.stderr)[-3000:]))
    return result.stdout.strip()


def private_text(path, content):
    path.write_text(content)
    path.chmod(0o600)


def write_env(path, values):
    if any('\n' in value or '\r' in value for value in values.values()):
        raise ValueError('Multiline environment values are not supported.')
    private_text(path, ''.join(f'{key}={value}\n' for key, value in values.items()))


def api(path, token):
    request = urllib.request.Request(
        API + path, headers={'PRIVATE-TOKEN': token},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def verified_commit(pipeline_id, token):
    pipeline = api(f'/pipelines/{pipeline_id}', token)
    if pipeline['status'] != 'success' or pipeline['ref'] != 'main':
        raise ValueError('Only a successful main pipeline may be deployed.')
    jobs = api(f'/pipelines/{pipeline_id}/jobs?per_page=100', token)
    if not jobs or any(job['status'] != 'success' for job in jobs):
        raise ValueError('Every job, including advisory scanners, must succeed.')
    commit = pipeline['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Invalid pipeline commit.')
    local = run('git', '-C', str(PROJECT), 'rev-parse', 'HEAD')
    if local != commit:
        raise ValueError('Run git pull first: local code must match the pipeline.')
    return commit


def immutable_image(commit):
    tag = f'{REPOSITORY}:{commit[:8]}'
    print(f'Pulling verified artifact {tag}...', flush=True)
    run('docker', 'pull', tag)
    image = json.loads(run('docker', 'image', 'inspect', tag))[0]
    labels = image['Config'].get('Labels') or {}
    if labels.get('org.opencontainers.image.revision') != commit:
        raise ValueError('Image revision label does not match the tested commit.')
    digest = next((item for item in image['RepoDigests']
                   if item.startswith(REPOSITORY + '@sha256:')), '')
    if not re.fullmatch(re.escape(REPOSITORY) + r'@sha256:[0-9a-f]{64}', digest):
        raise ValueError('Could not resolve the immutable image digest.')
    return digest


def db_network(container):
    info = json.loads(run('docker', 'inspect', container))[0]
    if not info['State']['Running']:
        raise ValueError('The existing PostgreSQL container is not running.')
    networks = info['NetworkSettings']['Networks']
    if len(networks) != 1:
        raise ValueError('Select the database network explicitly before deploying.')
    return next(iter(networks))


def runtime_env(source, container):
    values = {key: value for key, value in source.items() if key in APP_KEYS}
    values.update(PGHOST=container, PGPORT='5432')
    values.setdefault('DEBUG', 'false')
    hosts = values.get('ALLOWED_HOSTS', '192.168.1.160').split(',')
    values['ALLOWED_HOSTS'] = ','.join(dict.fromkeys(
        [host.strip() for host in hosts] + ['127.0.0.1', 'localhost'],
    ))
    values.setdefault('CSRF_TRUSTED_ORIGINS', 'http://192.168.1.160')
    if not all(values.get(key) for key in ('PGDATABASE', 'PGUSER', 'PGPASSWORD')):
        raise ValueError('Database settings are incomplete in .env.')
    return values


def image_command(state, *command):
    return run(
        'docker', 'run', '--rm', '--network', state['network'],
        '--env-file', state['runtime_env'], '--read-only',
        '--tmpfs', '/tmp:rw,nosuid,noexec,size=64m', '--cap-drop', 'ALL',
        '--security-opt', 'no-new-privileges:true', state['image'], *command,
    )


def extract_static(state):
    destination = Path(state['static'])
    destination.mkdir(mode=0o755)
    destination.chmod(0o755)
    container = run('docker', 'create', state['image'])
    try:
        run('docker', 'cp', f'{container}:/app/staticfiles/.', str(destination))
    finally:
        run('docker', 'rm', container)
    for path in destination.rglob('*'):
        path.chmod(0o755 if path.is_dir() else 0o644)
    if not (destination / 'main/img/neon-electrochemistry-lab-badge.png').is_file():
        raise ValueError('The published image does not contain collected static files.')


def save_controls(release):
    controls = {'static_changed': False}
    for name, path in (
        ('dropin', DROPIN), ('active', PRIVATE / 'active.env'),
        ('compose', PRIVATE / 'active.compose.yaml'),
        ('state', PRIVATE / 'state.json'),
    ):
        controls[name] = path.exists()
        if path.exists():
            shutil.copyfile(path, release / f'{name}.before')
            (release / f'{name}.before').chmod(0o600)
    private_text(release / 'controls.json', json.dumps(controls, indent=2))
    return controls


def backup_database(container, release):
    dump = release / 'postgres-all.sql.gz'
    with subprocess.Popen(
        ['docker', 'exec', '-u', 'postgres', container, 'pg_dumpall'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ) as process:
        with gzip.open(dump, 'wb', compresslevel=6) as stream:
            shutil.copyfileobj(process.stdout, stream)
        error = process.stderr.read().decode()
        if process.wait():
            raise RuntimeError('Database backup failed: ' + redact(error))
    with gzip.open(dump, 'rb') as stream:
        while stream.read(1024 * 1024):
            pass
    dump.chmod(0o600)


def activate_static(state, controls, release):
    active = PROJECT / 'staticfiles'
    if active.is_symlink() or not active.is_dir():
        raise ValueError('Expected the tracked staticfiles directory.')
    previous = PROJECT / 'static-releases' / ('previous-' + release.name)
    active.rename(previous)
    controls.update(static_changed=True, previous_static=str(previous))
    private_text(release / 'controls.json', json.dumps(controls, indent=2))
    Path(state['static']).rename(active)
    state['static'] = str(active)


def install_service(release):
    source = PROJECT / 'deploy/thrdlabapp-container.conf'
    target = release / 'container.conf'
    private_text(target, source.read_text().replace('@PROJECT_DIR@', str(PROJECT)))
    run('sudo', '-n', 'install', '-d', '-m', '755', str(DROPIN.parent))
    run('sudo', '-n', 'install', '-m', '644', str(target), str(DROPIN))
    run('sudo', '-n', 'systemctl', 'daemon-reload')


def compose(*command):
    return run(
        'docker', 'compose', '--project-name', 'thrdlabapp-lan',
        '--env-file', str(PRIVATE / 'active.env'),
        '-f', str(PRIVATE / 'active.compose.yaml'), *command,
    )


def healthy(expected_image):
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        containers = compose('ps', '--all', '--quiet', 'web').splitlines()
        for container in containers:
            try:
                info = json.loads(run('docker', 'inspect', container))[0]
            except RuntimeError:
                # Compose can list both generations while replacing a container;
                # the old ID may disappear between ps and inspect.
                continue
            if info['Config']['Image'] != expected_image:
                continue
            health = info['State'].get('Health', {}).get('Status')
            if health == 'healthy':
                names = {item.split('=', 1)[0] for item in info['Config']['Env']}
                if 'GITLAB_TOKEN' in names:
                    raise ValueError('GitLab token leaked into the app environment.')
                return container
        time.sleep(1)
    raise RuntimeError('Application did not become healthy within 90 seconds.')


def check_pages():
    paths = ('/', '/furnaces/', '/furnaces/furnace-booking/',
             '/furnaces/equipments/', '/furnaces/equipment-booking/',
             '/admin/login/', '/static/main/img/neon-electrochemistry-lab-badge.png')
    for path in paths:
        with urllib.request.urlopen(
            'http://192.168.1.160' + path, timeout=10,
        ) as response:
            if response.status != 200:
                raise RuntimeError('HTTP verification failed for ' + path)
    return list(paths)


def restore(release):
    controls = json.loads((release / 'controls.json').read_text())
    run('sudo', '-n', 'systemctl', 'stop', SERVICE)
    if (PRIVATE / 'active.env').exists():
        compose('stop', '--timeout', '30', 'web')
    if controls['static_changed']:
        active = PROJECT / 'staticfiles'
        if active.is_symlink() or (active.exists() and not active.is_dir()):
            raise RuntimeError('Refusing to replace an unexpected static directory.')
        if active.exists():
            stamp = str(time.time_ns())
            active.rename(PROJECT / 'static-releases' / ('rolled-back-' + stamp))
        Path(controls['previous_static']).rename(active)
    for name, filename in (
        ('active', 'active.env'), ('compose', 'active.compose.yaml'),
        ('state', 'state.json'),
    ):
        target = PRIVATE / filename
        if controls[name]:
            shutil.copyfile(release / f'{name}.before', target)
            target.chmod(0o600)
        else:
            target.unlink(missing_ok=True)
    if controls['dropin']:
        run('sudo', '-n', 'install', '-m', '644',
            str(release / 'dropin.before'), str(DROPIN))
    else:
        run('sudo', '-n', 'rm', '-f', str(DROPIN))
    run('sudo', '-n', 'systemctl', 'daemon-reload')
    run('sudo', '-n', 'systemctl', 'start', SERVICE)
    if controls['state']:
        state = json.loads((PRIVATE / 'state.json').read_text())
        state['container'] = healthy(state['image'])
        state['http_checks'] = check_pages()
        private_text(PRIVATE / 'state.json', json.dumps(state, indent=2) + '\n')
    print('Previous application, service settings and static files restored.', flush=True)


def prepare(source, pipeline_id, container):
    commit = verified_commit(pipeline_id, source.get('GITLAB_TOKEN', ''))
    image = immutable_image(commit)
    network = db_network(container)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    name = stamp + '-' + commit[:8]
    release = PRIVATE / name
    release.mkdir(mode=0o700)
    state = {'commit': commit, 'pipeline': pipeline_id, 'image': image,
             'network': network, 'release': str(release),
             'runtime_env': str(release / 'runtime.env'),
             'static': str(PROJECT / 'static-releases' / name)}
    write_env(Path(state['runtime_env']), runtime_env(source, container))
    extract_static(state)
    image_command(state, 'python', 'manage.py', 'check')
    image_command(state, 'python', 'manage.py', 'migrate', '--plan')
    return state, release


def deploy(source, pipeline_id, container):
    state, release = prepare(source, pipeline_id, container)
    controls = save_controls(release)
    print('Artifact prepared. Stopping service for backup and migration...', flush=True)
    run('sudo', '-n', 'systemctl', 'stop', SERVICE)
    try:
        backup_database(container, release)
        before = json.loads(image_command(state, 'python', '-c', COUNTS))
        image_command(state, 'python', 'manage.py', 'migrate', '--noinput')
        after = json.loads(image_command(state, 'python', '-c', COUNTS))
        if before != after:
            raise RuntimeError('Business record counts changed during migration.')
        activate_static(state, controls, release)
        write_env(PRIVATE / 'active.env', {
            'APP_IMAGE': state['image'], 'APP_RUNTIME_ENV': state['runtime_env'],
            'APP_DB_NETWORK': state['network'],
        })
        private_text(PRIVATE / 'active.compose.yaml',
                     (PROJECT / 'compose.lan.yaml').read_text())
        compose('config', '--quiet')
        install_service(release)
        run('sudo', '-n', 'systemctl', 'start', SERVICE)
        state['container'] = healthy(state['image'])
        state['http_checks'] = check_pages()
        state['counts'] = after
        private_text(PRIVATE / 'state.json', json.dumps(state, indent=2) + '\n')
        private_text(release / 'verified.json', json.dumps(state, indent=2) + '\n')
        print(json.dumps(state, indent=2), flush=True)
    except Exception:
        print('Deployment failed; restoring the previous runtime...', flush=True)
        restore(release)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--pipeline', type=int, help='Successful main pipeline ID')
    choice.add_argument('--rollback', action='store_true', help='Restore prior runtime')
    choice.add_argument('--status', action='store_true', help='Show deployed digest')
    parser.add_argument('--db-container', default='pg-standalone')
    args = parser.parse_args()
    os.umask(0o077)
    if PRIVATE.is_symlink():
        raise ValueError('Deployment state directory must not be a symlink.')
    PRIVATE.mkdir(mode=0o700, exist_ok=True)
    PRIVATE.chmod(0o700)
    static = PROJECT / 'static-releases'
    static.mkdir(mode=0o755, exist_ok=True)
    static.chmod(0o755)
    source = read_env(PROJECT / '.env')
    SECRETS.extend(source.get(key, '') for key in (
        'GITLAB_TOKEN', 'PGPASSWORD', 'SECRET_KEY', 'EM_HOST_PASSWORD',
    ))
    if args.pipeline:
        deploy(source, args.pipeline, args.db_container)
    else:
        state = json.loads((PRIVATE / 'state.json').read_text())
        if args.rollback:
            restore(Path(state['release']))
        else:
            print(json.dumps(state, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        raise SystemExit(redact(str(error)))

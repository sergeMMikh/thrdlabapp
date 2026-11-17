import json

import pytest

from scripts import deploy_lan


def test_runtime_environment_keeps_database_credentials_but_excludes_ci_token():
    values = deploy_lan.runtime_env({
        'GITLAB_TOKEN': 'test-only-ci-token',
        'CI': 'true',
        'DOCKERHUB_TOKEN': 'test-only-registry-token',
        'PGDATABASE': 'lab',
        'PGUSER': 'postgres',
        'PGPASSWORD': 'test-only-db-password',
    }, 'existing-postgres')
    assert values['PGPASSWORD'] == 'test-only-db-password'
    assert values['PGHOST'] == 'existing-postgres'
    assert values['DEBUG'] == 'false'
    assert '127.0.0.1' in values['ALLOWED_HOSTS']
    assert not {'GITLAB_TOKEN', 'DOCKERHUB_TOKEN', 'CI'} & values.keys()


def test_static_update_and_rollback_preserve_the_tracked_directory(
    tmp_path, monkeypatch,
):
    monkeypatch.setattr(deploy_lan, 'PROJECT', tmp_path)
    private = tmp_path / '.deployment'
    private.mkdir()
    compose_snapshot = private / 'active.compose.yaml'
    compose_snapshot.write_text('previous-compose-config')
    monkeypatch.setattr(deploy_lan, 'PRIVATE', private)
    monkeypatch.setattr(deploy_lan, 'DROPIN', tmp_path / 'test-container.conf')
    monkeypatch.setattr(deploy_lan, 'run', lambda *args: '')
    active = tmp_path / 'staticfiles'
    active.mkdir()
    (active / '.gitkeep').write_text('')
    (active / 'logo.png').write_bytes(b'original-logo')
    archives = tmp_path / 'static-releases'
    archives.mkdir()
    candidate = archives / 'candidate'
    candidate.mkdir()
    (candidate / '.gitkeep').write_text('')
    (candidate / 'logo.png').write_bytes(b'updated-logo')
    release = private / 'release'
    release.mkdir()
    controls = deploy_lan.save_controls(release)
    state = {'static': str(candidate)}

    deploy_lan.activate_static(state, controls, release)
    compose_snapshot.write_text('new-compose-config')
    assert active.is_dir() and not active.is_symlink()
    assert (active / '.gitkeep').is_file()
    assert (active / 'logo.png').read_bytes() == b'updated-logo'

    deploy_lan.restore(release)
    assert active.is_dir() and not active.is_symlink()
    assert (active / '.gitkeep').is_file()
    assert (active / 'logo.png').read_bytes() == b'original-logo'
    assert compose_snapshot.read_text() == 'previous-compose-config'


def test_deployment_rejects_an_allowed_failure_in_the_pipeline(monkeypatch):
    def fake_api(path, token):
        if path.endswith('/jobs?per_page=100'):
            return [{'status': 'failed', 'allow_failure': True}]
        return {'status': 'success', 'ref': 'main', 'sha': 'a' * 40}

    monkeypatch.setattr(deploy_lan, 'api', fake_api)
    with pytest.raises(ValueError, match='Every job'):
        deploy_lan.verified_commit(123, 'test-only-token')


def test_deployment_rejects_an_image_with_the_wrong_revision(monkeypatch):
    def fake_run(*args):
        if args[1:3] == ('image', 'inspect'):
            return json.dumps([{'Config': {'Labels': {
                'org.opencontainers.image.revision': 'b' * 40,
            }}}])
        return ''

    monkeypatch.setattr(deploy_lan, 'run', fake_run)
    with pytest.raises(ValueError, match='revision label'):
        deploy_lan.immutable_image('a' * 40)

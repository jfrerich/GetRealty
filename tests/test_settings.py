from getrealty import settings


def test_hash_global_setup():
    '''simple test to check hash_global setup correctly'''
    assert settings.hash_global['cache'] == {}

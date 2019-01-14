import lib.settings


def test_hash_global_setup():
    '''simple test to check hash_global setup correctly'''
    assert lib.settings.hash_global['cache'] == {}

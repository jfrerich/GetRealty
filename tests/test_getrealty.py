from getrealty import settings
from getrealty import GetRealty
import logging

config = settings.config


def test_fail_duplicate_rnumbers(caplog):
    # from getrealty import checkDuplicateRnumbers

    config['defaults']['RNUMBERS'] = "M95907 R72216 R72216 R38491"

    getrealty.checkDuplicateRnumbers()

    for record in caplog.records:

        assert caplog.record_tuples == [
            ('root', logging.ERROR, ('The following -rnumbers have duplicates.'
                                     ' Remove the duplicates')),
            ('root', logging.ERROR, 'R72216'),
        ]

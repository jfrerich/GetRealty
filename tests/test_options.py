from getrealty import settings, options
import pytest


config = settings.config

# @pytest.fixture
# def smtp_connection():
    # import smtplib
    # return smtplib.SMTP("smtp.gmail.com", 587, timeout=5)


def test_getCounty():

    assert config['defaults']['COUNTY'] == 'Bastrop'

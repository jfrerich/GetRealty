from getrealty import settings, webdata, createAdditionalInfo
import pytest

config = settings.config
hash_global = settings.hash_global


@pytest.mark.parametrize("rnum, expected", [
    ('R53752', (0,)),
    ('R56917', (0,)),
    ('R84783', (1, '2012/09/14')),
])
def test_enhance_readDatasheet(rnum, expected):
    pdf = 'DATASHEET_PAGE.pdf'
    xml = 'DATASHEET_PAGE.xml'
    test_file = 'test_files/test_enhance_readDatasheet/' + rnum + '/' + xml
    hash_global['DBWriteValues'].update({rnum: {pdf: {}}})
    webdata.readRnumDataSheetPageResponseData(rnum, pdf, test_file)
    assert (hash_global['DBWriteValues'][rnum][pdf]['NumTimesSold']
            == expected[0])
    if len(expected) > 1:
        assert (hash_global['DBWriteValues'][rnum][pdf]['LastTimeSold']
                == expected[1])


def test_getDetailMainEntries():
    html = 'PROP_DETAIL_RESULTS.html'

    rnum = 'R49589'
    test_file = 'test_files/test_getDetailMainEntries/' + html

    # hash_global['DBWriteValues'].update({rnum: {pdf: {}}})
    hash_global['DBWriteValues'].update({'R49589': {html: {}}})
    webdata.getDetailMainEntries(rnum, html, test_file)
    assert (
        hash_global['DBWriteValues'][rnum][html]['bills_link'] == (
            'http://www.bastroptac.com'
            '/Appraisal/PublicAccess/PropertyBills.aspx?'
            'PropertyID=49463&PropertyOwnerID=234696&NodeID=11'))

    assert(
        hash_global['DBWriteValues'][rnum][html]['details_link'] == (
            'http://www.bastroptac.com/'
            'Appraisal/PublicAccess/PropertyDetail.aspx?'
            'PropertyID=49463&PropertyOwnerID=234696'
            '&dbKeyAuth=Appraisal&TaxYear=2013&NodeID=11'))


def test_bug9():
    from getrealty.createAdditionalInfo import createDaysLate
    from getrealty.webdata import readRnumBillsPageResponseData
    #  - Last year paid doesn't match year from last date paid.
    #    This was correct.  Last year Paid doesn't have to be same as
    #    last date paid. possible to pay 2004 taxes in 2008
    html = 'BILL_PAGE_RESULTS.html'
    hash_global['DBWriteValues'].update({'R23357':
                                         {html: {}}})
    readRnumBillsPageResponseData('R23357',
                                  html,
                                  'test_files/test_bug9/' + html)
    assert createDaysLate('R23357',
                          'calcs',
                          'BILL_PAGE_RESULTS.html') == (2484, 10000,
                                                        '2004', '2008/09/30',
                                                        0, '2005')


@pytest.mark.parametrize("rnum, test_file, expected", [
    #  test_bug12 - calculating pct address diff cannot have ( or ) or /
    #               in the address. tests Different___State
    ('R49589', 'test_bug12', ('0.57', '1', '0', '0')),
    #  test_bug14 - wilco TimesSold/Last comes up as persons name... fixed..
    #               look for mm/dd/yyyy instead of counting lines. some entries
    #                don't have Volume or Page
    ('R035158', 'test_bug14', ('0.27', '1', '1', '0')),
    #  test_bug7 - no Property Address, but can determine a different state
    ('R53752', 'test_bug7/R53752', ('n/a', '1 np', 'n/a', '1 - MD')),
    ('R56917', 'test_bug7/R56917', ('n/a', '1 np', 'n/a', '1 - LA')),
    #  test_bug8 - No Property address means never got a 911 address.
    #              Almost always owner does not live there
    ('R26053', 'test_bug8/R26053', ('n/a', '1 np', 'n/a', '0')),
    ('R51215', 'test_bug8/R51215', ('n/a', '1 np', 'n/a', '0')),
    #  test_bug1 - incorrectly marked out of State because no zip code in
    #              property address
    ('R56984', 'test_bug1/R56984', ('0.69', '1', 'n/a', '0')),
    ('R64215', 'test_bug1/R64215', ('0.79', '1', 'n/a', '0')),
    #  test_bug6 - replace ROAD with RD before matching address
    ('R56922', 'test_bug6', ('0.00', '0', '0', '0')),
    #  test_bug10 - diff state says n/a, but TX is in owner addr
    ('R28871', 'test_bug10', ('0.47', '1', 'n/a', '0')),
    #  test_bug3 - zip code differs because of xxxxx-xxxx vs xxxxx
    ('R53677', 'test_bug3', ('0.00', '0', '0', '0')),
    #  test_bug2 - Incorrectly marked diff addr b/c no owner addr
    ('R522854', 'test_bug2', ('n/a', '0 no', 'n/a', 'n/a'))
])
def test_propAddrSameAsOwnerAddr(rnum, test_file, expected):

    from getrealty.createAdditionalInfo import propAddrSameAsOwnerAddr
    #  - calculating pct address diff cannot have ( or ) or / in the address
    #  tests Different___State
    html = 'PROP_DETAIL_RESULTS.html'
    test_file = 'test_files/' + test_file + '/' + html
    webdata.readRnumDetailPageResponseData(rnum, html, test_file)
    assert propAddrSameAsOwnerAddr(rnum, html) == expected

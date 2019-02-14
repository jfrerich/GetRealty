from getrealty import settings, sqlConnect, printArray

import os

config = settings.config

myPath = os.path.dirname(os.path.abspath(__file__))
myPA = printArray.MyPrintArray()


def test_sqlwherewithpercents():
    config['defaults']['SQL_WHERE'] = 'WHERE OwnerAddr LIKE "%C/O%"'
    config['defaults']['WORK_DIR'] = myPath + \
        '/test_files/test_sql_where_with_percents'
    sql_where = sqlConnect.getSearchSqlDbWhereCommand('r_num,Subd')
    db = sqlConnect.DB()
    db.execute(sql_where)
    results = db.fetchall()
    assert results == [('R38921', 'PINE FOREST UNIT 12 P III'),
                       ('R17815', 'EAGLESTON BLK 22 LOT 4')]


def test_buildTableIfDoesntExistQuery():
    assert sqlConnect.buildTableIfDoesntExistQuery() == 'CREATE TABLE IF NOT EXISTS RNUMBERS_Bastrop         (r_num PRIMARY KEY, rpg TEXT, Property_Interest TEXT, Links___Bills TEXT, Links___Det TEXT, Links___Hist TEXT, Links___Data TEXT, Maps___GIS TEXT, Maps___Map TEXT, NOTES TEXT, Subd TEXT, Prop_Details___Acres TEXT, Prop_Details___AssessVal TEXT, Prop_Details___AssessMinDue TEXT, Tax_Due___PctToAss TEXT, Tax_Due___TotAmtDue TEXT, DatePulled TEXT, TaxDates___OldestDue TEXT, TaxDates___LastPaid TEXT, TaxDates___LastYrPaid TEXT, Different___Addr TEXT, Different___Zip TEXT, Different___State TEXT, NHS_imp TEXT, InstallYr TEXT, TimesSold___Num TEXT, TimesSold___Last TEXT, Appraised___AppPctOfMax TEXT, Appraised___AppLastVal TEXT, Appraised___AppMaxVal TEXT, AppraisedMaxReduced___AppMaxAmt TEXT, AppraisedMaxReduced___AppMaxYr TEXT, Assess___AssPctOfMax TEXT, Assess___AssLastVal TEXT, Assess___AssMaxVal TEXT, AssessMaxReduced___AssMaxAmt TEXT, AssessMaxReduced___AssMaxYr TEXT, ImpNHS___LastPctOfMax TEXT, ImpNHS___LastVal TEXT, ImpNHS___MaxVal TEXT, ImpNHSMaxReduced___MaxAmt TEXT, ImpNHSMaxReduced___MaxYr TEXT, ImpHS___ihsPctOfMax TEXT, ImpHS___ihsLastVal TEXT, ImpHS___ihsMaxVal TEXT, ImpHSMaxReduced___ihsMaxAmt TEXT, ImpHSMaxReduced___ihsMaxYr TEXT, LandHS___lhsPctOfMax TEXT, LandHS___lhsLastVal TEXT, LandHS___lhsMaxVal TEXT, LandHSMaxReduced___lhsMaxAmt TEXT, LandHSMaxReduced___lhsMaxYr TEXT, LandNHS___lnhsPctOfMax TEXT, LandNHS___lnhsLastVal TEXT, LandNHS___lnhsMaxVal TEXT, LandNHSMaxReduced___lnhsMaxAmt TEXT, LandNHSMaxReduced___lnhsMaxYr TEXT, DaysLate___Curr TEXT, DaysLate___Max TEXT, PctDiffAddr TEXT, PropAddr TEXT, OwnerAddr TEXT, OwnerName TEXT, LegalDesc TEXT)'


def test_search_db():
    config['defaults']['SQL_WHERE'] = False
    config['defaults']['SQL_SEARCH'] = "Different___Zip:!0, " \
        "Different___State:!0, Prop_Details___Acres:1:2, " \
        "Prop_Details___AssessVal:30000:, TaxDates___LastYrPaid:2012:"
    config['defaults']['WORK_DIR'] = myPath + '/test_files/test_search_db'
    sql_where = sqlConnect.getSearchSqlDbWhereCommand("r_num, "
                                                      "NOTES_rnum_sheet, "
                                                      "NOTES, "
                                                      "Property_Interest")
    db = sqlConnect.DB()
    db.execute(sql_where)
    results = db.fetchall()
    assert results == [('R51011', '', '', 'Not Vetted'),
                       ('R55676', '', '', 'Not Vetted'),
                       ('R64204', '', '', 'Not Vetted'),
                       ('R48687', '', '', 'Not Vetted'),
                       ('R24342', '', '', 'Not Vetted'),
                       ('R59232', '', '', 'Not Vetted'),
                       ('R73481', '', '', 'Not Vetted'),
                       ('R45247', '', '', 'Not Vetted'),
                       ('R35823', '', '', 'Not Vetted')]


def test_search_db_rnumbers():
    config['defaults']['SQL_WHERE'] = False
    config['defaults']['SQL_SEARCH'] = 'OR::r_num::R53752:R56917'
    config['defaults']['WORK_DIR'] = myPath + \
        '/test_files/test_search_db_rnumbers'
    sql_where = sqlConnect.getSearchSqlDbWhereCommand('r_num,Subd')
    db = sqlConnect.DB()
    db.execute(sql_where)
    results = db.fetchall()
    assert results == [('R53752', 'ARTESIAN OAKS SEC 2'),
                       ('R56917', 'ARTESIAN OAKS SEC 3')]

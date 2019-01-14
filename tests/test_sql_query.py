from getrealty import settings, sqlConnect

config = settings.config


def test_sqlwherewithpercents():
    config['defaults']['SQL_WHERE'] = 'WHERE OwnerAddr LIKE "%C/O%"'
    config['defaults']['WORK_DIR'] = 'test_files/test_sql_where_with_percents'
    sql_where = sqlConnect.getSearchSqlDbWhereCommand('r_num,Subd')
    db = sqlConnect.DB()
    db.execute(sql_where)
    results = db.fetchall()
    assert results ==  [('R38921', 'PINE FOREST UNIT 12 P III'), ('R17815', 'EAGLESTON BLK 22 LOT 4')]

def test_search_db():
    config['defaults']['SQL_WHERE'] = False
    config['defaults']['SQL_SEARCH'] = 'Different___Zip:!0, Different___State:!0, Prop_Details___Acres:1:2, Prop_Details___AssessVal:30000:, TaxDates___LastYrPaid:2012:'
    config['defaults']['WORK_DIR'] = 'test_files/test_search_db'
    sql_where = sqlConnect.getSearchSqlDbWhereCommand('r_num,NOTES_rnum_sheet, NOTES, Property_Interest')
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
    config['defaults']['WORK_DIR'] = 'test_files/test_search_db_rnumbers'
    sql_where = sqlConnect.getSearchSqlDbWhereCommand('r_num,Subd')
    db = sqlConnect.DB()
    db.execute(sql_where)
    results = db.fetchall()
    assert results == [('R53752', 'ARTESIAN OAKS SEC 2'), ('R56917', 'ARTESIAN OAKS SEC 3')]

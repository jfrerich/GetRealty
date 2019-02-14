import logging
import os
import pprint
import re

import getrealty
from getrealty import printArray

pp = pprint.PrettyPrinter(width=1)
logger = logging.getLogger(__name__)
print('name', __name__)

# shorten so don't have to pass lib.config.config all over this module
hash_global = getrealty.settings.hash_global
config = getrealty.settings.config


def GetRealty():
    ''' Previous to this routine:
          args have been parsed from command line / gui
          Defaults read from config.yaml file


        The main program
            - calls to build sqlite db, create tables, update
              and modify table columns
            - determine properties in the caches
            - determine properties in the sqlite db
            - determine properies that meet query needs
            - Make calls to web servers to retrieve data
            - parse data
            - calculate additional info for each rnumber
            - write the output to XLSX file
    '''

    getrealty.mydirs.MyDirs().buildmydirs()

    # build the SQL table is it doesn't already exist
    getrealty.sqlConnect.buildTableIfDoesntExist()

    getrealty.sqlConnect.UpdateDBColumns()

    # check that there are no duplicate rnumbers specified with -rnumbers
    if config['defaults']['RNUMBERS'] is not False:
        if checkDuplicateRnumbers():
            exit()

    # build hash that contains all rnumbers that are cached on filesystem
    buildCacheDict()

    # get the rnumbers to for building XLSX page
    #   determined by reading config[defaults][RNUMBERS] or from search query
    #   command line options
    (rnumbers, rnumPropIDArray) = getRnumbers()

    # builds hash_global['cache']['db'][rnumber] dict value is 1 or 0
    checkIfRnumbersInDb(rnumbers)

    # -db_serach option tells program to ONLY read get data from the database
    if config['defaults']['DB_SEARCH'] is False:
        writeDbWithCacheOrServerData(rnumbers, rnumPropIDArray)

        # during regression, print the values for the rnumbers to a hash.
        # These values are grepped by the regression script to the result file
    if config['defaults']['REGRESS'] is True:
        saveRegressionData()

    # write the selected rnumbers to XLSX file
    getrealty.writeexcel.writeExcel(rnumbers)
    logger.info(hash_global)


def buildCacheDict():

    # get all the caches entries
    cache_dir = getrealty.mydirs.MyDirs().cachedir()
    dirlist = os.listdir(cache_dir)

    for mydir in dirlist:
        hash_global['cache'].update({mydir: 1})
        hash_global['propValues'].update({mydir: '-100'})


def saveRegressionData():
    '''function for use with -regress option.  Uses home made integration test
    suite '''

    fh_regress = open('test.regress', "w")

    sql_where = getrealty.sqlConnect.getSearchSqlDbWhereCommand(
        config['defaults']['REGRESS_GET_COLUMNS'])
    logger.info("sql_where = %s", sql_where)

    my_values = getrealty.sqlConnect.sqlQueryRequest(sql_where)

    for value in my_values:
        fh_regress.write(str(value))
        fh_regress.write("\n")


def writeDbWithCacheOrServerData(rnumbers, rnumPropIDArray):
    ''' check if rnumbers are in the cache
        build the hash_global['rnums'] dict
        hash_global['rnums'] contians 'omit' key. determines if rnumber
        data gets pulled from the server
    '''

    checkIfRnumbersInCache(rnumbers)
    count = 1
    carriage_return = 1

    for my_property in rnumPropIDArray:
        rnumber = my_property[0]

        # if rnumber is predetermined to be ommitted from the output file, or
        # from getting added to the database base on the omit function, skip it
        if 'omit' in hash_global['rnums'][rnumber]:
            continue

        # create cache r number dir if doesn't exist
        cache_dir = getrealty.mydirs.MyDirs().cachedir()
        cache_dir_new = cache_dir + '/' + rnumber

        if not os.path.exists(cache_dir_new):
            os.makedirs(cache_dir_new)

        # if Not in the cache or requested to update from server, go and get
        # the data from the server
        if (rnumber not in hash_global['cache']
                or config['defaults']['UPDATE_DB_FROM_SERVER'] is True):
            getDataFromServers(rnumber, my_property)

        # if rnumber in database and not requesting update from cache or
        # server, log rnumber as found in db and don't need to parse cache data
        # files
        if (hash_global['db'][rnumber] == 1 and
            config['defaults']['UPDATE_DB_FROM_CACHE'] is False and
                config['defaults']['UPDATE_DB_FROM_SERVER'] is False):
            # if rnumber in db, and not -update_db_from_server or
            # -update_db_from_cache have database entry - Don't need to
            # ping the server or calculate from the cache
            logger.info("In the Database {}!".format(rnumber))
        else:
            # CREATE A DATABASE ENTRY
            # If during a read of the files, good return value is 0. the file
            # is corrupt
            good_detail = getrealty.webdata.readResponseData(
                'Details', rnumber,
                config['defaults_static']['PROP_DETAIL_RESULTS'])
            good_bills = getrealty.webdata.readResponseData(
                'Bills', rnumber,
                config['defaults_static']['BILL_PAGE_RESULTS'])
            good_hist = getrealty.webdata.readResponseData(
                'History', rnumber,
                config['defaults_static']['HISTORY_PAGE_RESULTS'])
            good_data = getrealty.webdata.readResponseData(
                'Data', rnumber,
                config['defaults_static']['DATASHEET_PAGE'])

            print("good_hist", good_hist)

            # Create additional calculations, to add to the database. These are
            # values that have been found useful to the user, but not available
            # as raw numbers in the data files
            getrealty.createAdditionalInfo.createAdditionalInformation(
                rnumber, "calcs")

            # write the rnumber to the database, or update and existing rnumber
            # entry in the database
            writeOrUpdateDb(rnumber)  # Write the DB


def getDataFromServers(rnumber, my_property):
    ''' get data pages from the server if cached entry doesn't exist or
        -update_db_from_server
        will still omit rnumbers that fall out of requested criteria (min / max
        values)
    '''

    do_update = 0
    if config['defaults']['UPDATE_DB_FROM_SERVER'] is True:
        do_update = 1

    if (do_update == 1 or hash_global['rnums'][rnumber]
            [config['defaults_static']['HISTORY_PAGE_RESULTS']] == 0):
        getrealty.webdata.getPost("History", my_property,
                                  config['defaults_static']
                                  ['HISTORY_PAGE_RESULTS'])

    if (do_update == 1 or hash_global['rnums'][rnumber]
            [config['defaults_static']['PROP_DETAIL_RESULTS']] == 0):
        getrealty.webdata.getPost(
            "Details", my_property,
            config['defaults_static']['PROP_DETAIL_RESULTS'])

    if (do_update == 1 or hash_global['rnums'][rnumber]
            [config['defaults_static']['BILL_PAGE_RESULTS']] == 0):
        getrealty.webdata.getPost(
            "Bills", my_property,
            config['defaults_static']['BILL_PAGE_RESULTS'])

    if (do_update == 1 or hash_global['rnums'][rnumber]
            [config['defaults_static']['DATASHEET_PAGE']] == 0):
        getrealty.webdata.getPost(
            "Data",
            my_property,
            config['defaults_static']['DATASHEET_PAGE'])


def getRnumbers():
    ''' in this routine, we care about getting the list of rnumbers
    This is accomplished via a -db_search or querying the server'''
    # print(globals())
    rnumbers = []
    properties = []
    # Get rnumbers from Db Search
    if config['defaults']['DB_SEARCH'] is True:
        sql_where = getrealty.sqlConnect.getSearchSqlDbWhereCommand(False)
        sql_results = getrealty.sqlConnect.sqlQueryRequest(sql_where)

        rnumbers = [tup[0] for tup in sql_results]
    else:

        if config['defaults']['USE_LAST_ADV_SEARCH'] is not True \
                or config['defaults']['RNUMBERS'] is not False:
            getrealty.webdata.getAdvancedSearchPageResponse()

        properties = getrealty.webdata.getRnumbersFromAdvSearchOrRnumberInput()

        # get the desired Rnumbers only
        for my_property in properties:
            rnumber = my_property[0]
            rnumbers.append(rnumber)

    return(rnumbers, properties)


def checkIfRnumbersInCache(rnumbers):
    ''' in this routine, we care about getting the list of rnumbers
    '''
    num_queries = 0
    numPropsNotOmmitted = 1
    num_queries = 1

    num_rnumbers = len(rnumbers)

    # determine the number of entries that are cached
    logger.info("** Cache Found?")
    pr = " * RNUM    DE B H DA  " * 8 + "\n"
    logger.info(pr)

    carriage_return = 1

    getRequestPages = getRequestPagesArray()

    # determine properties to omit based on min / max value and -f option
    for rnumber in rnumbers:

        num_queries = determineCacheEntriesHash(
            rnumber, num_queries, getRequestPages)

        if carriage_return is 8:
            # 				$logger->info();
            carriage_return = 0
        carriage_return += 1

    numPropsNotOmmitted = getRnumsMeetingCriteria(num_rnumbers, rnumbers)

    if config['defaults']['NO_QUERY_PING_SERVER'] is False:
        questionUserIfWantToSubmit(
            num_rnumbers, numPropsNotOmmitted, num_queries)

    logger.info("(1/%s)  ", numPropsNotOmmitted)


def checkIfRnumbersInDb(rnumbers):
    ''' for all the rnumbers that we are going to collect, check if the value
            is rnumber exists in the database
        builds hash_global['cache']['db'][rnumber] dict Values are 1 or 0 for
            every rnumber
    '''
    for RNUM in rnumbers:

        # initialize as 0 = npt in the db
        hash_global['db'].update({RNUM: 0})

        sql_command = "SELECT r_num FROM " + \
            config['defaults']['TABLE_NAME'] + " WHERE r_num=\"" + RNUM + "\""

        sql_results = getrealty.sqlConnect.sqlQueryRequest(sql_command)

        values = [tup[0] for tup in sql_results]

        for row in values:
            # found in the database - set to 1
            hash_global['db'].update({RNUM: 1})


def questionUserIfWantToSubmit(
        num_rnumbers, num_rnumbers_non_ommitted, num_queries):

    logger.info("Number of R Numbers (total)          : %s", num_rnumbers)
    logger.info(
        "Number of R Numbers (not ommitted)   : %s",
        num_rnumbers_non_ommitted)
    logger.info("Number of Server Queries             : %s", num_queries)

    if (num_queries != 0):

        logger.info(
            "Do you want submit %s to the continue? [y/n] ",
            num_queries)


def getRnumsMeetingCriteria(num_rnumbers, rnumbers):

    numPropsNotOmmitted = 0

    for rnumber in rnumbers:
        if 'omit' in hash_global['rnums'][rnumber]:
            continue
        numPropsNotOmmitted += 1

    logger.info("num_rnumbers = %s", num_rnumbers)
    logger.info("num_rnum_non_ommitted = %s", numPropsNotOmmitted)

    return(numPropsNotOmmitted)


def determineCacheEntriesHash(rnumber, num_queries, pages):

    hash_global['rnums'].update({rnumber: {}})

    # don't add to query if below or above desired value
    value = int(hash_global['propValues'][rnumber])

    print_rnumber = '* {:<12}'.format(rnumber)

    def_max_value = int(config['defaults']['MAX_VALUE'])
    def_min_value = int(config['defaults']['MIN_VALUE'])

    pr_warn = print_rnumber

    if (config['defaults']['RNUMBERS'] is not "ALL") and (
            value <= def_min_value or value >= def_max_value):

            # if -f then force all properties to get run.
        if value >= def_min_value:
            if config['defaults']['FORCE']:
                pr_warn = "FORCED ** Value " + str(
                    value) + ">=" + str(def_max_value)
                logger.info(
                    "FORCED Value %s %s",
                    value,
                    config['defaults']['MAX_VALUE'])
            else:
                for page in pages:
                    hash_global['rnums'][rnumber].update({'omit': 1})
                logger.info(
                    "%sOmitted -  Value %s >= %s",
                    print_rnumber,
                    value,
                    def_max_value)
                return(num_queries)

        if value <= def_min_value:
                        # if -f then force all properties to get run.
            if config['defaults']['FORCE']:
                pr_warn = "FORCED ** Value " + str(
                    value) + "<=" + str(def_min_value)
                pass
            else:
                for page in pages:
                    hash_global['rnums'][rnumber].update({'omit': 1})
                logger.info(
                    "%sOmitted -  Value %s <= %s",
                    print_rnumber,
                    value,
                    def_min_value)
                return(num_queries)

        # see if cache entry request exists
    for page in pages:

        cache_dir = getrealty.mydirs.MyDirs().cachedir()
        cache_page = cache_dir + '/' + rnumber + '/' + page

        if os.path.exists(cache_page):
            # print("*** ", rnumber, " - CACHE FOUND ::",  cache_page)
            pr_warn += "Y "
            hash_global['rnums'][rnumber].update({page: 1})
        else:
            num_queries += 1
            pr_warn += "NOT_FOUND  "
            hash_global['rnums'][rnumber].update({page: 0})
    pr_warn += " "

    logger.info(pr_warn)

    return(num_queries)


def writeOrUpdateDb(rnumber):
    ''' write the data to the database..
        store the values for the rnubmer in a hash
    '''

    update = ""
    logger.info("write or update %s to the database", rnumber)

    my_hash = {'rnumber': {'wkst_headers': {}, 'merged_headers': {}}}

    myPA = printArray.MyPrintArray()
    for arrayEntryPtr in myPA.getMyPrintArray:

        merged_header = myPA.getPrintArrayValueByHeading(
            arrayEntryPtr,
            "merged_header")
        wkst_header = myPA.getPrintArrayValueByHeading(
            arrayEntryPtr, "wkst_header")
        key = myPA.getPrintArrayValueByHeading(arrayEntryPtr,
                                               "key")
        measure_name = myPA.getPrintArrayValueByHeading(
            arrayEntryPtr,
            "measure_name")

        if key in hash_global['DBWriteValues'][rnumber]:
            if measure_name in hash_global['DBWriteValues'][rnumber][key]:
                hpr_measure_name = hash_global['DBWriteValues'][rnumber][key][measure_name]
            else:
                hpr_measure_name = ""
        else:
            hpr_measure_name = ""

        my_hash['rnumber']['wkst_headers'].update(
            {wkst_header: hpr_measure_name})

        my_hash['rnumber']['merged_headers'].update(
            {wkst_header: merged_header})

    prepare_headings = []
    prepare_values = []
    prepare_values = []

    prepare_values.append(rnumber)

    # get the values for the rnumbers
    for wkst_header, value in my_hash['rnumber']['wkst_headers'].items():

        merged_header = my_hash['rnumber']['merged_headers'][wkst_header]

        # get merged name for udating/inserting to db
        wkst_header_merged = wkst_header
        if merged_header != "":
            MERGED_SEPARATOR = config['defaults_static']['MERGED_SEPARATOR']
            wkst_header_merged = merged_header + MERGED_SEPARATOR + wkst_header

        # create prepare_headings array for INSERT sql statement
        prepare_headings.append(wkst_header_merged)
        prepare_values.append(value)

        if config['defaults']['UPDATE_DB_FROM_SERVER'] is True or config['defaults']['UPDATE_DB_FROM_CACHE'] is True:
            # determine if supposed to update the db for this heading
            # defined in printArray
            do_update = myPA.getSecondValueFromHeadingValueCombo(
                "wkst_header", wkst_header, "do_update")

            if do_update != "Yes":
                continue
            update = update + wkst_header_merged + '=\"' + str(value) + '\",'

    # If Not in database, always need to insert Rnumber into the database
    # if rnumber not in hash_global['db'] :
    if hash_global['db'][rnumber] == 0:

        print("rnumber", rnumber, "NOT in the database")
        # This routine is entered when a cache was not found and
        # this is the first time a property is written to the db

        prepare_headings = ",".join(prepare_headings)
        myPAarray = myPA.getMyPrintArray()
        num_columns = len(myPAarray) + 1

        # construct the insert statement
        sql_prepare_insert_questions = "("
        for i in range(num_columns):
            sql_prepare_insert_questions += "?,"

        sql_prepare_insert_questions = re.sub(
            ',$', ')', sql_prepare_insert_questions)

        sql_prepare = "INSERT INTO " + \
            config['defaults']['TABLE_NAME'] + " (r_num,"
        sql_prepare += prepare_headings + ")"
        sql_prepare += " VALUES " + sql_prepare_insert_questions
        logger.info(sql_prepare)

        getrealty.sqlConnect.sqlInsertRequest(sql_prepare, prepare_values)

    elif config['defaults']['UPDATE_DB_FROM_SERVER'] is True or config['defaults']['UPDATE_DB_FROM_CACHE'] is True:

        # get rid of the last comma
        update = re.sub(',$', '', update)

        # build the key,values for SET statement
        # Update the database with the new values
        sql_update = "UPDATE " + config['defaults']['TABLE_NAME']
        sql_update += " SET " + update
        sql_update += " WHERE r_num='" + rnumber + "'"

        logger.info(sql_update)

        getrealty.sqlConnect.sqlSendSimpleRequest(sql_update)

    else:
        pass
        # $logger->error("ERROR I DON't KNOW WHAT TO DO!!");


def getRequestPagesArray():

    array = []

    array.append(config['defaults_static']['PROP_DETAIL_RESULTS'])
    array.append(config['defaults_static']['BILL_PAGE_RESULTS'])
    array.append(config['defaults_static']['HISTORY_PAGE_RESULTS'])
    array.append(config['defaults_static']['DATASHEET_PAGE'])

    return(array)


def checkDuplicateRnumbers():

    arr = config['defaults']['RNUMBERS'].split()

    seen = []
    dupes = []

    for x in arr:
        if x not in seen:
            seen.append(x)
        else:
            dupes.append(x)

    if len(dupes) > 0:
        logging.error(
            "The following -rnumbers have duplicates. Remove the duplicates")
        for dupe in dupes:
            logging.error(dupe)
        return 1
    return 0

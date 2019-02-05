import logging
import os
import sys
from argparse import ArgumentParser

import getrealty

config = getrealty.settings.config
logger = logging.getLogger(__name__)


def generate_argparser():
    parser = ArgumentParser(description='Let\'s get some CAD data!')

    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator')
    parser.add_argument('--rnumbers', help='list of rnumbers. Space separated')
    # parser.add_argument('--rnumbers ALL',
    #                     help='pull All rnumbers in the specified -county \
    #                     cache')
    parser.add_argument('--county',
                        help='County (choices are Bastrop, Williamson)',
                        required=True)
    parser.add_argument('--subd', help='Subdivision (Advanced Search)')
    parser.add_argument('--minacres', help='Min Acres (Advanced Search)')
    parser.add_argument('--maxacres', help='Max Acres (Advanced Search)')
    parser.add_argument('--minvalue',
                        help='Min Assessed Value (Advanced Search)')
    parser.add_argument('--maxvalue',
                        help='Max Assessed Value (Advanced Search)')
    parser.add_argument('--o', '--output',
                        help='output name of .XLSX and search files')
    parser.add_argument('--date', help='append date to output of .XLSX')
    parser.add_argument('-no_query_ping_server',
                        action="store_true",
                        help='don\'t query user if want to submit server ping')
    parser.add_argument('-no_query_overwrite_xls',
                        action="store_true",
                        help='don\'t query user if want to overwrite xls')
    parser.add_argument('--run_dir',
                        help='Location of cache, searches, and excel dir. \
                        (if defined, all exist in run_dir, otw, \
                        includes /$county/ for each dir')
    parser.add_argument('-use_last_adv_search',
                        action="store_true",
                        help='use last advanced search request don\'t send \
                        to server')
    parser.add_argument('-sep_wkts',
                        action="store_true",
                        help='If > 900 entires, place 900 entries in separate \
                        workbooks')
    parser.add_argument('-force',
                        action="store_true",
                        help='force server retreiving of Ommitted Rnumbers \
                        from DEFAULT_MIN_VALUE > value > DEFAULT_MAX_VALUE')
    parser.add_argument('--work_dir')

    group_db_query = parser.add_argument_group('DB QUERY OPTIONS')
    group_db_query.add_argument('-db_search', action="store_true")
    group_db_query.add_argument('--password',
                                help="WHERE command for searching DB. Ex. \
                                WHERE r_num=R53761")

    group_db_update = parser.add_argument_group('DB UPDATE OPTIONS')
    group_db_update.add_argument('-update_db_file',
                                 action="store_true",
                                 help=".xls file with desired changes to \
                                 make to DB")
    group_db_update.add_argument('-update_db_from_server',
                                 action="store_true",
                                 help="will force requested rnumbers to \
                                 update information with latest data from \
                                 server")
    group_db_update.add_argument('-update_db_from_cache',
                                 action="store_true",
                                 help="used to recalculate values in the db, \
                                 from the cache  values")
    # group_db_update.add_argument('-update_db')
    group_db_update.add_argument('-update_db_sum_diff_than_db',
                                 help="If the differences in summary_db and \
                                 database are different, update without \
                                 resolving conflicts")

    group_regress = parser.add_argument_group('REGRESSION OPTIONS')

    group_regress.add_argument('-regress', action="store_true")
    group_regress.add_argument('--regress_get_columns')

    group_regress.add_argument('--sql_where')
    group_regress.add_argument('--sql_search')

    group_new_db_options = parser.add_argument_group('NEW DB QUERY OPTIONS')
    group_new_db_options.add_argument('--update_db_file_junk',
                                      help='''.xls file with desired changes
                                      to make to DB''')

    # group_new_db_options.add_argument(' ',
    #                                   help='.xls file with desired changes \
    #                                   parser.parse_args')

    # group_new_db_options.add_argument(' ',
    #                                   help='-sql_search <comma separated \
    #                                   list of sql column options>')
    #
    # <Column_Name>:Min:Max  - Range of min / max values
    # <Column_Name>::Max     - Values less than Max value
    # <Column_Name>:Min:     - Values greater than Min value
    # <Column_Name>:<value>  - Values equal to <value>
    # <Column_Name>:!<value> - Values NOT equal to <value>
    #
    # Examples:
    #
    #     -sql_search "Subd:ARTESIAN OAKS SEC 3"
    #     -sql_search "Different___Zip:\!0,Different___Addr:1"
    #
    #     tcsh
    #
    #         Setting multiple in a shell
    #
    #             set SQL2 = "Different___Zip:\!0,"
    #             set SQL2 = "\$SQL2 Different___State:\!0, "
    #             set SQL2 = "\$SQL2 Prop_Details___Acres:1:2, "
    #             set SQL2 = "\$SQL2 Prop_Details___AssessVal:30000:, "
    #             set SQL2 = "\$SQL2 TaxDates___LastYrPaid:2012:"
    #
    #             \$SCRIPT -sql_search "\$SQL2" \
    #
    #         LIKE Clause
    #
    #             % is required when using LIKE clause
    #
    #             set RNUMBER='"CIRCLE%"'
    #                 -sql_where "WHERE subd LIKE \$RNUMBER"

    # print help if no args given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def setDefaults():

    getCounty()

    args = generate_argparser()

    setDefaultValue(args.minvalue,   'MIN_VALUE')
    setDefaultValue(args.maxvalue,   'MAX_VALUE')
    setDefaultValue(args.subd,       'SUBDIVISION')
    setDefaultValue(args.county,     'COUNTY')
    setDefaultValue(args.minacres,   'ACRES_LEAST')
    setDefaultValue(args.maxacres,   'ACRES_MOST')
    setDefaultValue(args.run_dir,    'RUN_DIR')
    setDefaultValue(args.work_dir,   'WORK_DIR')
    setDefaultValue(args.o,          'OUTPUT')
    setDefaultValue(args.rnumbers,   'RNUMBERS')
    setDefaultValue(args.db_search,  'DB_SEARCH')
    setDefaultValue(args.sql_search, 'SQL_SEARCH')
    setDefaultValue(args.force,      'FORCE')
    setDefaultValue(args.regress,    'REGRESS')
    setDefaultValue(args.regress_get_columns, 'REGRESS_GET_COLUMNS')
    setDefaultValue(args.sql_where,  'SQL_WHERE')
    setDefaultValue(args.no_query_overwrite_xls, 'NO_QUERY_OVERWRITE_XLS')
    setDefaultValue(args.no_query_ping_server, 'NO_QUERY_PING_SERVER')
    setDefaultValue(args.update_db_from_server,  'UPDATE_DB_FROM_SERVER')
    setDefaultValue(args.use_last_adv_search,  'USE_LAST_ADV_SEARCH')
    setDefaultValue(args.update_db_from_cache,   'UPDATE_DB_FROM_CACHE')

    os.chdir(config['defaults']['WORK_DIR'])


def setDefaultValue(arg, key):
    if arg is not None:
        config['defaults'][key] = arg


def getCounty():

    # required options
    # defined required options here
    # $logger->error("ERROR: Must Provide A County (-county)");

    # county = config.DEFAULT_COUNTY
    # if config.DEFAULT_COUNTY is 'Bastrop':
    if config['defaults']['COUNTY'] is 'Bastrop':
        config['defaults']['HOST_TAX_ACCESSOR'] = 'http://www.bastroptac.com'
        config['defaults']['HOST_TAX_ACCESSOR_WWW'] = 'www.bastroptac.com'

        config['defaults']['HOST_TAX_ACCESSOR_ADVANCED'] = \
            'http://www.bastroptac.com'
        config['defaults']['HOST_TAX_ACCESSOR_WWW_ADVANCED'] = \
            'www.bastroptac.com'

        config['defaults']['GIS_WWW'] = '''http://gis.bisconsultants.com/
        bastropcad/?slayer=0&exprnum=0&esearch="'''

    elif (config['defaults']['COUNTY'] is "Williamson"):

        config['defaults']['HOST_TAX_ACCESSOR'] = 'http://www.tax.wilco.org'
        config['defaults']['HOST_TAX_ACCESSOR_WWW'] = 'tax.wilco.org'

        config['defaults']['HOST_TAX_ACCESSOR_ADVANCED'] = \
            'http://search.wcad.org'
        config['defaults']['HOST_TAX_ACCESSOR_WWW_ADVANCED'] = \
            'search.wcad.org'

        config['defaults']['GIS_WWW'] = 'http://gisapp.wcad.org/?pin='


if __name__ == '__main__':

    args = generate_argparser()
    print(args)

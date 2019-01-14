import logging
import pprint
import re
import sqlite3

import getrealty

pp = pprint.PrettyPrinter(width=1)
logger = logging.getLogger(__name__)
config = getrealty.settings.config


class DB(object):

    """Initialize and manipulate the SQLite3 database"""

    def __init__(self):
        self.database = config['defaults']['WORK_DIR'] + '/RealEstate.db'

        self.connect()

    def connect(self):
        """Connect to the SQLite3 database."""

        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()

    def commit(self):
        """commit to the SQLite3 database."""

        self.conn.commit()

    def execute(self, statement, values=''):
        self.cursor.execute(statement, values)

    def fetchall(self):
        return(self.cursor.fetchall())

    def close(self):
        self.conn.close()


def getSearchSqlDbWhereCommand(columns):

    # DEFAULT: where command will grab all of the columns.
    # If $column defined, only those columns will be returned.
    # (This is only used for regression)
    if columns is False:
        columns = "*"
    else:
        columns = columns

    sql_where_options = []
    #
    # my @sql_options = split(/\s+/, $SQL_SEARCH);
    if config['defaults']['SQL_SEARCH'] is False:
        sql_options = []
    else:
        sql_options = config['defaults']['SQL_SEARCH'].split(',')

    # previous options that are now found using the -sql_search option
    # sql_subd=s'
    # sql_where=s'
    # sql_Diff_Zip=s'
    # sql_Diff_State=s'
    # sql_acres_min=s'
    # sql_acres_max=s'
    # sql_PctToAss_min=s'
    # sql_PctToAss_max=s'
    # sql_Assess_min=s'
    # sql_Assess_max=s'
    # sql_LastYrPaid_min=s'
    # sql_LastYrPaid_max=s'

    array_MinMax = (
        "Prop_Details___Acres",
        "Prop_Details___AssessVal",
        "Tax_Due___PctToAss",
        "Tax_Due___TotAmtDue",
        "TaxDates___LastYrPaid"
    )
    MinMaxValues = "|".join(array_MinMax)

    sql_or = 0

    # print('sql_options', sql_options)
    for search in sql_options:

        # print('search = ', search)

        if re.search(r'OR::(\S+)::(\S+)', search):
            my_search = re.search(r'OR::(\S+)::(\S+)', search)
            # print("  sql_where_options = ", sql_where_options)

            # given a list of values for a column,
            # construct a where command with OR of all entries

            search_db_name = my_search.group(1)
            search_vals = my_search.group(2)

            # get original values
            sql_values_orig = search_vals.split(":")

            # add double quote to all values
            sql_values = []
            for val in sql_values_orig:
                val = "\"" + val + "\""
                sql_values.append(val)

            # my @sql_values = split(":", $search_vals);
            # print "Dumper();\n" . Dumper(@sql_values);

    # sql_where_options_str = " AND ".join(sql_where_options)
            join_str = " OR " + search_db_name + '='
            sql_or_command = join_str.join(sql_values)
            # sql_or_command = join(" OR $search_db_name=", @sql_values);
            sql_or_command = search_db_name + "=" + sql_or_command

            # print("sql_or_command = " ,sql_or_command)
            sql_or = 1
        elif re.search(r'(\S+):(\S+):(\S+)', search):
            my_search = re.search(r'(\S+):(\S+):(\S+)', search)
            # 2 semi-colon
            # column value equals value after semi colon
            search_db_name = my_search.group(1)
            search_val1 = my_search.group(2)
            search_val2 = my_search.group(3)

            if re.search(MinMaxValues, search_db_name):
                sql_where_options = sqlQueryOptsMinMax(search_val1,
                                                       search_val2,
                                                       search_db_name,
                                                       sql_where_options)
            else:
                print("ERROR: ", search_db_name, " not yet ready")
                exit()
        elif re.search(r'(\S+)::(\S+)', search):
            pass
# 			# 2 semi-colon
# 			# only max value given
# 			my $search_db_name = $1;
# 			my $search_val1 = $2;
# 			#print "search2 max = $search_db_name $search_val1\n";
# 			if ($search_db_name =~ /$MinMaxValues/) {
#     			@sql_where_options = sqlQueryOptsMinMax(False, $search_val1,
#                $search_db_name, @sql_where_options);
# 			}
# 			else {
# 				print "ERROR: $search_db_name not yet ready\n";
# 				exit;
# 			}
# 		}
        elif re.search(r'(\S+):(\S+):', search):
            my_search = re.search(r'(\S+):(\S+):', search)
# 			# 2 semi-colon
# 			# only min value given
            search_db_name = my_search.group(1)
            search_val1 = my_search.group(2)
            # print "search3 min = $search_db_name $search_val1\n";

            if re.search(MinMaxValues, search_db_name):
                sql_where_options = sqlQueryOptsMinMax(search_val1,
                                                       False,
                                                       search_db_name,
                                                       sql_where_options)
#     			@sql_where_options = sqlQueryOptsMinMax($search_val1, undef,
#                                   $search_db_name, @sql_where_options);
# 			}
# 			else {
# 				print "ERROR: $search_db_name not yet ready\n";
# 				exit;
# 			}
#
# 		}
        elif re.search(r'(\S+):(.*)', search):
            # 1 semi-colon
            # column value equals value after semi colon
            # currenly allows using !
            my_search = re.search(r'(\S+):(.*)', search)
# 			# 2 semi-colon
# 			# column value equals value after semi colon
            search_db_name = my_search.group(1)
            search_val = my_search.group(2)

            if re.search('(r_num|Subd|Different___(Zip|Addr|State)|OwnerName)',
                         search_db_name):

                is_not = 0

                if re.search(r'\!(\S+)', search_val):
                    my_search1 = re.search(r'\!(\S+)', search)
                    is_not = 1
                    search_val = my_search1.group(1)

                sql_where_options = sqlQueryOptsTextMatch2(is_not,
                                                           search_db_name,
                                                           search_val,
                                                           sql_where_options)
            else:
                print("ERROR: ", search_db_name, " not yet ready")
                exit()
        else:
            print("ERROR: Search Options \"", search, "\" is not valid")
# 			exit;
# 			#$logger->error("ERROR: Search Options \"$search\" is not valid");

    # DEFAULT : select all rows
    sql_where = "SELECT {} FROM {}".format(columns,
                                           config['defaults']['TABLE_NAME'])

    # join all options
    sql_where_options_str = " AND ".join(sql_where_options)

    # if used sql_xx db search options, suffix to the where command
    if config['defaults']['SQL_WHERE'] is not False:
        sql_where = sql_where + " " + config['defaults']['SQL_WHERE']
    elif sql_or:
        sql_where = sql_where + " WHERE " + sql_or_command
    elif sql_where_options_str != "":
        sql_where = sql_where + " WHERE " + sql_where_options_str

    # print("sql", sql_where)
    return(sql_where)


def sqlSendSimpleRequest(command):

    db = getrealty.sqlConnect.DB()
    db.execute(command)
    db.commit()
    db.close()

    # conn = sqlite3.connect(sqlConnect().getDbFileName())
    # cur = conn.cursor()
    # cur.execute(command)
    # conn.commit()
    # conn.close()


def sqlInsertRequest(command, prepare_values):

    db = getrealty.sqlConnect.DB()
    db.execute(command, prepare_values)
    db.commit()
    db.close()

    # conn = sqlite3.connect()
    # cur = conn.cursor()
    # cur.execute(command, prepare_values)
    # conn.commit()
    # conn.close()


def sqlQueryRequest(command):

    # see sql execute command for more.
    # second "prepare_values", used for INSERT when define a prepare statement
    # and then send the values as the second argument

    db = getrealty.sqlConnect.DB()
    db.connect()
    db.execute(command)

    values = db.fetchall()

    db.close()

    return(values)


def buildTableIfDoesntExist():
    # create the table if it doesn't exist.  In perl, this was done with an sql
    # call to determine if it existed first. In here, we use "IF NOT EXISTS"
    # sql command to achieve the same

    headingsArray = getrealty.printArray.getHeadingsFromPrintArray(1, 1)

    table_name = config['defaults']['TABLE_NAME']

    query_headings = ' TEXT, '.join(headingsArray) + " TEXT)"
    query = 'CREATE TABLE IF NOT EXISTS {} \
        (r_num PRIMARY KEY, '.format(table_name) + query_headings

    sqlSendSimpleRequest(query)


def sqlQueryOptsTextMatch2(is_not, db_col_name, search_val, array):

    if (is_not == 1):
        array.append("NOT " + db_col_name + '=\'' + search_val + '\'')
    else:
        array.append(db_col_name + '=\'' + search_val + '\'')

    return(array)


def sqlQueryOptsMinMax(var_min, var_max, db_col_name, array):

    if var_min is not False:
        array.append(db_col_name + '>=' + var_min)

    if var_max is not False:
        array.append(db_col_name + '<=' + var_max)

    return(array)


def UpdateDBColumns():

    # this routine reads the printArray and creates any new columns
    # don't exist in the TABLE.  It does it on the fly so that printArray
    # can be updated without sql commands failing to find columnns
    AllHeadings = getrealty.printArray.getHeadingsFromPrintArray(1, 0)

    table_name = config['defaults']['TABLE_NAME']

    query = 'PRAGMA table_info( {} )'.format(table_name)
    sql_results = sqlQueryRequest(query)
    names = [tup[1] for tup in sql_results]

    new_list = list(set(AllHeadings) - set(names))
    # print(new_list)

    for new_col in sorted(new_list):
        query = 'ALTER'
        query = 'ALTER TABLE {} ADD COLUMN {} TEXT'.format(table_name, new_col)
        sqlSendSimpleRequest(query)

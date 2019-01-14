import logging
import pprint

import getrealty

pp = pprint.PrettyPrinter(width=1)

config = getrealty.settings.config
logger = logging.getLogger(__name__)


class MyPrintArray(object):

    """Docstring for MyClass. """

    def __init__(self):

        # self.printArrayHeadings = (
        #     "pts", "do_update", "db_type",  "comment")
        # self.printArray = [
        #     [ 2,    "No" ],
        #     [ 0,    "Yes"],
        # ]

        k_det  = config['defaults_static']['PROP_DETAIL_RESULTS']
        k_bill = config['defaults_static']['BILL_PAGE_RESULTS']
        # k_hist = config.HISTORY_PAGE_RESULTS
        k_data = config['defaults_static']['DATASHEET_PAGE']
        k_calc = "calcs"
        undef = ' '

        # do_update - when updating from the server or cache, label which columns to update
        #				. do not want to update columns that have data which was input from the user
        #				. Ie. notes, property interest..
        # pts - (print to summary) these are values that will be printed to the summary sheet
        #       0 - (print to db only) values to db, but not to summary or NOTESandContacts sheet
        #       1 - (print to summary) values printed to summary sheet
        #       2 - (print to rnumber page) values printed to NOTESandContacts sheet

        # This is the list of entires to go into the worksheet.
        # The order is kept from below.
        #                     Merged                     Name for wkst        key      key name                                             cond
        #       Do_update     Header                     header               found    of measure              type           format        format    db_type     comment
        self.printArrayHeadings = (
            "pts", "do_update", "merged_header",         "wkst_header",       "key",   "measure_name",         "type",         "format",     "condF",  "db_type",  "comment")
        self.printArray = [
            [ 2,    "No",         "",                    "NOTES_rnum_sheet",  k_calc,  "",                     undef,          undef,        undef,    "",         ""                                                                                       ],
            # 2,    "No",         "",                    "CONTS_rnum_sheet",  $k_calc, "",                     undef,          undef,        undef,    "",                                                                                                 ],
            #[ 0,    "Yes",        "",                   "unique_key",        $k_calc, "UniqueKey",            undef,         undef,        undef,    "",                                                                                            ],
            [ 0,    "Yes",        "",                    "County",            k_calc,  "County",               undef,          undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "",                    "rpg",               k_calc,  "",                     undef,          "format1or0", undef,    "",         "Does the Rnumber have additional Notes (Rnumber tab)"                                  ],
            [ 1,    "No",         "",                    "Property_Interest", k_calc,  "PropInterest",         undef,          undef,        undef,    "",         " "                                                                                        ],
            [ 0,    "Yes",        "Files",               "BillsF",            k_calc,  "bills_wkt",            "file",         undef,        undef,    "",         " "                                                                                        ],
            [ 0,    "Yes",        "Files",               "HistF",             k_calc,  "hist_wkt",             "file",         undef,        undef,    "",         " "                                                                                        ],
            [ 0,    "Yes",        "Files",               "DetF",              k_calc,  "detail_wkt",           "file",         undef,        undef,    "",         " "                                                                                        ],
            [ 0,    "Yes",        "Files",               "DataF",             k_calc,  "datasheet_wkt",        "file",         undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "Links",               "Bills",             k_det,   "bills_link",           "link:Bills",   undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "Links",               "Det",               k_det,   "details_link",         "link:Det",     undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "Links",               "Hist",              k_det,   "hist_link",            "link:Hist",    undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "Links",               "Data",              k_det,   "datasheet_link",       "link:Data",    undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "Maps",                "GIS",               k_det,   "GIS_link",             "link:GIS",     undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "Maps",                "Map",               k_det,   "Property Address",     "goog",         undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "No",         "",                    "NOTES",             k_calc,  "",                     undef,          undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "",                    "Subd",              k_calc,  "subd",                 undef,          undef,        undef,    "",         "Subdivision"                                                                           ],
            [ 1,    "Yes",        "Prop_Details",        "Acres",             k_det,   "Acreage",              undef,          undef,        undef,    "REAL",     " "                                                                                        ],
            [ 1,    "Yes",        "Prop_Details",        "AssessVal",         k_det,   "Assessed",             undef,          undef,        undef,    "REAL",     " "                                                                                        ],
            [ 1,    "Yes",        "Prop_Details",        "AssessMinDue",      k_calc,  "AssessMinDue",         undef,          undef,        undef,    "REAL",     "Assessed Minus Tax Amount Due.  Good for Tax Sale List"                                ],
            [ 1,    "Yes",        "Tax_Due",             "PctToAss",          k_calc,  "TaxToAssessVal",       undef,          "formatpct",  undef,    "REAL",     "Percentage of Taxes Due to Assessed Value of the Property"                             ],
            [ 1,    "Yes",        "Tax_Due",             "TotAmtDue",         k_calc,  "TotAmtDue",            undef,          undef,        undef,    "REAL",     "Total Amount of Taxes Due at the time the information was pulled"                      ],
            [ 1,    "Yes",        "",                    "DatePulled",        k_bill,  "DateResponseCaptured", undef,          undef,        undef,    "",         "Date the Response files were pulled from the server"                                   ],
            [ 1,    "Yes",        "TaxDates",            "OldestDue",         k_calc,  "OldestTaxDue",         undef,          undef,        undef,    "",         "Oldes Taxes Due. Sometimes later year taxes are paid, but older taxes are still due"   ],
            [ 1,    "Yes",        "TaxDates",            "LastPaid",          k_calc,  "LastDatePaid",         undef,          undef,        undef,    "",         "Last Date Taxes were paid."                                                            ],
            [ 1,    "Yes",        "TaxDates",            "LastYrPaid",        k_calc,  "LastYearPaid",         undef,          undef,        undef,    "",         "Last year taxes were paid."                                                            ],
            [ 1,    "Yes",        "Different",           "Addr",              k_calc,  "diff_addr",            undef,          "format1or0", undef,    "",         "Owner and Property addresses Differ"                                                   ],
            [ 1,    "Yes",        "Different",           "Zip",               k_calc,  "diff_zip",             undef,          "format1or0", undef,    "",         "Owner and Property zip codes Differ"                                                   ],
            [ 1,    "Yes",        "Different",           "State",             k_calc,  "diff_state",           undef,          "format1or0", undef,    "",         "Owner and Property states Differ"                                                      ],
            [ 1,    "Yes",        "",                    "NHS_imp",           k_calc,  "NHS_improved",         undef,          "format1or0", undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "",                    "InstallYr",         k_calc,  "UtilInstallYr",        undef,          undef,        undef,    "",         "Year Utilites were installed. Value > {}".format(config['defaults_static']['IMPNHS_VALUE_MIN'])                     ],

            [ 1,    "Yes",        "TimesSold",           "Num",               k_data,  "NumTimesSold",         undef,          undef,        undef,    "",         "Number of Times the Property has been sold"                                            ],
            [ 1,    "Yes",        "TimesSold",           "Last",              k_data,  "LastTimeSold",         undef,          undef,        undef,    "",         "Last Time the Property was Sold"                                                       ],

            [ 1,    "Yes",        "Appraised",           "AppPctOfMax",       k_calc,  "AppPctOfMax",          undef,          "lt_grey",    undef,    "REAL",     "Appraised: Percent Current Value / Max Value ever"                                 ],
            [ 1,    "Yes",        "Appraised",           "AppLastVal",        k_calc,  "AppLastVal",           undef,          undef,        undef,    "REAL",     "Appraised: Last Value Ever Recoreded"                                              ],
            [ 1,    "Yes",        "Appraised",           "AppMaxVal",         k_calc,  "AppMaxVal",            undef,          undef,        undef,    "REAL",     "Appraised: Maximum Value Ever Recoreded"                                           ],
            [ 1,    "Yes",        "AppraisedMaxReduced", "AppMaxAmt",         k_calc,  "AppMaxReduced",        undef,          undef,        undef,    "REAL",     "Appraised: Maximum Reduced Amount from one year to the next"                       ],
            [ 1,    "Yes",        "AppraisedMaxReduced", "AppMaxYr",          k_calc,  "AppMaxReducedYr",      undef,          undef,        undef,    "",         "Appraised: Year Maximum Reduced Amount Occured"                                    ],

            [ 1,    "Yes",        "Assess",              "AssPctOfMax",       k_calc,  "AssPctOfMax",          undef,          "lt_grey",    undef,    "REAL",     "Assessed: Percent Current Value / Max Value ever"                                 ],
            [ 1,    "Yes",        "Assess",              "AssLastVal",        k_calc,  "AssLastVal",           undef,          undef,        undef,    "REAL",     "Assessed: Last Value Ever Recoreded"                                              ],
            [ 1,    "Yes",        "Assess",              "AssMaxVal",         k_calc,  "AssMaxVal",            undef,          undef,        undef,    "REAL",     "Assessed: Maximum Value Ever Recoreded"                                           ],
            [ 1,    "Yes",        "AssessMaxReduced",    "AssMaxAmt",         k_calc,  "AssMaxReduced",        undef,          undef,        undef,    "REAL",     "Assessed: Maximum Reduced Amount from one year to the next"                       ],
            [ 1,    "Yes",        "AssessMaxReduced",    "AssMaxYr",          k_calc,  "AssMaxReducedYr",      undef,          undef,        undef,    "",         "Assessed: Year Maximum Reduced Amount Occured"                                    ],

            [ 1,    "Yes",        "ImpNHS",              "LastPctOfMax",      k_calc,  "ImpNHSPctOfMax",       undef,          "lt_grey",    undef,    "REAL",     "Improved Non-Homestead: Percent Current Value / Max Value ever"                                 ],
            [ 1,    "Yes",        "ImpNHS",              "LastVal",           k_calc,  "ImpNHSLastVal",        undef,          undef,        undef,    "REAL",     "Improved Non-Homestead: Last Value Ever Recoreded"                                              ],
            [ 1,    "Yes",        "ImpNHS",              "MaxVal",            k_calc,  "ImpNHSMaxVal",         undef,          undef,        undef,    "REAL",     "Improved Non-Homestead: Maximum Value Ever Recoreded"                                           ],
            [ 1,    "Yes",        "ImpNHSMaxReduced",    "MaxAmt",            k_calc,  "ImpNHSMaxReduced",     undef,          undef,        undef,    "REAL",     "Improved Non-Homestead: Maximum Reduced Amount from one year to the next"                       ],
            [ 1,    "Yes",        "ImpNHSMaxReduced",    "MaxYr",             k_calc,  "ImpNHSMaxReducedYr",   undef,          undef,        undef,    "",         "Improved Non-Homestead: Year Maximum Reduced Amount Occured"                                    ],

            [ 1,    "Yes",        "ImpHS",               "ihsPctOfMax",       k_calc,  "ImpHSPctOfMax",        undef,          "lt_grey",    undef,    "REAL",     "Improved Homestead: Percent Current Value / Max Value ever"                                 ],
            [ 1,    "Yes",        "ImpHS",               "ihsLastVal",        k_calc,  "ImpHSLastVal",         undef,          undef,        undef,    "REAL",     "Improved Homestead: Last Value Ever Recoreded"                                              ],
            [ 1,    "Yes",        "ImpHS",               "ihsMaxVal",         k_calc,  "ImpHSMaxVal",          undef,          undef,        undef,    "REAL",     "Improved Homestead: Maximum Value Ever Recoreded"                                           ],
            [ 1,    "Yes",        "ImpHSMaxReduced",     "ihsMaxAmt",         k_calc,  "ImpHSMaxReduced",      undef,          undef,        undef,    "REAL",     "Improved Homestead: Maximum Reduced Amount from one year to the next"                       ],
            [ 1,    "Yes",        "ImpHSMaxReduced",     "ihsMaxYr",          k_calc,  "ImpHSMaxReducedYr",    undef,          undef,        undef,    "",         "Improved Homestead: Year Maximum Reduced Amount Occured"                                    ],

            [ 1,    "Yes",        "LandHS",              "lhsPctOfMax",       k_calc,  "LandHSPctOfMax",       undef,          "lt_grey",    undef,    "REAL",     "Land Homestead: Percent Current Value / Max Value ever"                                 ],
            [ 1,    "Yes",        "LandHS",              "lhsLastVal",        k_calc,  "LandHSLastVal",        undef,          undef,        undef,    "REAL",     "Land Homestead: Last Value Ever Recoreded"                                              ],
            [ 1,    "Yes",        "LandHS",              "lhsMaxVal",         k_calc,  "LandHSMaxVal",         undef,          undef,        undef,    "REAL",     "Land Homestead: Maximum Value Ever Recoreded"                                           ],
            [ 1,    "Yes",        "LandHSMaxReduced",    "lhsMaxAmt",         k_calc,  "LandHSMaxReduced",     undef,          undef,        undef,    "REAL",     "Land Homestead: Maximum Reduced Amount from one year to the next"                       ],
            [ 1,    "Yes",        "LandHSMaxReduced",    "lhsMaxYr",          k_calc,  "LandHSMaxReducedYr",   undef,          undef,        undef,    "",         "Land Homestead: Year Maximum Reduced Amount Occured"                                    ],

            [ 1,    "Yes",        "LandNHS",             "lnhsPctOfMax",      k_calc,  "LandNHSPctOfMax",      undef,          "lt_grey",    undef,    "REAL",     "Land Non-Homestead: Percent Current Value / Max Value ever"                                 ],
            [ 1,    "Yes",        "LandNHS",             "lnhsLastVal",       k_calc,  "LandNHSLastVal",       undef,          undef,        undef,    "REAL",     "Land Non-Homestead: Last Value Ever Recoreded"                                              ],
            [ 1,    "Yes",        "LandNHS",             "lnhsMaxVal",        k_calc,  "LandNHSMaxVal",        undef,          undef,        undef,    "REAL",     "Land Non-Homestead: Maximum Value Ever Recoreded"                                           ],
            [ 1,    "Yes",        "LandNHSMaxReduced",   "lnhsMaxAmt",        k_calc,  "LandNHSMaxReduced",    undef,          undef,        undef,    "REAL",     "Land Non-Homestead: Maximum Reduced Amount from one year to the next"                       ],
            [ 1,    "Yes",        "LandNHSMaxReduced",   "lnhsMaxYr",         k_calc,  "LandNHSMaxReducedYr",  undef,          undef,        undef,    "",         "Land Non-Homestead: Year Maximum Reduced Amount Occured"                                    ],

            [ 1,    "Yes",        "DaysLate",            "Curr",              k_calc,  "CurrDaysLate",         undef,          undef,        undef,    "REAL",     "Current Number of Days Taxes are Late"                                                 ],
            [ 1,    "Yes",        "DaysLate",            "Max",               k_calc,  "max_days_late",        undef,          undef,        undef,    "REAL",     "Maximum Days Late over all years.  Used to determine history of times late"            ],
            [ 1,    "Yes",        "",                    "PctDiffAddr",       k_calc,  "pctDiffAddr",          undef,          "format1or0", undef,    "REAL",     "Owner and Property addresses Differ"                                                   ],
            [ 1,    "Yes",        "",                    "PropAddr",          k_det,   "Property Address",     undef,          undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "",                    "OwnerAddr",         k_det,   "Owner Address",        undef,          undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "",                    "OwnerName",         k_det,   "Owner Name",           undef,          undef,        undef,    "",         " "                                                                                        ],
            [ 1,    "Yes",        "",                    "LegalDesc",         k_det,   "Legal Description",    undef,          undef,        undef,    "",         " "                                                                                        ],
#	    [ 1,    "Yes",        "Prop_Details",        "Interest",
#	    $k_det,  "Undivided Interest",   undef,          undef,        undef,
#	    "",],
#		[ 1,    "Yes",        "",               "MinDaysLate",       $k_calc, "min_days_late",        undef,          undef,        undef,    "",                                                                                                 ],
#		[ 1,    "Yes",        "",                    "Utilities",         $k_calc, "utilities",            undef,          undef,        undef,    "",                                                                                                 ],
        ]


    def getMyPrintArray(self):
        return(self.printArray)

    def getMyReturnHash(self):
        return(storePrintArray(self.printArrayHeadings,self.printArray))

def getSecondValueFromHeadingValueCombo(heading, heading_name, heading2):

	# heading = heading to search
	# heading_name = heading to find in heading column
	# heading2 = name of heading to find value

	# this routine is an API to return the value of a second heading, given
	# a heading and value.
	#
	# Ex. for wkst_header,NOTES combo, find value of do_update for that
	#     same row of data.

    myPA = MyPrintArray()
    myRH = myPA.getMyReturnHash()

	# get the array entry number in print array data
    array_number = getPrintArrayHashByValue(heading, heading_name)

	# get value for 2nd heading
    value = myRH['data'][array_number][heading2]

    return(value)

def getPrintArrayHashByValue(heading, heading_name):

	# this routine is an API to return a single hash entry number that represents
	# the anonymous hash matching the heading and heading name value.

    myPA = MyPrintArray()
    myRH = myPA.getMyReturnHash()

    num_returns = 0
    my_list = list(myRH['data'])
    for PrintArrayEntry in my_list:

        if not myRH['data'][PrintArrayEntry][heading]:
            continue
        if not myRH['data'][PrintArrayEntry][heading] is heading_name:
            continue

        if myRH['data'][PrintArrayEntry][heading] is heading_name:
            return_hash_number = PrintArrayEntry
            num_returns = num_returns + 1

    return(return_hash_number)

def storePrintArray(printArrayHeadings,printArray):

    return_hash = {'data':{}}

    cnt = 0
    for myprintArray in (printArray):
        # print(myprintArray)
        for i,heading in enumerate(printArrayHeadings):
            heading_val = myprintArray[i]
            if cnt not in return_hash['data']:
                return_hash['data'][cnt] = {heading:heading_val}
            else :
                return_hash['data'][cnt].update({heading:heading_val})

        cnt += 1
    return_hash['headings'] = printArrayHeadings

    return return_hash

def getHeadingsFromPrintArray(merged,pts_get):

    # This API returns an array of heading names.

    # merged = 1 (return the merged heading names)
    # merged = 0 (return the non-merged heading names)

    # If pts_is defined, only return headings for that type
    # DEFAULT is to grab all entries

    myPAarray = MyPrintArray().getMyPrintArray()

    headingsArray = []
    MERGED_SEPARATOR = config['defaults_static']['MERGED_SEPARATOR']

    for arrayEntryPtr in myPAarray:

        merged_heading = getPrintArrayValueByHeading(arrayEntryPtr, "merged_header")
        heading        = getPrintArrayValueByHeading(arrayEntryPtr, "wkst_header")
        pts            = getPrintArrayValueByHeading(arrayEntryPtr, "pts")

        # when getting summary print headings, only pts == 1 is taken from printArray
        if pts_get:
            if pts is not pts_get:
                continue

        if merged:
            if merged_heading is not "":
                heading = merged_heading + MERGED_SEPARATOR + heading

        db_heading = heading

        headingsArray.append(db_heading)

    return (headingsArray);

def getPrintArrayValueByHeading(arrayEntryPtr,heading):

    # when iterating through following call this routine to get the value of the desired header(s);
    #    foreach my $arrayEntryPtr (@printArray) {

    myPA = MyPrintArray()
    myRH = myPA.getMyReturnHash()

    i = 0
    found = 0
    for printHeading in myRH['headings']:
        if heading == printHeading:
            heading_array_number = i
            found = 1
            break
        i += 1

    return(arrayEntryPtr[i])

def CreatePrintHash():

	# this routine stores all of the print information to the excel worksheet.
	# @header stores the headers and order of the headers.
	# $print_hash stores all key value pairs each rnumber

    printhash = {'type':{},'format':{},'cond_format':{},'comment':{},'headers':[],'headers_merged':[],'headers_merged_num':{}}

    myPA = MyPrintArray()
    myPAarray = myPA.getMyPrintArray()

    for arrayEntryPtr in myPAarray:
        pts            = getPrintArrayValueByHeading(arrayEntryPtr, "pts")
        merged_heading = getPrintArrayValueByHeading(arrayEntryPtr, "merged_header")
        heading        = getPrintArrayValueByHeading(arrayEntryPtr, "wkst_header")
        #my $key            = getPrintArrayValueByHeading($arrayEntryPtr, "key");
        #my $measure_name   = getPrintArrayValueByHeading($arrayEntryPtr, "measure_name");
        my_type        = getPrintArrayValueByHeading(arrayEntryPtr, "type")
        my_format      = getPrintArrayValueByHeading(arrayEntryPtr, "format")
        cond_format    = getPrintArrayValueByHeading(arrayEntryPtr, "condF")
        comment        = getPrintArrayValueByHeading(arrayEntryPtr, "comment")

		# if not a summary entry, don't add, otw, headers get shifted
        if (pts is not 1) : continue

        if (merged_heading is ""):
            printhash['headers_merged'].append("")
        else:
            if merged_heading not in printhash['headers_merged_num']:
                printhash['headers_merged_num'].update({merged_heading:1})
                printhash['headers_merged'].append(merged_heading)
            else:
                old_merged_heading = printhash['headers_merged_num'][merged_heading]
                new_merged_heading_val = old_merged_heading + 1
                printhash['headers_merged_num'].update({merged_heading:new_merged_heading_val})

            heading = "{}{}{}".format(merged_heading,config['defaults_static']['MERGED_SEPARATOR'],heading)
        printhash['headers'].append(heading)

		# get the type of input, formatting, conditional formatting, and comment
        if my_type is not " ":     printhash['type'].update({heading:my_type})
        if my_format is not " ":   printhash['format'][heading]      = my_format
        if cond_format is not " " : printhash['cond_format'][heading] = cond_format
        if comment is not " " :     printhash['comment'][heading]     = comment

    return(printhash)

if __name__ == '__main__':
    pass


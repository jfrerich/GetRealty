import logging
import re
from collections import Counter
from datetime import date

import getrealty


config = getrealty.settings.config
hash_global = getrealty.settings.hash_global

logger = logging.getLogger(__name__)


def createAdditionalInformation(rnumber, key_calcs):

    key_bill = config['defaults_static']['BILL_PAGE_RESULTS']
    key_hist = config['defaults_static']['HISTORY_PAGE_RESULTS']
    key_detail = config['defaults_static']['PROP_DETAIL_RESULTS']
    key_data = config['defaults_static']['DATASHEET_PAGE']

    # Details Calculations
    (pct_same_addr, diff_addr, diff_zip, diff_state) = propAddrSameAsOwnerAddr(
        rnumber,
        key_detail)
    subdivision = getSubdivision(rnumber, key_detail)

    # create key for filling hash below
    hash_global['DBWriteValues'][rnumber].update({key_calcs: {}})

    # create short variable to use in code because this is placed a lot
    hash_key_calcs = hash_global['DBWriteValues'][rnumber][key_calcs]

    # Bills Calculations
    (maxDaysLate, minDaysLate, LastYearPaid, LastDatePaid, currDaysLate,
     OldestTaxesDue) = createDaysLate(rnumber, key_calcs, key_bill)

    # Multiple Pages Calculations
    (pctTaxToAssessedValue, AssMinDue) = pctTaxToAssessedValuedef(rnumber,
                                                                  key_bill,
                                                                  key_detail)

    totamtdue = hash_global['DBWriteValues'][rnumber][key_bill][
        'Total Amount Due']
    hash_key_calcs.update({'TotAmtDue': totamtdue})

    # push values to calc hash key
    hash_key_calcs['PropInterest'] = \
        config['defaults_static']['INITIAL_PROP_INTEREST']
    # hash_key_calcs['PropInterest'] = "=IF(ISERROR(SHEET($rnumber)),
    # \"Not Vetted\",$rnumber.E4)";

    hash_key_calcs['subd'] = subdivision
    hash_key_calcs['County'] = config['defaults']['COUNTY']

    # Use this if / when use the same table name, but uniquify key
    # $hash_key_calcscalcs}->{UniqueKey}     = "${COUNTY}_${rnumber}";

    hash_key_calcs['subdivision'] = maxDaysLate
    hash_key_calcs['max_days_late'] = maxDaysLate
    hash_key_calcs['min_days_late'] = minDaysLate
    hash_key_calcs['LastYearPaid'] = LastYearPaid
    hash_key_calcs['LastDatePaid'] = LastDatePaid
    hash_key_calcs['CurrDaysLate'] = currDaysLate
    hash_key_calcs['OldestTaxDue'] = OldestTaxesDue

    hash_key_calcs['pctDiffAddr'] = pct_same_addr
    hash_key_calcs['diff_addr'] = diff_addr
    hash_key_calcs['diff_zip'] = diff_zip
    hash_key_calcs['diff_state'] = diff_state
    hash_key_calcs['TaxToAssessVal'] = pctTaxToAssessedValue
    hash_key_calcs['AssessMinDue'] = AssMinDue

    # History Calculations (Improvement)
    # Appraised Value
    (App, ApputilInstall,
     AppinstallYear,
     AppLastVal,
     AppMaxRedAmt,
     AppMaxReducedYr,
     AppMaxVal,
     AppPctOfMax) \
        = utilitiesInstalled(rnumber, key_calcs, key_hist, "AppraisedValue")

    # Assessed
    (Ass, AssutilInstall,
     AssinstallYear,
     AssLastVal,
     AssMaxRedAmt,
     AssMaxReducedYr,
     AssMaxVal,
     AssPctOfMax) \
        = utilitiesInstalled(rnumber, key_calcs, key_hist, "Assessed")

    # Imp_NHS
    (impNHS,
     impNHSutilInstall,
     impNHSinstallYear,
     impNHSLastVal,
     impNHSMaxRedAmt,
     impNHSMaxReducedYr,
     impNHSMaxVal,
     impNHSPctOfMax) \
        = utilitiesInstalled(rnumber, key_calcs, key_hist, "ImpNHS")

    # Imp_HS
    (impHS,
     impHSutilInstall,
     impHSinstallYear,
     impHSLastVal,
     impHSMaxRedAmt,
     impHSMaxReducedYr,
     impHSMaxVal,
     impHSPctOfMax) \
        = utilitiesInstalled(rnumber, key_calcs, key_hist, "ImpHS")

    # Land HS
    (landHS,
     landHSutilInstall,
     landHSinstallYear,
     landHSLastVal,
     landHSMaxRedAmt,
     landHSMaxReducedYr,
     landHSMaxVal,
     landHSPctOfMax) = utilitiesInstalled(rnumber,
                                          key_calcs,
                                          key_hist,
                                          "LandHS")

    # Land NHS
    (landNHS,
     landNHSutilInstall,
     landNHSinstallYear,
     landNHSLastVal,
     landNHSMaxRedAmt,
     landNHSMaxReducedYr,
     landNHSMaxVal,
     landNHSPctOfMax) = utilitiesInstalled(rnumber,
                                           key_calcs,
                                           key_hist,
                                           "LandNHS")

    hash_key_calcs['ImpNHSPctOfMax'] = impNHSPctOfMax
    hash_key_calcs['ImpNHSMaxReducedYr'] = impNHSMaxReducedYr
    hash_key_calcs['ImpNHSMaxVal'] = impNHSMaxVal
    hash_key_calcs['ImpNHSLastVal'] = impNHSLastVal
    hash_key_calcs['ImpNHSMaxReduced'] = impNHSMaxRedAmt
    hash_key_calcs['utilities'] = impNHSutilInstall
    hash_key_calcs['UtilInstallYr'] = impNHSinstallYear
    hash_key_calcs['NHS_improved'] = impNHS

    hash_key_calcs['AppMaxReducedYr'] = AppMaxReducedYr
    hash_key_calcs['AppMaxVal'] = AppMaxVal
    hash_key_calcs['AppLastVal'] = AppLastVal
    hash_key_calcs['AppMaxReduced'] = AppMaxRedAmt
    hash_key_calcs['AppPctOfMax'] = AppPctOfMax

    hash_key_calcs['AssMaxReducedYr'] = AssMaxReducedYr
    hash_key_calcs['AssMaxVal'] = AssMaxVal
    hash_key_calcs['AssLastVal'] = AssLastVal
    hash_key_calcs['AssMaxReduced'] = AssMaxRedAmt
    hash_key_calcs['AssPctOfMax'] = AssPctOfMax

    hash_key_calcs['ImpHSMaxReducedYr'] = impHSMaxReducedYr
    hash_key_calcs['ImpHSMaxVal'] = impHSMaxVal
    hash_key_calcs['ImpHSLastVal'] = impHSLastVal
    hash_key_calcs['ImpHSMaxReduced'] = impHSMaxRedAmt
    hash_key_calcs['ImpHSPctOfMax'] = impHSPctOfMax
    # hash_key_calcs[utilities]           = impHSutilInstall
    # hash_key_calcs[UtilInstallYr]       = impHSinstallYear
    # hash_key_calcs[NHS_improved]        = impHS

    hash_key_calcs['LandHSMaxReducedYr'] = landHSMaxReducedYr
    hash_key_calcs['LandHSMaxVal'] = landHSMaxVal
    hash_key_calcs['LandHSLastVal'] = landHSLastVal
    hash_key_calcs['LandHSMaxReduced'] = landHSMaxRedAmt
    hash_key_calcs['LandHSPctOfMax'] = landHSPctOfMax

    hash_key_calcs['LandNHSMaxReducedYr'] = landNHSMaxReducedYr
    hash_key_calcs['LandNHSMaxVal'] = landNHSMaxVal
    hash_key_calcs['LandNHSLastVal'] = landNHSLastVal
    hash_key_calcs['LandNHSMaxReduced'] = landNHSMaxRedAmt
    hash_key_calcs['LandNHSPctOfMax'] = landNHSPctOfMax

    cache_dir = getrealty.mydirs.MyDirs().cachedir()
    hash_key_calcs.update(
        {'bills_wkt': "/".join([cache_dir, rnumber, key_bill])})
    hash_key_calcs.update(
        {'hist_wkt': "/".join([cache_dir, rnumber, key_hist])})
    hash_key_calcs.update(
        {'detail_wkt': "/".join([cache_dir, rnumber, key_detail])})
    hash_key_calcs.update(
        {'datasheet_wkt': "/".join([cache_dir, rnumber, key_data])})


def propAddrSameAsOwnerAddr(rnumber, key):

    # if owner address not in hash, return values and don't calculate

    ownr_addr = hash_global['DBWriteValues'][rnumber][key]['Owner Address']
    prop_addr = hash_global['DBWriteValues'][rnumber][key]['Property Address']

    if ownr_addr == ",":
        return("n/a", "0 no", "n/a", "n/a")
    elif ownr_addr == "":
        return("n/a", "0 no", "n/a", "n/a")

    if prop_addr != "":

        # zip
        # remove -xxx from zip code
        prop_zip = re.sub(r'.*\s(\d+)(-\d+)?$', r'\1', prop_addr)
        ownr_zip = re.sub(r'.*\s(\d+)(-\d+)?$', r'\1', ownr_addr)

        if not re.search(
                r'\d\d\d\d', prop_zip) or not re.search(
                r'\d\d\d\d', ownr_zip):
            diff_zip = "n/a"

# 			$logger->warn("WARNING: Zip Not Recognized");
# 			$logger->warn("\tOwner Address : $ownr_addr");
# 			$logger->warn("\tProp Address  : $prop_addr");
# 			$logger->warn("\tOwner Zip : $ownr_zip");
# 			$logger->warn("\tProp Zip  : $prop_zip");

        elif prop_zip == ownr_zip:
            diff_zip = "0"
        else:
            diff_zip = "1"

        # state
        # prop_state = re.sub(r'.*,?\s?(\S\S) (\d+)(-\d+)?$', r'\1', prop_addr)
        ownr_state = re.sub(r'.*,?\s?(\S\S) (\d+)(-\d+)?$', r'\1', ownr_addr)

        if not re.search(r'^\S\S$', ownr_state):
            diff_state = "n/a"

# 			$logger->warn("WARNING: State Not Recognized");
# 			$logger->warn("Owner Address : $ownr_addr");
# 			$logger->warn("Owner State : $ownr_state");
        elif ownr_state == config['defaults_static']['STATE']:
            diff_state = "0"
        else:
            diff_state = "1 - " + ownr_state

        # Address
        prop_addr = re.sub(r'(\d+)(-\d+)?$', r'\1', prop_addr)
        ownr_addr = re.sub(r'(\d+)(-\d+)?$', r'\1', ownr_addr)

        # Substitutions before compare
        # get rid of irrelevant portions of addr
        (ownr_addr, prop_addr) = removeFromAddr(
            ownr_addr, prop_addr, " RD ", " ")
        (ownr_addr, prop_addr) = removeFromAddr(
            ownr_addr, prop_addr, " ROAD ", " ")
        (ownr_addr, prop_addr) = removeFromAddr(
            ownr_addr, prop_addr, " LN ", " ")
        (ownr_addr, prop_addr) = removeFromAddr(
            ownr_addr, prop_addr, " CV ", " ")
        (ownr_addr, prop_addr) = removeFromAddr(
            ownr_addr, prop_addr, " HWY ", " ")
        (ownr_addr, prop_addr) = removeFromAddr(
            ownr_addr, prop_addr, " FM ", " ")
        (ownr_addr, prop_addr) = removeFromAddr(
            ownr_addr, prop_addr, " ST ", " ")
        (ownr_addr, prop_addr) = removeFromAddr(
            ownr_addr, prop_addr, ",", "")  # commas
        (ownr_addr, prop_addr) = removeFromAddr(
            ownr_addr, prop_addr, " ", "")  # spaces - Do this one last

        if ownr_addr == prop_addr:
            diff_addr = "0"
        else:
            diff_addr = "1"

        pct_same_addr = getPctDiffInAddr(ownr_addr, prop_addr)

        return(pct_same_addr, diff_addr, diff_zip, diff_state)

    else:
        # if the owner address is known, can still determine if the owner is
        # in a different state

        # state
        ownr_state = re.sub(r'.*,?\s?(\S\S) (\d+)(-\d+)?$', r'\1', ownr_addr)

        if not re.search(r'^\S\S$', ownr_state):
            diff_state = "n/a"

            # $logger->warn("WARNING: State Not Recognized");
            # $logger->warn("Owner Address : $ownr_addr");
            # $logger->warn("Owner State : $ownr_state");

        elif ownr_state != config['defaults_static']['STATE']:
            diff_state = "1 - " + ownr_state
        else:
            diff_state = "0"
        return("n/a", "1 np", "n/a", diff_state)
    # else:
    #     return("n/a", "n/a", "n/a", "n/a")


def utilitiesInstalled(rnumber, key_calcs, key_hist, my_type):

    DEBUG_UTIL = 0

    installYear = None
    NHS_improved = 0

    prevYrValue = 0
    currYrValue = 0
    impYrDiff = 0
    MaxReduced = 0
    MaxReducedYr = 0
    MaxVal = 0

    for year, date_paid in (
        sorted(
            hash_global['DBWriteValues'][rnumber]
            [key_hist]['TaxYear'].items(),
            key=lambda kv: kv[0])):

        # set the intitial value to 0
        if my_type not in hash_global['DBWriteValues'][rnumber][key_hist][
                'TaxYear'][year]:
            currYrValue = 0
        else:
            currYrValue = float(
                hash_global['DBWriteValues'][rnumber]
                [key_hist]['TaxYear'][year][my_type])

        impYrDiff = (prevYrValue) - (currYrValue)
        if (impYrDiff > config['defaults_static']
                ['MIN_IMP_DIFF']) and (MaxReduced >= 0):
            MaxReduced = impYrDiff
            MaxReducedYr = year

        if (DEBUG_UTIL):
            print("CurrYrValue=", currYrValue)
            print("diff=", impYrDiff)
            print("MaxReduced=", MaxReduced)
            print("MaxReducedYr=", MaxReducedYr)
            print("prevYrValue=", prevYrValue)

        # need better method.  Right now only 8000 gets tagged.
        # could be >8k, <10??
        # what gets included in this ??
        # really trying to use this to determine if utilities on the land..
        # if (($currYrValue >= "8000.00") && ($currYrValue < "9500.00")) {
        # if (($currYrValue >= $DEFAULT_IMPNHS_VALUE_MIN) && ($currYrValue <=
        # $DEFAULT_IMPNHS_VALUE_MAX)) {
        if currYrValue >= config['defaults_static']['IMPNHS_VALUE_MIN']:
            if installYear is None:
                installYear = year

        # was the land ever improved?
        if currYrValue > MaxVal:
            MaxVal = currYrValue

        # was the land ever improved?
        if currYrValue > 0:
            if NHS_improved is not None:
                NHS_improved = 1

        prevYrValue = currYrValue

        # print "\n" if $DEBUG_UTIL;

    # $installYear = "n/a" if (! defined $installYear);
    # $NHS_improved = 0    if (! defined $NHS_improved);

    if installYear is None:
        installYear = "n/a"
    if NHS_improved is None:
        NHS_improved = 0

    PctOfMax = 0
    if (currYrValue == 0) or (MaxVal == 0):
        PctOfMax = 0
    else:
        PctOfMax = (currYrValue / MaxVal) * 100

    PctOfMax = '{:.2f}'.format(PctOfMax)

    # "utilites installed?", "Year installed"
    # return("N", "Not Installed");

    return(NHS_improved, 0, installYear, currYrValue,
           MaxReduced, MaxReducedYr, MaxVal, PctOfMax)


def getSubdivision(rnumber, key):

    try:
        hash_global['DBWriteValues'][rnumber][key]['Legal Description']
    except BaseException:
        pass

    subdivision = hash_global['DBWriteValues'][rnumber][key][
        'Legal Description']
    subdivision = re.sub(r',.*', '', subdivision)

    return(subdivision)


def createDaysLate(rnumber, key_calcs, key_bill):

    response_date = hash_global['DBWriteValues'][rnumber][key_bill][
        'DateResponseCaptured']
    response_date_arr = response_date.split("/")
    response_date_new = date(int(response_date_arr[2]),
                             int(response_date_arr[0]),
                             int(response_date_arr[1]))
    # print
    # Dumper(%{$hash_global['DBWriteValues']->{$rnumber}->{$key_bill}->{dates_paid}});

    DEBUG_DAYS = 0

    maxDaysLate = 0
    maxDaysLateYr = 0
    minDaysLate = 10000
# my @date_paid_array_new;

# good
    LastYearPaid = ""
    LastDatePaid = None

    CurrDaysLate = 0
    OldestTaxesDue = 'N/A'
    thisYrPaid = 0

    # print "year  date_paid    days_late  currdayslate\n" if $DEBUG_DAYS;

    thisYear = 1

    for year, date_paid in (
        sorted(
            hash_global['DBWriteValues'][rnumber]
            [key_bill]['dates_paid'].items(),
            key=lambda kv: kv[0],
            reverse=True)):
        year_p1 = int(year) + 1
        pay_due = date(year_p1, 1, 31)
        # print ("year", year)

        date_paid = hash_global['DBWriteValues'][rnumber][key_bill][
            'dates_paid'][year]

        if date_paid == "":
            # get info for this year last year
            if thisYear:
                thisYrPaid = 0
                OldestTaxesDue = year
                thisYear = 0
                continue
            else:
                thisYrPaid = 1

            # grab the oldest taxes never paid
            OldestTaxesDue = year

            # equal to due date for that current response created - date due
            # for that year. If found here, it is the first time not paid
            delta = pay_due - response_date_new
            CurrDaysLate = delta.days

            continue

        # Set to zero if
        if (CurrDaysLate is not None):
            CurrDaysLate = 0

        date_paid_array = date_paid.split("/")
        date_paid_array_formatted1 = (date_paid_array[2],
                                      date_paid_array[0],
                                      date_paid_array[1])
        date_paid_array_formatted = date(int(date_paid_array[2]),
                                         int(date_paid_array[0]),
                                         int(date_paid_array[1]))

        # Keep max days late on payment
        days_late = (date_paid_array_formatted - pay_due).days

        if days_late > maxDaysLate:
            maxDaysLate = days_late
            maxDaysLateYr = year

        # last year Paid taxes
        # Once found, that is the last time paid taxes
        if LastYearPaid == "":
            LastYearPaid = year
        if LastDatePaid is None:
            LastDatePaid = "/".join(date_paid_array_formatted1)

        if (DEBUG_DAYS):
            print("year=", year)
            print("DueDate=" + "/".join(pay_due) + " ")
            print("DatePaid=", date_paid_array_formatted)
            print("ThisYrPaid=", thisYrPaid)
            # print_days_late = '{%4s}'.format(diff)
            # diff = '{:.2f}'.format(diff)
            # print("DaysLate=", print_days_late )
            print("MaxDaysLate=", maxDaysLate)
            print("MaxDaysLateYr=", maxDaysLateYr)
            print("lastYearPaid=", LastYearPaid)
            print("lastDatePaid=", LastDatePaid)
            print("CurrDayeLate=", CurrDaysLate)
            # print("MinDaysLate=$minDaysLate  " if $DEBUG_DAYS;
            print("OldestNotPaid=", OldestTaxesDue)
            print("\n")

    return(maxDaysLate, minDaysLate,
           LastYearPaid, LastDatePaid,
           CurrDaysLate, OldestTaxesDue)


def pctTaxToAssessedValuedef(rnumber, key_bill, key_detail):

    assessed_value = float(
        hash_global['DBWriteValues'][rnumber]
        [key_detail]['Assessed'].replace(',', ''))
    current_taxes_due = float(
        hash_global['DBWriteValues'][rnumber][key_bill]
        ['Total Amount Due'].replace(',', ''))

    pct = (current_taxes_due / assessed_value) * 100
    diff = assessed_value - current_taxes_due
    diff = '{:.2f}'.format(diff)

    pct_formatted = '{:.2f}'.format(pct)

    return(pct_formatted, diff)


def removeFromAddr(ownr_addr, prop_addr, find, replace):

    prop_addr = re.sub(find, replace, prop_addr)
    ownr_addr = re.sub(find, replace, ownr_addr)

    return(ownr_addr, prop_addr)


def getPctDiffInAddr(ownr_addr, prop_addr):

    ownr_addr = re.sub(r'[\/\(\)]', '', ownr_addr)
    prop_addr = re.sub(r'[\/\(\)]', '', prop_addr)

    o_array = list(ownr_addr)
    p_array = list(prop_addr)

    if len(o_array) > len(p_array):
        num_longer = len(o_array)
    else:
        num_longer = len(p_array)

    c1 = Counter(o_array)
    c2 = Counter(p_array)

    diff = c1 - c2
    # print(list(diff.elements()))
    num_left = len(list(diff.elements()))

    pct_same = num_left / num_longer
    pct_same = '{:.2f}'.format(pct_same)

    # print("ownr_addr =", ownr_addr)
    # print("prop_addr =", prop_addr)
    # print("num_l =", num_longer)
    # print("num_s =", num_shorter)
    # print("num_left =", num_left)
    # print("pct_same =", pct_same)

    return(pct_same)

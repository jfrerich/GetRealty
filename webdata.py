import logging
import re
import subprocess
import urllib

import lib.settings
import lib.mydirs
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
config = lib.settings.config
hash_global = lib.settings.hash_global


def readResponseData(page_type, rnumber, response_file_suffix):

    cache_dir = lib.mydirs.MyDirs().cachedir()
    response_file = cache_dir + '/' + rnumber + '/' + response_file_suffix
    # add rnumber to dict, if it doesn't exist
    if rnumber not in hash_global['DBWriteValues']:
        hash_global['DBWriteValues'].update({rnumber: {}})

    # add page_type to dict
    hash_global['DBWriteValues'][rnumber].update({response_file_suffix: {}})

    if page_type == "History":
        readRnumHistPageResponseData(
            rnumber,
            response_file_suffix,
            response_file)
    elif page_type == "Details":
        readRnumDetailPageResponseData(
            rnumber,
            response_file_suffix,
            response_file)
    elif page_type == "Bills":
        readRnumBillsPageResponseData(
            rnumber,
            response_file_suffix,
            response_file)
    elif page_type == "Data":
        response_file = (cache_dir
                         + '/'
                         + rnumber
                         + '/'
                         + config['defaults_static']['DATASHEET_PAGE_XML'])
        readRnumDataSheetPageResponseData(
            rnumber,
            response_file_suffix,
            response_file)


def readRnumHistPageResponseData(rnumber, hash_key, response_file):

    # TreeBuilder will not find the follwing in this file
    # because it is above the <html> tag
    #
    # Parse as a file
    #
    # <HistoryResults>
    #   <TaxYear MinTaxYear="1988" MaxTaxYear="2013" />
    #   <History TaxYear="1988" Name="Exemptions" Value="" />
    #   <History TaxYear="1989" Name="Exemptions" Value="" />

    the_page = open(response_file)
    soup = BeautifulSoup(the_page, "html.parser")

    # print(soup.prettify())

    tags = soup.find('taxyear')

    hash_short = hash_global['DBWriteValues'][rnumber][hash_key]
    hash_short.update({'MinTaxYear': tags.get('mintaxyear')})

    tags = soup.find_all('history')
    for t in tags:

        taxyear = t.get('taxyear')
        name = t.get('name')
        value = t.get('value')
        if value == "" or not t.has_attr('value'):
            continue

        if 'TaxYear' not in hash_short:
            hash_short.update({'TaxYear': {}})
        if taxyear not in (hash_short['TaxYear']):
            hash_short['TaxYear'].update({taxyear: {}})

        hash_short['TaxYear'][taxyear].update({name: value})

    # pprint.PrettyPrinter().pprint(hash_global['DBWriteValues'][rnumber][hash_key])


def readRnumDetailPageResponseData(rnumber, hash_key, response_file):

    # add rnumber to dict, if it doesn't exist
    if rnumber not in hash_global['DBWriteValues']:
        hash_global['DBWriteValues'].update({rnumber: {}})

    # add page_type to dict
    hash_global['DBWriteValues'][rnumber].update({hash_key: {}})

    # check that response file is not corrupt.
    # my @check_values = ("Legal Description");
    # return(0) unless \
    # checkValuesExistInResponseFile($response_file, @check_values);
    #
    # get first level mains
    # (return1, return4) = \
    #   getDetailMainEntries(rnumber, hash_key, response_file)
    getDetailMainEntries(rnumber, hash_key, response_file)

    # Exemption Codes
    # my $return2 = getDetailEntityCodes($rnumber, $hash_key, $response_file);
    # my $return3 = \
    #   getDetailValuesBreakdown($rnumber, $hash_key, $response_file);
    # pp.pprint(hash_global['DBWriteValues'][rnumber][hash_key])


def getDetailPropIDPropOwnerID(rnumber, hash_key, soup):

    # check that response file is not corrupt.
    # @check_values = ("PropertyID", "PropertyOwnerID");
    # return(0) unless \
    #   checkValuesExistInResponseFile($response_file, @check_values);

    # my $fh = new FileHandle;
    # unless (open ($fh, $response_file)) {
    # 	$logger->error("ERROR: cannot open the file '$response_file': $!");
    # 	exit;
    # }

    # souplines = soup.prettify()
    for line in soup.get_text().split("\n"):
        # print("line=", line)
        if re.search(r"PropertyID=(\d+)", line):
            m = re.search(r"PropertyID=(\d+)", line)
            propertyID = m.group(1)
        if re.search(r"PropertyOwnerID=(\d+)", line):
            m = re.search(r"PropertyOwnerID=(\d+)", line)
            propertyOwnerID = m.group(1)

    try:
        propertyID
    except BaseException:
        logger.error("ERROR: propertyID or propertyOwnerID not defined")
    try:
        propertyOwnerID
    except BaseException:
        logger.error("ERROR: propertyID or propertyOwnerID not defined")

    prefix = (config['defaults_static']['HOST_TAX_ACCESSOR']
              + "/Appraisal/PublicAccess/")
    pIDandPOID = ("PropertyID="
                  + propertyID
                  + "&PropertyOwnerID="
                  + propertyOwnerID)

    html_bills = prefix + "PropertyBills.aspx?"
    html_bills += pIDandPOID + "&NodeID=11"

    html_details = prefix + "PropertyDetail.aspx?"
    html_details += pIDandPOID + "&dbKeyAuth=Appraisal&TaxYear=2013&NodeID=11"

    html_hist = prefix + "PropertyHistory.aspx?"
    html_hist += pIDandPOID + "&NodeID=11&FirstTaxYear="
    html_hist += (config['defaults_static']['FIRSTTAXYEAR']
                  + "&LastTaxYear="
                  + config['defaults_static']['LASTTAXYEAR'])

    html_data = prefix + "PropertyDataSheet.aspx?"
    html_data += pIDandPOID + "&NodeID=11"

    # my $html_gis = "http://gis.bisconsultants.com/bastropcad/?esearch=\
    # $rnumber&slayer=0&exprnum=0";
    html_gis = config['defaults_static']['GIS_WWW'] + rnumber

    hash_short = hash_global['DBWriteValues'][rnumber][hash_key]
    hash_short.update({'bills_link': html_bills})
    hash_short.update({'details_link': html_details})
    hash_short.update({'hist_link': html_hist})
    hash_short.update({'GIS_link': html_gis})
    hash_short.update({'datasheet_link': html_data})

    hash_short.update({'propertyID': propertyID})
    hash_short.update({'propertyOwnerID': propertyOwnerID})
    # return(0)

# ####################################
# sub checkValuesExistInResponseFile {
#
# 	my ($response_file, @check_names) = @_;
#
# 	my $fh = new FileHandle;
# 	unless (open ($fh, $response_file)) {
# 		$logger->error("ERROR: cannot open the file '$response_file': $!");
# 	}
#
# 	my $tmp_hash;
#
# 	while (my $line = <$fh>) {
#
# 		my $looparray = 0;
#
# 		foreach my $name (@check_names) {
# 			$looparray++;
# 			if ($line =~ /$name/) {
# 				$tmp_hash->{$looparray} = 1;
# 			}
# 		}
# 	}
# 	close $fh;
#
# 	my $num_keys = keys %{$tmp_hash};
# 	my $num_checks = $#check_names + 1;
#
# 	if ($num_keys eq $num_checks) {
# 		return(1);
# 	}
# 	else {
# 		return(0);
# 	}
# }


def getDetailMainEntries(rnumber, hash_key, response_file):

    the_page = open(response_file)
    soup = BeautifulSoup(the_page, "html.parser")

    getDetailPropIDPropOwnerID(rnumber, hash_key, soup)
    table = soup.table

    owner_info_begin = 0
    owner_info_end = 0

    parcel_info_begin = 0
    parcel_info_end = 0

    owner_array = []
    parcel_array = []

    table = soup.find_all('td')
    for rows in table:
        cell_value = rows.get_text().strip()
        if re.match("Owner Information", cell_value):
            owner_info_begin = 1
            continue  # don't append this line
        if re.match("Parcel Information", cell_value):
            owner_info_end = 1
            parcel_info_begin = 1
            continue  # don't append this line
        if re.match("Values Breakdown", cell_value):
            parcel_info_end = 1

        if owner_info_begin == 1 and owner_info_end == 0:
            owner_array.append(cell_value)
        if parcel_info_begin == 1 and parcel_info_end == 0:
            parcel_array.append(cell_value)

    tables = soup.find_all('table')

    values_bd_table = tables[10]

    # values_bd_array table
    vals = values_bd_table.find_all('td')
    tmp_array = []
    for v in vals:
        # skip table included in vals.  it creats an extr td and messes up
        # assessed: key, value pair
        if v.find("table") is not None:
            continue
        value = (v.get_text().strip())
        tmp_array.append(value)

    pusharray_to_hash2(rnumber, hash_key, tmp_array)

    # used to find the correct table
    # cnt = 0
    # for table in tables:
    #     print("\n\ncnt =", cnt, table)
    #     cnt += 1

    # print(table.prettify())

    pusharray_to_hash(rnumber, hash_key, owner_array)
    pusharray_to_hash(rnumber, hash_key, parcel_array)
    # pusharray_to_hash(rnumber, hash_key, values_bd_array)

    # pp.pprint(values_bd_array)


def getRnumbersFromAdvSearchOrRnumberInput():
    '''This routine returns an array of properties. Each property entry
    is a list of [RNUM, propertyOwnerID, propertyID]'''

    properties = []

    # try: mydefaults().getvalue('DEFAULT_RNUMBERS')
    # except NameError: args.rnumbers = None

    if config['defaults']['RNUMBERS'] is False:

        # if not using -rnumbers, get the rnumbers from an
        # advanced search response

        # ADVANCED_SEARCH_RESPONSE_FILE = MyDirs().advanced_search_file()
        ADVANCED_SEARCH_RESPONSE_FILE = \
            lib.mydirs.MyDirs().advanced_search_file(".SEARCH_RESULTS.html")
        response_file = ADVANCED_SEARCH_RESPONSE_FILE
        properties = getRnumbersFromAdvancedSearchResponse(
            "",
            response_file,
            properties)

    else:
        # if specify -rnumbers "RNUM1 RNUM2"
        #         or -rnumbers "ALL"
        RNUMBERS = config['defaults']['RNUMBERS']

        # get all the cache entries
        if RNUMBERS is "ALL":
            pass
            # @RNUMBERS = keys %{$hash_global->{cache}};
        else:
            RNUMBERS_array = RNUMBERS.split()

        # if getEmptyCacheDirs(RNUMBERS_array):

        for RNUM in RNUMBERS_array:

            # found a cache entry
            if RNUM in hash_global['cache'] \
                    and config['defaults']['UPDATE_DB_FROM_SERVER'] is False:
                logger.info("{} - In the Cache".format(RNUM))

                propertyOwnerID, propertyID = \
                    getPropIDAndPropOwnerIDFromCachDetails(RNUM)

                properties.append([RNUM, propertyOwnerID, propertyID])
            else:
                # go get the rnumber page from the server
                # if -rnumbers "ALL", this else never gets entered
                # $logger->info("$RNUM - Not in Cache or DB, go get it");

                getPropIDSearchResult(RNUM)

                response_file = \
                    (lib.mydirs.MyDirs()
                     .advanced_search_file(".RNUMBER_SEARCH_RESULTS.html"))
                properties = \
                    getRnumbersFromAdvancedSearchResponse(RNUM,
                                                          response_file,
                                                          properties)

    return(properties)


def getPropIDSearchResult(RNUM):
    '''Get a single Rnumber page response.'''
    # $logger->info("** Get Property ID Search Page Response**");

    # host = config['defaults_static']['HOST_TAX_ACCESSOR']
    host = config['defaults_static']['HOST_TAX_ACCESSOR_ADVANCED']
    # host_www = config['defaults_static']['HOST_TAX_ACCESSOR_WWW']

    post = '/Property-Detail'
    url = host + post

    # values = {"PropertyQuickRefID": RNUM}
    # DATA = urllib.parse.urlencode(values).encode("utf-8")

    # headers = {}

    # passing url and data separately does not work.  just construct the url
    # and pass to Request
    url = host + post + '?PropertyQuickRefID={}'.format('R26053')
    req = urllib.request.Request(url)

    # this works
    # req = urllib.request.Request('(http://www.bastroptac.com/'
    #                              'Property-Detail?'
    #                              'PropertyQuickRefID=R26053')

    # Also works
    # url = ('http://www.bastroptac.com/Property-Detail?'
    #        'PropertyQuickRefID=R26053')
    # req = urllib.request.Request(url)

    response = urllib.request.urlopen(req)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.URLError as err:
        logging.error("jason", err)
        exit()

    # page is gzipped.  Unzip first, then decode
    the_page = response.read().decode()
    print(the_page)

    PROP_ID_SEARCH_RESPONSE_FILE_UNZIPPED = lib.mydirs.MyDirs(
    ).advanced_search_file(".RNUMBER_SEARCH_RESULTS.html")
    fh = open(PROP_ID_SEARCH_RESPONSE_FILE_UNZIPPED, "w")
    fh.write(the_page)

    return(the_page)


def getRnumbersFromAdvancedSearchResponse(rnum, response_file, properties):

    f = open(response_file, "r")
    the_page = f.read()

    soup = BeautifulSoup(the_page, "html.parser")

    # print(soup.prettify())
    # find label tags with class = ssPropertyLink
    tags = soup.find_all('label', class_='ssPropertyLink')

    rnumbers_only = []

    for t in tags:
        rnumber = t.text.strip()
        rest = t.attrs['onclick']
        array = re.search(r"\((.*)\)", rest).group(1).split(',')
        propertyownerID = array[1].strip()
        propertyID = array[2].strip()

        properties.append([rnumber, propertyownerID, propertyID])
        rnumbers_only.append(rnumber)

    # only expecting one property (ie. Property ID search, not Advanced search
    if rnum != "" and len(rnumbers_only) is not 1:
        print("\n")
        print("ERROR : ", rnum, "Property ID Search returned \
              more than one Property")
        print("        ", rnumbers_only)
        print("        Check Rnumber Search from Property tax page.")
        print("        Should only be returning only property")
        print("\n")
        exit()

    # get the property values
    # used to omit some queries
    tables = soup.find_all('table')

    # used to find the correct table
    # cnt = 0
    # for table in tables:
    #     # print("\n\ncnt =", cnt, table)
    #     cnt += 1

    values_bd_table = tables[3]

    # EXAMPLE SECTION
    # <td valign="top">
    #   <label class="ssPropertyLink" onclick="ViewPropertyOrOwners( 1 ,
    #           189371 , 65680 )">
    #     R90079
    #   </label>
    # </td>
    # <td class="ssDataColumn" valign="top">
    #   CREAMER, JOHN S JR &amp; MARY JO
    # </td>
    # <td class="ssDataColumn" textalign="left">
    #   108 KANI LN BASTROP, TX 78602
    # </td>
    # <td class="ssDataColumn" valign="top">
    #   $186,166
    # </td>

    # this is extremely slow. FIX IT.  Probably load the file use if then with
    # flags to get the values in stead of doing it all with Beautiful Soup

    for my_rnum in rnumbers_only:
        # find tag with Rnumber
        rnum_tag = values_bd_table.find('label', text=re.compile(my_rnum),
                                        attrs={'class': 'ssPropertyLink'})
        # get parent of <label> and the 3rd next sibling is the property value
        value = str((rnum_tag
                     .parent
                     .nextSibling
                     .nextSibling
                     .nextSibling
                     .get_text())).strip()
        value = re.sub(r'\$', '', value)
        value = re.sub(r',', '', value)

        hash_global['propValues'].update({my_rnum: value})

    return(properties)


def pusharray_to_hash2(rnumber, hash_key, array):

    tmp_arr = []
    for v in array:
        v = re.sub(r':$', '', v)   # : after for key names
        v = re.sub(r'\s\+', '', v)  # + listed after values
        v = re.sub(r'\s=', '', v)  # = listed after values (assessed)
        v = re.sub(r'(\d), (\d)', r'\1\2', v)  # remove commas from values only
        v = re.sub(r'\$', '', v)  # remove $ signs
        tmp_arr.append(v)

    h = altElement1(tmp_arr)
    g = altElement2(tmp_arr)

    dict_values = dict(zip(h, g))
    hash_global['DBWriteValues'][rnumber][hash_key].update(dict_values)


def pusharray_to_hash(rnumber, hash_key, array):
    array = array[:-1]

    tmp_arr = []
    for v in array:
        v = re.sub(r':$', '', v)   # : after for key names
        v = re.sub(r'\s\+', '', v)  # + listed after values
        v = re.sub(r'\s=', '', v)  # = listed after values (assessed)
        v = re.sub(r'(\d),(\d)', r'\1\2', v)  # remove commas from values only
        v = re.sub(r'\$', '', v)   # remove $ signs
        tmp_arr.append(v)

    h = altElement1(tmp_arr)
    g = altElement2(tmp_arr)

    dict_values = dict(zip(h, g))

    hash_global['DBWriteValues'][rnumber][hash_key].update(dict_values)


def altElement1(a):
    return a[0::2]


def altElement2(a):
    return a[1::2]


def getPost(page_type, my_property, response_file_suffix):

    cache_dir = lib.mydirs.MyDirs().cachedir()
    rnumber = my_property[0]
    PropertyOwnerID = my_property[1]
    PropertyID = my_property[2]
    response_file = cache_dir + '/' + rnumber + '/' + response_file_suffix

    # $logger->info("**  SERVER: GET $page_type Page : \
    #       rnum=$rnumber, poID=$PropertyOwnerID, pID=$PropertyID");
    print("**  SERVER: GET ", page_type, "Page : rnum=", rnumber, "poID=",
          PropertyOwnerID, "pID=", PropertyID)

    if page_type == "History":
        post = '/Appraisal/PublicAccess/PropertyHistory.aspx'
        values = {"PropertyID": PropertyID,
                  "NodeID": "11",
                  "FirstTaxYear": config['defaults_static']['FIRSTTAXYEAR'],
                  "LastTaxYear": config['defaults_static']['LASTTAXYEAR'],
                  "PropertyOwnerID": PropertyOwnerID}
    elif page_type == "Details":
        post = '/Appraisal/PublicAccess/PropertyDetail.aspx'
        values = {"PropertyID": PropertyID,
                  "dbKeyAuth": "Appraisal",
                  "TaxYear": "2013",
                  "NodeID": "11",
                  "PropertyOwnerID": PropertyOwnerID}
    elif page_type == "Bills":
        post = '/Appraisal/PublicAccess/PropertyBills.aspx'
        values = {"PropertyID": PropertyID,
                  "NodeID": "11",
                  "PropertyOwnerID": PropertyOwnerID}
    elif page_type == "Data":
        post = '/Appraisal/PublicAccess/PropertyDataSheet.aspx'
        values = {"PropertyID": PropertyID,
                  "PropertyOwnerID": PropertyOwnerID}
    else:
        print("page_type \"", page_type, "\" not recognized")
        exit()

    data = urllib.parse.urlencode(values).encode("utf-8")

    host = config['defaults_static']['HOST_TAX_ACCESSOR']
    url = host + post

    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)

    # print the request results to a file
    # Data is a pdf and needs to be opened as binary
    # the others are all HTML
    if page_type == 'Data':
        fh = open(response_file, 'wb')
        fh.write(response.read())
        createDataSheetXML(rnumber, response_file)

    else:
        the_page = response.read().decode()
        fh = open(response_file, "w")
        fh.write(the_page)

    fh.close()

# 	if ($request) {
#         print $fh $request->content;
# 	else {
#         print $request->status_line . "\n";


def readRnumBillsPageResponseData(rnumber, hash_key, response_file):

    getPastCurrentTotalAmntsDue(rnumber, hash_key, response_file)
    getYearlyInfo(rnumber, hash_key, response_file)
    # return1 = getPastCurrentTotalAmntsDue(rnumber, hash_key, response_file)
    # return2 = getYearlyInfo(rnumber, hash_key, response_file)
#
# 	unless ($return1 && $return2) {
# 		$logger->warn("BILLS: return1=$return1 return2=$return2");
# 		return (0)


def getPastCurrentTotalAmntsDue(rnumber, hash_key, response_file):

    # check that response file is not corrupt.
    # check_values = ("tblFees", "Past Years Due",
    #                 "Current Amount Due", "Total Amount Due")
    # return(0) unless checkValuesExistInResponseFile($response_file,
    #                                                 @check_values);

    the_page = open(response_file)
    soup = BeautifulSoup(the_page, "html.parser")

    # print(soup.prettify())

    table = soup.find('table', attrs={'id': 'tblFees'})
    # print(table.find_all('tr')[1])

    for rows in table.find_all('tr')[2:3]:
        cells = rows.find_all('td')
        value = cells[0].get_text()
        value2 = cells[1].get_text()
        value3 = cells[2].get_text()

        value3 = re.sub(r'\$', '', value3)
        value3 = re.sub(',', '', value3)

    hash_global['DBWriteValues'][rnumber][hash_key].update(
        {"Past Years Due": value})
    hash_global['DBWriteValues'][rnumber][hash_key].update(
        {"Current Amount Due": value2})
    hash_global['DBWriteValues'][rnumber][hash_key].update(
        {"Total Amount Due": value3})


def getYearlyInfo(rnumber, hash_key, response_file):

    # my @headers = ["Year", "Tax Description *", "Date Paid"];
    #
    # check that response file is not corrupt.
    # my @check_values = ("tblFees", "Year", "Tax Description *", "Date Paid");
    # return(0) unless checkValuesExistInResponseFile($response_file,
                                                    # @check_values);

    the_page = open(response_file)
    soup = BeautifulSoup(the_page, "html.parser")

    table = soup.find('table', attrs={'id': 'tblFees'})
    # print(table.prettify())

    hash_global['DBWriteValues'][rnumber][hash_key].update({'dates_paid': {}})

    last_year = None
    last_date = None
    for rows in table.find_all('tr')[4:]:
        cells = rows.find_all('td')

        year = cells[0].get_text()
        date = cells[6].get_text()

        if re.search("total", year):
            (hash_global['DBWriteValues']
             [rnumber][hash_key]['dates_paid'].update({last_year: last_date}))

        last_year = year
        last_date = date

    # get the date of the response file
    # Will be used to provide days late for payments
    # relative to the time of getting the response file

    date_response = soup.find('input', attrs={'id': 'effDate'})['value']
    hash_global['DBWriteValues'][rnumber][hash_key].update(
        {"DateResponseCaptured": date_response})


def readRnumDataSheetPageResponseData(rnumber, hash_key, response_file):

    # response_file = config['defaults_static']['DATASHEET_PAGE_XML']
    hash_key = config['defaults_static']['DATASHEET_PAGE']
    # createDataSheetXML(rnumber, response_file)
    # pdfFileObj = open(response_file, 'rb')
    # pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    #
    # # # creating a page object
    # pageObj = pdfReader.getPage(0)
    # #
    # # # extracting text from page
    # print(pageObj.extractText().split('\n'))

    with open(response_file) as f:
        lines = f.readlines()

    # pdfFileObj = open(response_file, 'r')
    # pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    found_rooms_line = 0
    foundLastTimeSold = 0
    numtimessold = 0

    for line in lines:

        # strip lines with only whitespace
        line = line.strip()

        if re.search(r'>Rooms<\/text>', line):
            found_rooms_line = 1
        elif (found_rooms_line):

            # reached the end of the sales
            if re.search(r'>Page<\/text>', line):
                break

            # remove commas from values only
            line = re.sub(r'.*>(.*)<\/text>', r'\1', line)

            # keep the name and date sold
            # could get volume and page here
            if re.search(r'\d\d\/\d\d\/\d\d\d\d', line):
                numtimessold += 1
                if foundLastTimeSold == 0:
                    line_arr = line.split("/")
                    line = "/".join([line_arr[2].strip(),
                                     line_arr[0],
                                     line_arr[1]])
                    (hash_global['DBWriteValues']
                     [rnumber][hash_key]['LastTimeSold']) = line
                    foundLastTimeSold = 1

    hash_global['DBWriteValues'][rnumber][hash_key]['NumTimesSold'] \
        = numtimessold


def createDataSheetXML(rnumber, response_file):

    command = (config['defaults_static']['PDFTOHTML_SRC']
               + ' -xml '
               + response_file)
    subprocess.check_output("sleep 2", shell=True)
    subprocess.check_output(command, shell=True)
    # subprocess.call(command, shell=True)
    print("2. ", response_file)
    # process = subprocess.Popen(command, shell=True)
    # process.wait()
    # subprocess.run(['/Users/j_honky/Downloads/pdftohtml-0.40a/src/pdftohtml'],['-xml'],['/Users/j_honky/code/getrealty/python_version/cache/R70097/DATASHEET_PAGE.pdf'])


def getAdvancedSearchPageResponse():
    '''Return the table from Advanced search response in json format.  This is
    easier to parse than HTML data'''

    print(' jaf DEBUG - need to write parser for this json data')

    headers = {}  # header info is not needed

    # create the request with variables
    values = {
        'pn': '1',
        'PropertyID': 'R53677',
        'NameFirst': '',
        'NameLast': '',
        'PropertyOwnerID': '',
        'BusinessName': '',
        'StreetNoFrom': '',
        'StreetNoTo': '',
        'StreetName': '',
        'City': '',
        'ZipCode': '',
        'Neighborhood': '',
        'pStatus': 'All',
        'AbstractSubdivisionCode': config['defaults']['SUBDIVISION'],
        'AbstractSubdivisionName': '',
        'Block': '',
        'TractLot': '',
        'AcresFrom': config['defaults']['ACRES_LEAST'],
        'AcresTo': config['defaults']['ACRES_MOST'],
        'ty': '2018',
        'pvty': '2018',
        'pt': 'RP%3BMH%3BNR%3BPP',
        'st': '9',
        'so': '1',
        'take': '20',
        'skip': '0',
        'page': '1',
        'pageSize': '20HTTP/1.1 200 OK',
    }

    host = config['defaults_static']['HOST_TAX_ACCESSOR_ADVANCED']
    post = '/ProxyT/Search/Properties/advancedsearch'
    url = host + post

    data = urllib.parse.urlencode(values).encode("utf-8")

    req = urllib.request.Request(url, data, headers)
    response = urllib.request.urlopen(req)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.URLError as err:
        logging.error("jason", err)
        exit()

    # page is gzipped.  Unzip first, then decode
    # the_page = gzip.decompress(response.read()).decode()
    the_page = response.read().decode()

    ADVANCED_SEARCH_RESPONSE_FILE = \
        lib.mydirs.MyDirs().advanced_search_file(".SEARCH_RESULTS.html")
    # print(ADVANCED_SEARCH_RESPONSE_FILE)

    fh = open(ADVANCED_SEARCH_RESPONSE_FILE, "w")
    fh.write(the_page)


def checkValuesExistInResponseFile(response_file, check_names):
    pass
    #
    # my $fh = new FileHandle;
    # unless (open ($fh, $response_file)) {
    # 	$logger->error("ERROR: cannot open the file '$response_file': $!");
    #
    # my $tmp_hash;
    #
    # while (my $line = <$fh>) {
    #
    # 	my $looparray = 0;
    #
    # 	foreach my $name (@check_names) {
    # 		$looparray++;
    # 		if ($line =~ /$name/) {
    # 			$tmp_hash->{$looparray} = 1;
    # close $fh;
    #
    # my $num_keys = keys %{$tmp_hash};
    # my $num_checks = $#check_names + 1;
    #
    # if ($num_keys eq $num_checks) {
    # 	return(1);
    # else {
    # 	return(0);


def getPropIDAndPropOwnerIDFromCachDetails(RNUM):

    print(RNUM, "found in cache")

    cache_dir = lib.mydirs.MyDirs().cachedir()
    response_file = (
        "/".join([cache_dir,
                  RNUM,
                  config['defaults_static']['PROP_DETAIL_RESULTS']]))

    AssessedValOnNextLine = 0
    for line in open(response_file, "r"):
        # print(line)
        if re.search(r'PropertyID=(\d+)', line):
            my_search = re.search(r'PropertyID=(\d+)', line)
            propertyID = my_search.group(1)
        if re.search(r'PropertyOwnerID=(\d+)', line):
            propertyOwnerID = my_search.group(1)

        if re.search(r'Assessed:', line):
            AssessedValOnNextLine = 1
            # propertyOwnerID = 1;
        elif AssessedValOnNextLine == 1:
            value = line
            value = re.sub(r'^\s+', '', value)  # remove beginning whitespace
            value = re.sub(r'\$', '', value)  # remove Dollar sign
            value = re.sub(r',', '', value)  # remove comma
            value = re.sub(r'(\d+).*', '\1', value)

            # chomp($value); # for some reason has to be last!

            AssessedValOnNextLine = 0
            hash_global['propValues']['RNUM'] = value

    # close $fh;

    return(propertyOwnerID, propertyID)

# ####################################
# sub getDetailEntityCodes {
#
# 	my ($rnumber, $hash_key, $response_file) = @_;
#
# 	my $te = HTML::TableExtract->new( depth => 2, count => 3, gridmap => 0);
# 	$te->parse_file($response_file);
# 	my $report = $te->tables_report(1, "|");
# 	#print $report;
#
# 	my @array;
# 	# All Exemption codes are stored in a single key
# 	foreach my $ts ($te->tables) {
# 		foreach my $row ($ts->rows) {
#
#             my $key   = @$row[0];
# 			my @temp_array = split ("\n", $key);
#
# 			push (@array, @temp_array);
#
# 		}
# 	}
#
# $hash_global['DBWriteValues']->{$rnumber}->{$hash_key}->{Entity_Codes} \
#   = \@array;

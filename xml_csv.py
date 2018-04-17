# import modules
import time
import gzip
import csv
import xml.etree.ElementTree as ET
import glob
import json
import argparse
import sys
import os

# define function that constructs the name for an attribute
def getAttributeName(_attr_name, _attr_attribute, _el_name, _el_tag, _el_extends):

    # if there is a specified name for the attribute
    if _attr_name is not None:
        return _attr_name
    # else if the element extends another element
    elif _el_extends is not None:
        return _attr_attribute
    # else if there is a specified name for the element
    elif _el_name is not None:
        return _el_name + "_" + _attr_attribute
    # else if there is no specified names for neither
    else:
        return _el_tag + "_" + _attr_attribute

# define function that constructs a tag name of an element
def getNamespace(_key, _namespace):

    # if there is no namespace defined
    if _namespace is None:
        return _key
    # else if there is no list of namespaces provided
    elif namespaces is None:
        return "{" + _namespace + "}" + _key
    # else if there is both a namespace and a list provided
    else:
        return "{" + namespaces[_namespace] + "}" + _key


# define the element reader
def readElement(_structure, _tree, _vars, _colsuffix):

    global csv_writer
    global rows
    global counter
    global input_datafiles

    # set default properties of the element
    _element = {
        "tag": None,
        "name": None,
        "extends": None,
        "namespace": None,
        "attributes": None,
        "text": False,
        "row": False,
        "multiple": False,
        "columns": 1,
        "children": None
    }

    # update the element with the passed structure
    _element.update(_structure)

    # check if element is extending other elements
    if _element['extends'] is not None:

        # start with an empty list
        els = []

        # loop through each extended element
        for extend in _element['extends']:

            # put the found extended element in the list
            els.append(_tree.find(getNamespace(extend, _element['namespace'])))

    # check if the element occurs multiple times in either rows or columns
    elif _element['multiple'] is True or _element['columns'] > 1:

        # find all elements (which returns a list)
        els = _tree.findall(getNamespace(_element['tag'], _element['namespace']))

    # if not multiple
    else:

        # put first found element in a list
        els = [_tree.find(getNamespace(_element['tag'], _element['namespace']))]

    # get the tree element() with correct namespace if provided
    for index, el in enumerate(els):

        # quit if no element is found
        if el is None:
            continue

        # construct the suffix for the column name (if there's multiple columns with the same tag)
        colsuffix = ""
        if _colsuffix is not "":
            colsuffix += _colsuffix
        if _element['columns'] > 1:
            colsuffix += "_" + str(index + 1)

        # check if there are any attributes on the element
        if _element['attributes'] is not None:

            # loop through them
            for attribute in _element['attributes']:

                # set default properties of attribute
                _attribute = {
                    "attribute": None,
                    "name": None,
                    "namespace": None
                }

                # update the attribute
                _attribute.update(attribute)

                # get the column name
                colname = getAttributeName(_attribute['name'], _attribute['attribute'], _element['name'], _element['tag'], _element['extends']) + colsuffix

                # get the attribute value
                value = el.get(getNamespace(_attribute['attribute'], _attribute['namespace']))

                # add attribute value to the vars
                _vars.update({ colname: value })

        # check if the text content should be saved
        if _element['text'] is True:

            # get the column name
            colname = (_element['tag'] if _element['name'] is None else _element['name']) + colsuffix

            # get the text value
            value = el.text

            # add text content to the vars
            _vars.update({ colname: value })

        # check if element should be a row in the result
        if _element['row'] is False:

            # check if there are children to the element
            if _element['children'] is not None:

                # loop through them
                for child in _element['children']:

                    # read each element
                    readElement(child, el, _vars, colsuffix)

        # element is indeed a row
        else:

            # from this point, every new value is unique for the row, so we create a copy of the vars up to this point
            row_vars = _vars.copy()

            # check if there are children to the element
            if _element['children'] is not None:

                # loop through them
                for child in _element['children']:

                    # read each element
                    readElement(child, el, row_vars, colsuffix)

            # write a row in the csv file
            csv_writer.writerow(row_vars)

            # output to system
            rows += 1
            if rows % 1000 == 0:
                print("\rFile: " + str(file_counter) + "/" + str(len(input_datafiles)) + " - Rows written: " + str(rows), end="")


# define the column name reader
def getColumnNames(_structure, _cols, _colsuffix):

    # set default properties of the element
    _element = {
        "tag": None,
        "name": None,
        "extends": None,
        "namespace": None,
        "attributes": None,
        "text": False,
        "row": False,
        "multiple": False,
        "columns": 1,
        "children": None
    }

    # update the element with the passed structure
    _element.update(_structure)

    # start counter
    i = 1
    while i < _element['columns'] + 1:

        # construct the suffix for the column name (if there's multiple columns with the same tag)
        colsuffix = ""
        if _colsuffix is not "":
            colsuffix += _colsuffix
        if _element['columns'] > 1:
            colsuffix += "_" + str(i)

        # check if there are any attributes on the element
        if _element['attributes'] is not None:

            # loop through them
            for attribute in _element['attributes']:

                # set default properties of attribute
                _attribute = {
                    "attribute": None,
                    "name": None,
                    "namespace": None
                }

                # update the attribute
                _attribute.update(attribute)

                # get the column name
                colname = getAttributeName(_attribute['name'], _attribute['attribute'], _element['name'], _element['tag'], _element['extends']) + colsuffix

                # add attribute to columns if it doesn't exist yet
                if colname not in _cols:
                    _cols.append(colname)

        # check if the text content should be saved
        if _element['text'] is True:

            # get the column name
            colname = (_element['tag'] if _element['name'] is None else _element['name']) + colsuffix

            # add tag to columns
            if colname not in _cols:
                _cols.append(colname)

        # check if there are children to the element
        if _element['children'] is not None:

            # loop through them
            for child in _element['children']:

                # read each element
                getColumnNames(child, _cols, colsuffix)

        # increase counter
        i += 1

    # return the list of column names
    return _cols

# function that converts one file
def convertFile(datafile, outputfolder, counter):

    global input_datafiles
    global file_counter
    global csv_writer

    # set the file counter
    file_counter = counter

    # use current folder as output folder if none is given
    if outputfolder is None:
        outputfolder = os.path.dirname(datafile.name)
    else:
        # check if output directory actually exists
        if not os.path.exists(os.path.dirname(outputfolder)):
            os.makedirs(os.path.dirname(outputfolder))
        outputfolder = os.path.dirname(outputfolder)

    # read the data file
    data = datafile.read()

    # parse xml data into an element tree
    tree = ET.fromstring(data)

    # initialize the row counter
    global rows
    rows = 0

    # get all the field names
    fieldnames = getColumnNames(structure, [], "")

    # create a csv file
    csv_file = open(outputfolder + "/" + os.path.basename(datafile.name) + ".csv", 'w')
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction='ignore', delimiter=',')
    csv_writer.writeheader()

    # start with reading the structure
    readElement(structure, tree, {}, "")

    # write the final number of rows written
    print("\rFile: " + str(file_counter) + "/" + str(len(input_datafiles)) + " - Rows written: " + str(rows))


# parse options given to script
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data", help="The data source file (or path to files with trailing '/') to be converted (.xml or .gz)", metavar="", default="data.xml")
parser.add_argument("-s", "--structure", help="The structure file to be used (.json)", metavar="", default="structure.json")
parser.add_argument("-ns", "--namespaces", help="The namespaces to be used (.json)", metavar="")
parser.add_argument("-o", "--output", help="The output folder with trailing '/', defaults to source location", metavar="")
options = parser.parse_args()

# save options to variables
input_datafile = options.data
input_structure = options.structure
input_namespaces = options.namespaces
input_outputfolder = options.output

# start timer
timer = time.time()

# output that we're doing something
print("\nPreparing everything... (The script can be aborted by pressing ctrl+c)")

# open and parse namespaces json
if input_namespaces is not None:
    namespacesfile = open(input_namespaces, "r") if input_namespaces[-4:] == "json" else sys.exit("Error: Provided namespaces file is not a .json file.")
    namespaces = json.load(namespacesfile)
else:
    namespaces = None

# open and parse structure json
structurefile = open(input_structure, "r") if input_structure is not None and input_structure[-4:] == "json" else sys.exit("Error: Provided structure file is not a .json file.")
structure = json.load(structurefile)

# start with empty list of data files
input_datafiles = []

# fill the list of data files
if "," in input_datafile:
    input_datafiles.extend(input_datafile.split(","))
elif input_datafile[-1:] == "/":
    input_datafiles.extend(glob.glob(input_datafile + "*.gz"))
    input_datafiles.extend(glob.glob(input_datafile + "*.xml"))
else:
    input_datafiles.extend(input_datafile)

# loop through the input files
for i, input_datafiles_item in enumerate(input_datafiles):

    # check which file reader should be used
    if input_datafiles_item[-3:] == ".gz":
        convertFile(gzip.open(input_datafiles_item), input_outputfolder, i+1)
    elif input_datafiles_item[-4:] == ".xml":
        convertFile(open(input_datafiles_item, "r"), input_outputfolder, i+1)
    else:
        sys.exit("Error: Provided data source file is not a .gz or .xml file.")

# print duration of script execution
print("Finished in " + str(round(time.time() - timer, 2)) + " seconds\n")
print("\a")

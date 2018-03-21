# import modules
import time
import gzip
import csv
import xml.etree.ElementTree as ET
import glob
import json
import argparse
import sys

# parse options given to script
parser = argparse.ArgumentParser()
parser.add_argument("data", help="The data source file to be converted (.xml or .gz)")
parser.add_argument("structure", help="The structure file to be used (.json)")
parser.add_argument("--namespaces", help="The namespaces to be used (.json)", metavar="")
parser.add_argument("--output", help="The output file to be generated, defaults to source file name and location", metavar="")
options = parser.parse_args()

# save options to variables
input_datafile = options.data
input_structure = options.structure
input_namespaces = options.namespaces or "examples/namespaces/namespaces.json"
input_outputfile = options.output or options.data + ".csv"

# start timer
timer = time.time()

# output that we're doing something
print("\nPreparing everything... (The script can be aborted by pressing ctrl+c)")

# open and parse namespaces json
namespacesfile = open(input_namespaces, "r") if input_namespaces is not None and input_namespaces[-4:] == "json" else sys.exit("Error: Provided namespaces file is not a .json file.")
namespaces = json.load(namespacesfile)

# open and parse structure json
structurefile = open(input_structure, "r") if input_structure is not None and input_structure[-4:] == "json" else sys.exit("Error: Provided structure file is not a .json file.")
structure = json.load(structurefile)

# open and read data file
if input_datafile[-2:] == "gz":
    datafile = gzip.open(input_datafile)
elif input_datafile[-3:] == "xml":
    datafile = open(input_datafile, "r")
else:
    sys.exit("Error: Provided data source file is not a .gz or .xml file.")
data = datafile.read()

# parse xml data into an element tree
tree = ET.fromstring(data)

# initialize the row counter
rows = 0

# define the element reader
def readElement(_structure, _tree, _vars):

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
        "children": None
    }

    # update the element with the passed structure
    _element.update(_structure)

    # check if element is extending other elements
    if _element['extends'] is not None:

        els = []

        # loop through each extended element
        for extend in _element['extends']:

            # put the extended element in the list
            els.append(_tree.find(extend if _element['namespace'] is None else "{" + namespaces[_element['namespace']] + "}" + extend))

        # print(els)

    # check if the element occurs multiple times
    elif _element['multiple'] is True:

        # find all elements
        els = _tree.findall(_element['tag'] if _element['namespace'] is None else "{" + namespaces[_element['namespace']] + "}" + _element['tag'])

    # if not multiple
    else:

        # put first element in list
        els = [_tree.find(_element['tag'] if _element['namespace'] is None else "{" + namespaces[_element['namespace']] + "}" + _element['tag'])]

    # get the tree element() with correct namespace if provided
    for index, el in enumerate(els):

        # quit if no element is found
        if el is None:
            continue

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

                # add attribute value to the vars
                _vars.update({ ((((_element['tag'] if _element['name'] is None else _element['name']) + '_' if _element['extends'] is None else '') + _attribute['attribute']) if _attribute['name'] is None else _attribute['name']): el.get(_attribute['attribute'] if _attribute['namespace'] is None else "{" + namespaces[_attribute['namespace']] + "}" + _attribute['attribute']) })

        # check if the text content should be saved
        if _element['text'] is True:

            # add text content to the vars
            _vars.update({ (_element['tag'] if _element['name'] is None else _element['name']): el.text })

        # check if element should be a row in the result
        if _element['row'] is True:

            # from this point, every new value is unique for the row, so we create a copy of the current vars
            row_vars = _vars.copy()

            # check if there are children to the element
            if _element['children'] is not None:

                # loop through them
                for child in _element['children']:

                    # read each element
                    readElement(child, el, row_vars)

            # write a row in the csv file
            global csv_writer
            csv_writer.writerow(row_vars)

            # output to system
            global rows
            rows += 1
            if rows % 150 == 0:
                print("\rRows written: " + str(rows), end="")



        # element is not a row
        else:

            # check if there are children to the element
            if _element['children'] is not None:

                # loop through them
                for child in _element['children']:

                    # read each element
                    readElement(child, el, _vars)


# define the column name reader
def getColumnNames(_structure, _cols):

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
        "children": None
    }

    # update the element with the passed structure
    _element.update(_structure)

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

            colname = (((_element['tag'] if _element['name'] is None else _element['name']) + "_" if _element['extends'] is None else '') + _attribute['attribute']) if _attribute['name'] is None else _attribute['name']

            # add attribute to columns if it doesn't exist yet
            if colname not in _cols:
                _cols.append(colname)

    # check if the text content should be saved
    if _element['text'] is True:

        colname = _element['tag'] if _element['name'] is None else _element['name']

        # add tag to columns
        if colname not in _cols:
            _cols.append(colname)

    # check if there are children to the element
    if _element['children'] is not None:

        # loop through them
        for child in _element['children']:

            # read each element
            getColumnNames(child, _cols)


    # return the list of column names
    return _cols

# get all the field names
fieldnames = getColumnNames(structure, [])

# create a csv file
csv_file = open(input_outputfile, 'w')
csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction='ignore', delimiter=',')
csv_writer.writeheader()

# start with reading the structure
readElement(structure, tree, {})

# write the final number of rows written
print("\rRows written: " + str(rows))

# print duration of script execution
print("Finished in " + str(round(time.time() - timer, 2)) + " seconds\n")

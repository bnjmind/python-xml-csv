# import modules
import time
import gzip
import csv
import xml.etree.ElementTree as ET
from pick import pick
import glob
import os

# clear console
os.system('cls' if os.name=='nt' else 'clear')

# show a file prompt
files = glob.glob('../1_data/*.gz')
chosen_file, file_index = pick(files, 'Choose a gzipped data file:')

# start timer
timer = time.time()

print("Working...")

# define some name spaces
namespaces = {
    "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
    "datex2": "http://datex2.eu/schema/2/2_0",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}

# define the structure in which the data is represented (see ../0_info/structure.xlsx for info)
structure = {
    "tag": "Body",
    "namespace": "soapenv",
    "children": [
        {
            "tag": "d2LogicalModel",
            # "namespace": "datex2",
            "children": [
                {
                    "tag": "payloadPublication",
                    "namespace": "datex2",
                    "children": [
                        {
                            "tag": "measurementSiteTableReference",
                            "name": "locTableRef",
                            "namespace": "datex2",
                            "attributes": [
                                {
                                    "key": "id",
                                    "name": "locTableID"
                                },
                                {
                                    "key": "version",
                                    "name": "locTableVersion"
                                }
                            ]
                        },
                        {
                            "tag": "siteMeasurements",
                            "namespace": "datex2",
                            "multiple": True,
                            "children": [
                                {
                                    "tag": "measurementSiteReference",
                                    "namespace": "datex2",
                                    "attributes": [
                                        {
                                            "key": "id",
                                            "name": "locID"
                                        },
                                        {
                                            "key": "version",
                                            "name": "locVersion"
                                        }
                                    ]
                                },
                                {
                                    "tag": "measurementTimeDefault",
                                    "name": "mTime",
                                    "namespace": "datex2",
                                    "text": True
                                },
                                {
                                    "tag": "measuredValue",
                                    "namespace": "datex2",
                                    "attributes": [
                                        {
                                            "key": "index",
                                            "name": "locIndex"
                                        }
                                    ],
                                    "row": True,
                                    "multiple": True,
                                    "children": [
                                        {
                                            "tag": "measurementEquipmentTypeUsed",
                                            "namespace": "datex2",
                                            "children": [
                                                {
                                                    "tag": "values",
                                                    "namespace": "datex2",
                                                    "children": [
                                                        {
                                                            "tag": "value",
                                                            "name": "mEquipmentX",
                                                            "namespace": "datex2",
                                                            "text": True
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            "tag": "measuredValue",
                                            "namespace": "datex2",
                                            "children": [
                                                {
                                                    "tag": "basicData",
                                                    "namespace": "datex2",
                                                    "attributes": [
                                                        {
                                                            "key": "type",
                                                            "name": "mTypeX",
                                                            "namespace": "xsi"
                                                        }
                                                    ],
                                                    "children": [
                                                        {
                                                            "tag": "measurementOrCalculationTime",
                                                            "name": "mTimeX",
                                                            "namespace": "datex2",
                                                            "text": True
                                                        },
                                                        {
                                                            "tag": "vehicleFlow",
                                                            "namespace": "datex2",
                                                            "children": [
                                                                {
                                                                    "tag": "vehicleFlowRate",
                                                                    "name": "mVehicleFlowRate",
                                                                    "namespace": "datex2",
                                                                    "text": True
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "tag": "averageVehicleSpeed",
                                                            "namespace": "datex2",
                                                            "children": [
                                                                {
                                                                    "tag": "speed",
                                                                    "name": "mSpeed",
                                                                    "namespace": "datex2",
                                                                    "text": True
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "tag": "travelTimeType",
                                                            "name": "mTravelTimeType",
                                                            "namespace": "datex2",
                                                            "text": True
                                                        },
                                                        {
                                                            "tag": "travelTime",
                                                            "namespace": "datex2",
                                                            "children": [
                                                                {
                                                                    "tag": "duration",
                                                                    "name": "mDuration",
                                                                    "namespace": "datex2",
                                                                    "text": True
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "tag": "trafficStatus",
                                                            "namespace": "datex2",
                                                            "children": [
                                                                {
                                                                    "tag": "trafficStatusValue",
                                                                    "name": "mTrafficStatus",
                                                                    "namespace": "datex2",
                                                                    "text": True
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "extends": [
                                                                "vehicleFlow",
                                                                "averageVehicleSpeed",
                                                                "travelTime",
                                                                "trafficStatus"
                                                            ],
                                                            "namespace": "datex2",
                                                            "attributes": [
                                                                {
                                                                    "key": "computationalMethod",
                                                                    "name": "mCompMethodX"
                                                                },
                                                                {
                                                                    "key": "numberOfIncompleteInputs",
                                                                    "name": "mNumInputsIncomp"
                                                                },
                                                                {
                                                                    "key": "numberOfInputValuesUsed",
                                                                    "name": "mNumInputsUsed"
                                                                },
                                                                {
                                                                    "key": "standardDeviation",
                                                                    "name": "mStDev"
                                                                },
                                                                {
                                                                    "key": "supplierCalculatedDataQuality",
                                                                    "name": "mAccuracyX"
                                                                }
                                                            ],
                                                            "children": [
                                                                {
                                                                    "tag": "dataError",
                                                                    "name": "mError",
                                                                    "namespace": "datex2",
                                                                    "text": True
                                                                },
                                                                {
                                                                    "tag": "reasonForDataError",
                                                                    "namespace": "datex2",
                                                                    "children": [
                                                                        {
                                                                            "tag": "values",
                                                                            "namespace": "datex2",
                                                                            "children": [
                                                                                {
                                                                                    "tag": "value",
                                                                                    "name": "mErrorReason",
                                                                                    "namespace": "datex2",
                                                                                    "text": True
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}

# open file
datafile = gzip.open(chosen_file)

# read content
data = datafile.read()

# parse data
tree = ET.fromstring(data)

# define the element reader
def readElement(_structure, _tree, _vars):

    # if (time.time() - timer) > 15: return

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
                    "key": None,
                    "name": None,
                    "namespace": None
                }

                # update the attribute
                _attribute.update(attribute)

                # add attribute value to the vars
                _vars.update({ ((((_element['tag'] if _element['name'] is None else _element['name']) + '_' if _element['extends'] is None else '') + _attribute['key']) if _attribute['name'] is None else _attribute['name']): el.get(_attribute['key'] if _attribute['namespace'] is None else "{" + namespaces[_attribute['namespace']] + "}" + _attribute['key']) })

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
                "key": None,
                "name": None,
                "namespace": None
            }

            # update the attribute
            _attribute.update(attribute)

            colname = (((_element['tag'] if _element['name'] is None else _element['name']) + "_" if _element['extends'] is None else '') + _attribute['key']) if _attribute['name'] is None else _attribute['name']

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
csv_file = open('../3_results/' + os.path.basename(datafile.name)[:-3] + '.csv', 'w', newline='')
csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction='ignore', delimiter=',')
csv_writer.writeheader()

# start with reading the structure
readElement(structure, tree, {})

# print duration of script execution
print("Finished in " + str(time.time() - timer) + " seconds")

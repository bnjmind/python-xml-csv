# python-xml-csv
Convert an XML file to a CSV using a predefined structure. It can be used to convert a complexly structured XML file to a CSV file that has unique cases on each row. Which tag and attribute values are included in the CSV file are defined beforehand by the user.

## 0. Usage
```
python3 xml_csv.py data structure [--namespaces] [--output]
```
Where 'data' is a relative path to an .xml or .gz file, 'structure' and '--namespaces' are relative paths to .json files, and '--output' is a relative path to a .csv file.

## 1. Structure file
A structure file defines how the XML file should be read and converted to a CSV file. It consists of a tree of element dictionaries (see below) that describes how the XML file is structured. **Note:** The root element of the XML should not be included.

### 1.1. Element dictionary

Key        | Type                           | Default | Required
-----------|--------------------------------|---------|--------------------------
tag        | String                         | None    | Yes, if 'extends' is None
name       | String                         | None    | No
extends    | List of 'tags'                 | None    | Yes, if 'tag' is None
namespace  | String                         | None    | No
attributes | List of Attribute dictionaries | None    | No
text       | Boolean                        | False   | No
row        | Boolean                        | False   | No
multiple   | Boolean                        | False   | No
columns    | Integer                        | 1       | No
children   | List of Element dictionaries   | None    | No

#### tag
The tag name of the element in the XML file.

#### name
Used to change variable name to this instead of the default which is the 'tag'. Useful when 'tag' does not tell much.

#### extends
Used to extend keys of this element object, to multiple other element objects.

Extended elements cannot have 'multiple' set to True.
The extend Element Object must have the same namespace of the extended elements and cannot have 'text', 'row', or 'multiple' set to True.

#### namespace
The namespace used for the tag name.

#### attributes
Used to save the attributes of the element.

#### text
Used to save the text content of the element.

#### row
Identifies if each of this element should be one row in the resulting CSV file.

Can only be true if:
1. No other element in the structure has 'row' set to True.

#### multiple
Identifies if the element occurs multiple times in the file.

Can only be true if:
1. No other elements on the same level (i.e. in the same array of Element Objects) have 'multiple' set to True.
2. Element is a descendant of an element that has 'multiple' set to True, or no element has 'multiple' set to True yet at all.
3. Element is not a descendant of an element that has 'row' set to True. Use the 'columns' option in that case.

#### columns
Used to define elements that are repeated in a single row. Column names will have a suffix to make them unique.

#### children
Used to identify direct children of the current element in the XML file.

### 1.2. Attribute dictionary

Key       | Type   | Default | Required
----------|--------|---------|---------
attribute | String | None    | Yes
name      | String | None    | No
namespace | String | None    | No

#### attribute
The attribute name.

#### name
Used to overwrite the default variable name that is generated (which is [tag]/[name]\_[attribute]).

#### namespace
The namespace used for the attribute name.

## 2. Example

### 2.1. Data source file (.xml or .gz)
```
<?xml version="1.0"?>
<root>
  <measurements>
    <measurementtime>11:00</measurementtime>
    <measurement>
      <location id="1" name="station_a" />
      <values>
        <item index="1">
          <value>12000</value>
          <unit>ms</unit>
        </item>
        <item index="2">
          <value>12</value>
          <unit>s</unit>
        </item>
      </values>
    </measurement>
    <measurement>
      <location id="2" name="station_b" />
      <values>
        <item index="1">
          <value>22000</value>
          <unit>ms</unit>
        </item>
        <item index="2">
          <value>22</value>
          <unit>s</unit>
        </item>
        <item index="3">
          <value>0.37</value>
          <unit>min</unit>
        </item>
      </values>
    </measurement>
  </measurements>
  <measurements>
    <measurementtime>12:00</measurementtime>
    <measurement>
      <location id="1" name="station_a" />
      <values>
        <item index="1">
          <value>13000</value>
          <unit>ms</unit>
        </item>
        <item index="2">
          <value>13</value>
          <unit>s</unit>
        </item>
      </values>
    </measurement>
    <measurement>
      <location id="2" name="station_b" />
      <values>
        <item index="1">
          <value>23000</value>
          <unit>ms</unit>
        </item>
        <item index="2">
          <value>23</value>
          <unit>s</unit>
        </item>
        <item index="3">
          <value>0.38</value>
          <unit>min</unit>
        </item>
      </values>
    </measurement>
  </measurements>
</root>
```

### 2.2. Structure file (.json)
```
{{
  "tag": "measurements",
  "multiple": true,
  "children": [
    {
      "tag": "measurementtime",
      "name": "time",
      "text": true
    },
    {
      "tag": "measurement",
      "multiple": true,
      "row": true,
      "children": [
        {
         "tag": "location",
         "attributes": [
           {
             "attribute": "id",
             "name": "locID"
           },
           {
             "attribute": "name"
           }
         ]
        },
        {
         "tag": "values",
         "children": [
           {
             "tag": "item",
             "attributes": [
               {
                 "attribute": "index"
               }
             ],
             "columns": 3,
             "children": [
               {
                 "tag": "value",
                 "text": true
               },
               {
                 "tag": "unit",
                 "text": true
               }
             ]
           }
         ]
        }
      ]
    }
  ]
}
```

### 2.3. Output file
```
time,locID,location_name,item_index_1,value_1,unit_1,item_index_2,value_2,unit_2,item_index_3,value_3,unit_3
11:00,1,station_a,1,12000,ms,2,12,s,,,
11:00,2,station_b,1,22000,ms,2,22,s,3,0.37,min
12:00,1,station_a,1,13000,ms,2,13,s,,,
12:00,2,station_b,1,23000,ms,2,23,s,3,0.38,min
```
Formatted:

time  | locID | location_name | item_index_1 | value_1 | unit_1 | item_index_2 | value_2 | unit_2 | item_index_3 | value_3 | unit_3
------|-------|---------------|--------------|---------|--------|--------------|---------|--------|--------------|---------|-------
11:00 | 1     | station_a     | 1            | 12000   | ms     | 2            | 12      | s      |              |         |
11:00 | 2     | station_b     | 1            | 22000   | ms     | 2            | 22      | s      | 3            | 0.37    | min
12:00 | 1     | station_a     | 1            | 13000   | ms     | 2            | 13      | s      |              |         |
12:00 | 2     | station_b     | 1            | 23000   | ms     | 2            | 23      | s      | 3            | 0.38    | min

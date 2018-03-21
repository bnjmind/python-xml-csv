# python-xml-csv
Convert an XML file to a CSV using a predefined structure. It can be used to convert a complexly structured XML file to a CSV file that has unique cases on each row. Which tag and attribute values are included in the CSV file are defined beforehand by the user.

## 0. Usage
1. Start the program
2. Choose the data source file
3. Choose the structure file
4. Choose the output file

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

### 2.1. Data source file
```
<?xml version="1.0"?>
<root>
  <measurements>
    <location id="192" name="station_a" />
    <values>
      <value id="1">13</value>
      <value id="2">27</value>
      <value id="3">8</value>
    </values>
  </measurements>
</root>
```

### 2.2. Structure file
```
{
  "tag": "measurements",
  "children": [

    {
      "tag": "location",
      "attributes": [
        {
          "attribute": "id",
          "name": "locationID"
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
          "tag": "value",
          "multiple": True,
          "row": True,
          "text": True,
          "attributes": [
            {
              "attribute": "id",
              "name": "valueID"
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
locationID,location_name,valueID,value
192,station_a,1,13
192,station_a,2,27
192,station_a,3,8
```
Formatted:

locationID | location_name | valueID | value
-----------|---------------|---------|------
192        | station_a     | 1       | 13
192        | station_a     | 2       | 27
192        | station_a     | 3       | 8

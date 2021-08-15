# s3s
AWS S3 Simplified - minimize amount of code for storing / loading / listing / deleting objects stored in AWS S3 via a `dict`- like interface.

## Installation 

`pip install https://github.com/iaroslav-ai/s3s/archive/refs/heads/main.zip`

## What this library can do

```python
from s3s import S3

# create s3 wrapper with root path s3://some-bucket/path1/path2
s3 = S3('some-bucket', 'path1', 'path2')

# serialize and store json object in s3://some-bucket/path1/path2/data.json
eg_json = {'key': 'value', 'key2': [1,2,3]}
s3['data.json'] = eg_json

# load and deserialize json object from s3://some-bucket/path1/path2/data.json
loaded_json = s3['data.json']
assert loaded_json == eg_json

# store pandas dataframe in s3 as .csv file in s3://some-bucket/path1/path2/data.csv
import pandas as pd  
eg_df = pd.DataFrame({'C1': [1, 2], 'C2': [3, 4]})
s3['data.csv'] = eg_df
assert eg_df.equals(s3['data.csv'])

# store arbitrary object in s3 at s3://some-bucket/path1/path2/object.pkl
s3['object.pkl'] = lambda x: x*x

# loading arbitrary python object from s3://some-bucket/path1/path2/object.pkl
# warning: do not load from untrusted sources!
loaded_square_func = s3['object.pkl']
assert loaded_square_func(3) == 3*3

# A subset of data types is supported currently. See source code for details
try:
    s3['data.zip'] = 'abc'
except ValueError as ex:
    pass

# write json to s3://some-bucket/path1/path2/subpath/object.json
s3['subpath', 'object.json'] = eg_json
assert s3['subpath', 'object.json'] == eg_json

# check if object exist or not
assert 'object.pkl' in s3
assert ('subpath', 'object.json') in s3
assert ('random', 'path.pkl') not in s3

# create an S3 object pointing at a "subdirectory" of the parent S3 object
subpath_s3 = s3['subpath']
assert subpath_s3['object.json'] == s3['subpath', 'object.json']

# list objects in root s3 path - s3://some-bucket/path1/path2 including other subpath 
obj_list = [key for key in s3]
assert 'data.csv' in obj_list
assert 'subpath' in obj_list  

# list a "subdirectory" 
for key in s3['subpath']:
    # the only key 
    assert 'object.json' == key

# delete s3://some-bucket/path1/path2/data.csv
del s3['data.csv']
assert 'data.csv' not in s3

# get size of s3://some-bucket/path1/path2/data.json object in bytes
json_size = s3.size('data.json')
assert json_size == 35

# get url of some key of `S3` object
s3_uri = s3.uri('subpath', 'object.json')
assert s3_uri == 's3://some-bucket/path1/path2/subpath/object.json'
```
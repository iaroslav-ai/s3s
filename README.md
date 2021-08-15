# s3s
AWS S3 Simplified - minimize amount of code for storing / loading / listing / deleting objects stored in AWS S3 via a `dict`- like interface.


## How to use this library


```
from s3s import S3

# create s3 wrapper with root path s3://some-bucket/path1/path2
s3 = S3('some-bucket', 'path1', 'path2')

# serialize and store json object in s3://some-bucket/path1/path2/data.json
eg_json = {'key': 'value', 'key2': [1,2,3]}
s3['data.json'] = eg_json

# load and deserialize json object from s3://some-bucket/path1/path2/data.json
loaded_json = s3['data.json']
assert loaded_json == eg_json

# write json to s3://some-bucket/path1/path2/subpath/object.json
s3['subpath', 'object.json'] = eg_json

# store pandas dataframe in s3 as .csv file in s3://some-bucket/path1/path2/data.csv
import pandas as pd  
s3['data.csv'] = pd.DataFrame({'C1': [1, 2], 'C2': [3, 4]})

# store arbitrary object in s3 at s3://some-bucket/path1/path2/object.pkl
s3['object.pkl'] = lambda x: x*x

# loading arbitrary python object from s3://some-bucket/path1/path2/object.pkl
# warning: do not load from untrusted sources!
loaded_square_func = s3['object.pkl']
assert loaded_square_func(3) = 3*3
```
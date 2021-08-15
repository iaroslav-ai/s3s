from typing import Union
from abc import abstractmethod
from s3fs import S3FileSystem
import cloudpickle as pc
import json
import pandas as pd


def _dump_pandas(df, f):
    assert isinstance(df, pd.DataFrame)
    return df.to_csv(f)


def _load_pandas(f):
    return pd.read_csv(f, index_col=0)



class S3:
    formats = {
        '.pkl': {
            'load': pc.load,
            'load_open_kwargs': {'mode': 'rb'},
            'dump': pc.dump,
            'dump_open_kwargs': {'mode': 'wb'},
        },
        '.json': {
            'load': json.load,
            'load_open_kwargs': {'mode': 'r'},
            'dump': json.dump,
            'dump_open_kwargs': {'mode': 'w'},
        },
        '.csv': {
            'load': _load_pandas,
            'load_open_kwargs': {'mode': 'r'},
            'dump': _dump_pandas,
            'dump_open_kwargs': {'mode': 'w'},
        }
    }

    def __init__(self, *path):
        self.path = path
        self.fs = S3FileSystem()

    def uri(self, *key):
        path = self.path + self._check(key)
        path = 's3://' + "/".join(str(v) for v in path)
        return path

    def _ls(self):
        return [
            path.split('/')[-1] for path in self.fs.ls(self.uri())
        ]

    def size(self, *key):
        return self.fs.size(self.uri(*key))

    def _subpath(self, *key):
        return S3(*(self.path + key))

    def _check(self, key):
        if not isinstance(key, tuple):
            key = (key,)
        result = tuple()
        for value in key:
            if isinstance(value, tuple):
                result += value
            else:
                result += (value,)
        return tuple(str(v) for v in result)

    def _get_io(self, key):
        key = self._check(key)
        for fmt, config in self.formats.items():
            if key[-1].endswith(fmt):
                return config
        return None

    def __iter__(self):
        return iter(self._ls())

    def __contains__(self, key):
        return self.fs.exists(self.uri(key))

    def __delitem__(self, key):
        self.fs.rm(self.uri(key), recursive=True)
    
    def __setitem__(self, key, value):
        io = self._get_io(key)
        if io is None:
            raise ValueError(f'The key {key} does not end with any known extension:{list(self.formats.keys())}')
        with self.fs.open(self.uri(key), **io['dump_open_kwargs']) as f:
            io['dump'](value, f)

    def __getitem__(self, key):
        io = self._get_io(key)
        if io is None:
            return self._subpath(*self._check(key))
        with self.fs.open(self.uri(key), **io['load_open_kwargs']) as f:
            return io['load'](f)


def _readme_workflow():
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

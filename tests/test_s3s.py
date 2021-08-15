from moto import mock_s3
from s3s import S3, _readme_workflow
import boto3 

egbucket = 'test-bucket'

def _setup():
    s3client = boto3.client('s3')
    s3client.create_bucket(Bucket=egbucket)
    s3client.create_bucket(Bucket='some-bucket')


@mock_s3
def test_readme_workflow():
    _setup()
    _readme_workflow()


@mock_s3
def test_json_serialization():
    _setup()

    json_example = {'data': 'value', 'array': [1,2,3]}
    s3 = S3(egbucket)
    s3['data.json'] = json_example
    loaded_json = s3['data.json']
    assert loaded_json == json_example


@mock_s3
def test_pickle_serialization():
    _setup()
    pkl_example = lambda x: x*x

    s3 = S3(egbucket)
    s3['data.pkl'] = pkl_example

    loaded_pkl = s3['data.pkl']

    for i in range(10):
        assert loaded_pkl(i) == pkl_example(i)


@mock_s3
def test_pandas_serialization():
    _setup()
    import pandas as pd
    pd_example = pd.DataFrame({
        'A': [1,2,3],
        'B': ['c','d','e'],
    })
    s3 = S3(egbucket)
    s3['data.csv'] = pd_example
    loaded_pd = s3['data.csv']
    assert loaded_pd.equals(pd_example)

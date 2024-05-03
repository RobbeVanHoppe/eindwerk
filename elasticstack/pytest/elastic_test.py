# Custom pytest plugin or test runner
import pytest
from elasticsearch import Elasticsearch

# Initialize Elasticsearch client with HTTPS
es = Elasticsearch([{'host': 'es01', 'port': 9200, 'scheme': 'https'}], basic_auth=('elastic', 'QcifyTest123.'), verify_certs=False)

@pytest.fixture(scope='module')
def elasticsearch_client():
    return es

# Example test
def test_example(elasticsearch_client):
    status = 1 == 1
    test_result = {
        'test_name': 'test_example',
        'status': 'pass'
    }
        # Index the test result into Elasticsearch
    es.index(index='pytest_results', body=test_result)


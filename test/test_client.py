# test/test_client.py
import sys
import os
import pytest
import responses
from client import get_hello, post_echo

# Ensure the parent directory containing client.py is in the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def base_url():
    return "http://example.com"


@responses.activate
def test_get_hello(base_url):
    responses.add(
        responses.GET,
        f"{base_url}/hello",
        json={'message': 'Hello, World!'},
        status=200
    )

    response_data = get_hello(base_url)
    assert response_data == {'message': 'Hello, World!'}


@responses.activate
def test_post_echo(base_url):
    input_data = {'key': 'value'}
    responses.add(
        responses.POST,
        f"{base_url}/echo",
        json=input_data,
        status=200
    )

    response_data = post_echo(base_url, input_data)
    assert response_data == input_data

    input_data = {'hello': 'world'}
    responses.add(
        responses.POST,
        f"{base_url}/echo",
        json=input_data,
        status=200
    )

    response_data = post_echo(base_url, input_data)
    assert response_data == input_data

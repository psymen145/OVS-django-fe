from django.test import TestCase
from django.test.utils import setup_test_environment
from django.test import Client

from .models import *

# Create your tests here.
setup_test_environment()
client = Client()

response = client.get('/')
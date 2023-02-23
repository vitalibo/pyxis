import json
import re
from typing import Any
from urllib.parse import urlparse

import boto3

from pyboost import function
from pyboost.config import Config, ConfigReader, ConfigValueResolver


class S3ConfigReader(ConfigReader):
    """
    A Config reader that reads from Amazon S3.
    """

    test = function(lambda x: x.startswith('s3://'))

    def __init__(self):
        self.__s3 = boto3.resource('s3')

    def read(self, path: str) -> str:
        url_parsed = urlparse(path)
        bucket_name, key = url_parsed.netloc, url_parsed.path[1:]
        obj = self.__s3.Object(bucket_name, key)
        return obj.get()['Body'].read().decode('utf-8')


class SecretsManagerResolver(ConfigValueResolver):
    """
    A configuration value resolver that resolves secrets from Secrets Manager.
    """

    test = function(lambda x: x.startswith('{{resolve:secretsmanager:') and x.endswith('}}'))

    def __init__(self):
        self.__secretsmanager = boto3.client('secretsmanager')

    def resolve(self, config: Config, key: str, value: str) -> Any:
        secret_id, secret_string, json_key, version_id = \
            re.findall(r'{{resolve:secretsmanager:(.*):(.*):(.*)(:.*)?}}', value)[0]
        if secret_string != 'SecretString':
            raise ValueError('SecretString is the only supported secret type')
        params = {'SecretId': secret_id}
        if version_id != '':
            params['VersionId'] = version_id
        response = self.__secretsmanager.get_secret_value(**params)
        return json.loads(response['SecretString'])[json_key]


class SSMResolver(ConfigValueResolver):
    """
    A configuration value resolver that resolves secrets from SSM.
    """

    test = function(lambda x: x.startswith('{{resolve:ssm:') and x.endswith('}}'))

    def __init__(self):
        self.__ssm = boto3.client('ssm')

    def resolve(self, config: Config, key: str, value: str) -> Any:
        parameter_name = re.findall(r'{{resolve:ssm:(.*?)}}', value)[0]
        response = self.__ssm.get_parameter(Name=parameter_name)
        return response['Parameter']['Value']


class SSMSecureResolver(ConfigValueResolver):
    """
    A configuration value resolver that resolves secrets from SSM.
    """

    test = function(lambda x: x.startswith('{{resolve:ssm-secure:') and x.endswith('}}'))

    def __init__(self):
        self.__ssm = boto3.client('ssm')

    def resolve(self, config: Config, key: str, value: str) -> Any:
        parameter_name = re.findall(r'{{resolve:ssm-secure:(.*?)}}', value)[0]
        response = self.__ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']


class CloudFormationOutputResolver(ConfigValueResolver):
    """
    A configuration value resolver that resolves CloudFormation outputs.
    """

    test = function(lambda x: x.startswith('{{resolve:cloudformation:') and x.endswith('}}'))

    def __init__(self):
        self.__cloudformation = boto3.client('cloudformation')

    def resolve(self, config: Config, key: str, value: str) -> Any:
        stack_name, output_key = re.findall(r'{{resolve:cloudformation:(.*?):(.*?)}}', value)[0]
        response = self.__cloudformation.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0]['Outputs']
        output = [output for output in outputs if output['OutputKey'] == output_key][0]
        return output['OutputValue']

import json
import re
import urllib.parse
from typing import Any

import boto3

from pyboost import function
from pyboost.config import Config, ConfigReader, ConfigValueResolver

__all__ = [
    'S3ConfigReader',
    'SecretsManagerResolver',
    'SSMResolver',
    'CloudFormationResolver'
]


class S3ConfigReader(ConfigReader):
    """
    A Config reader that reads from Amazon S3 bucket.
    The path must be in the following format:
        s3://bucket-name/key/to/config.json
    """

    test = function(lambda x: x.startswith('s3://'))

    def __init__(self):
        self.__s3 = boto3.resource('s3')

    def read(self, path: str) -> str:
        url_parsed = urllib.parse.urlparse(path)
        bucket_name, key = url_parsed.netloc, url_parsed.path[1:]
        obj = self.__s3.Object(bucket_name, key)
        return obj.get()['Body'].read().decode('utf-8')


class SecretsManagerResolver(ConfigValueResolver):
    """
    A Config value resolver that resolves secrets from AWS Secrets Manager.
    The value must be in the following format:
        {{resolve:secretsmanager:secret-id:secret-string:json-key:version-id}}

    :param secret-id: The secret ID. This can be either the friendly name of the secret or the full ARN of the secret.
    :param secret-string: The type of secret. Currently only SecretString is supported.
    :param json-key: The key of the secret to extract from the response.
    :param version-id: The unique identifier of the version of the secret that you want to retrieve.
    """

    regex = re.compile(
        r'{{resolve:secretsmanager:(arn:aws:secretsmanager:.*:.*:secret:.+?|.+?)(?::(.*?)(?::(.*?)(?::(.*?))?)?)?}}'
    )
    test = function(lambda x: x.startswith('{{resolve:secretsmanager:') and x.endswith('}}'))

    def __init__(self):
        self.__sm = boto3.client('secretsmanager')

    def resolve(self, config: Config, key: str, value: str) -> Any:
        match = re.match(self.regex, value)
        if match is None:
            raise ValueError(f'Value "{value}" is not a valid Secrets Manager format')
        secret_id, decryption, json_path, version_id = match.groups()

        if secret_id is None or secret_id == '':
            raise ValueError('Secret ID is required')
        if decryption is not None and decryption != 'SecretString':
            raise ValueError('SecretString is the only supported decryption type')

        params = {'SecretId': secret_id}
        if version_id is not None:
            params['VersionId'] = version_id
        response = json.loads(self.__sm.get_secret_value(**params)['SecretString'])

        if json_path is None:
            return response
        return Config(response).get(json_path)


class SSMResolver(ConfigValueResolver):
    """
    A Config value resolver that resolves value from Systems Manager Parameter Store.
    The value must be in the following format:
        {{resolve:ssm:parameter-name:version}}
        {{resolve:ssm-secure:parameter-name:version}}
    if ssm-secure is used, the parameter is secure string parameter otherwise it is plaintext.

    :param parameter-name: The name of the parameter.
    :param version: The version of the parameter.
    """

    test = function(
        lambda x: (x.startswith('{{resolve:ssm:') or x.startswith('{{resolve:ssm-secure:')) and x.endswith('}}')
    )
    regex = re.compile(r'{{resolve:ssm(-secure)?:([-a-zA-Z0-9_./]+)(:\d+)?}}')

    def __init__(self):
        self.__ssm = boto3.client('ssm')

    def resolve(self, config: Config, key: str, value: str) -> Any:
        match = re.match(self.regex, value)
        if match is None:
            raise ValueError(f'Value "{value}" is not a valid SSM format')
        with_decryption, parameter_name, version = match.groups()

        if version is not None and version != '':
            parameter_name = parameter_name + version
        params = {'Name': parameter_name}
        if with_decryption is not None:
            params['WithDecryption'] = True

        response = self.__ssm.get_parameter(**params)
        return response['Parameter']['Value']


class CloudFormationResolver(ConfigValueResolver):
    """
    A Config value resolver that resolves CloudFormation outputs.
    The value must be in the following format:
        {{resolve:cloudformation:stack-name:output-key}}

    :param stack-name: The name or the unique stack ID that is associated with the stack.
    :param output-key: The name of the output value as it appears in the Outputs section of the stack description.
    """

    regex = re.compile(r'{{resolve:cloudformation:([a-zA-Z0-9-]+):([a-zA-Z0-9]+)}}')

    test = function(lambda x: x.startswith('{{resolve:cloudformation:') and x.endswith('}}'))

    def __init__(self):
        self.__cfn = boto3.client('cloudformation')

    def resolve(self, config: Config, key: str, value: str) -> Any:
        match = re.match(self.regex, value)
        if match is None:
            raise ValueError(f'Value "{value}" is not a valid CloudFormation format')
        stack_name, output_key = match.groups()

        response = self.__cfn.describe_stacks(StackName=stack_name)

        if len(response['Stacks']) == 0:
            raise ValueError(f'CloudFormation stack "{stack_name}" does not exist')
        outputs = response['Stacks'][0]['Outputs']
        output = [output for output in outputs if output['OutputKey'] == output_key]
        if len(output) == 0:
            raise ValueError(f'CloudFormation stack "{stack_name}" does not have output "{output_key}"')
        return output[0]['OutputValue']

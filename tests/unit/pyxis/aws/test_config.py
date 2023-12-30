import io
from unittest import mock

import pytest

from pyxis.aws.config import CloudFormationResolver, S3ConfigReader, SecretsManagerResolver, SystemsManagerResolver
from pyxis.config import Config, ConfigReader, ConfigValueResolver


@mock.patch('boto3.resource')
def test_s3_config_reader(mock_boto3):
    mock_s3_object = mock.Mock()
    mock_s3_object.get.return_value = {'Body': io.BytesIO(b'foo')}
    mock_s3_resource = mock.Mock()
    mock_s3_resource.Object.return_value = mock_s3_object
    mock_boto3.return_value = mock_s3_resource
    reader = S3ConfigReader()

    actual = reader.read('s3://bucket/key')

    assert actual == 'foo'


def test_s3_config_reader_test():
    assert S3ConfigReader.test('s3://bucket/key') is True
    assert S3ConfigReader.test('foo://bucket/key') is False


@pytest.mark.parametrize('value, expected', [
    [
        '{{resolve:secretsmanager:MySecret}}',
        {'host': 'localhost', 'port': 5432, 'creds': {'username': 'foo', 'password': 'bar'}}
    ], [
        '{{resolve:secretsmanager:MySecret:SecretString:host}}',
        'localhost'
    ], [
        '{{resolve:secretsmanager:MySecret:SecretString:port}}',
        5432
    ], [
        '{{resolve:secretsmanager:MySecret:SecretString:creds}}',
        {'username': 'foo', 'password': 'bar'}
    ], [
        '{{resolve:secretsmanager:MySecret:SecretString:creds.username}}',
        'foo'
    ], [
        '{{resolve:secretsmanager:MySecret:SecretString:creds.password}}',
        'bar'
    ]
])
@mock.patch('boto3.client')
def test_secrets_manager_resolver_secret_id(mock_boto3, value, expected):
    mock_secretsmanager = mock.Mock()
    mock_boto3.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = \
        {'SecretString': '{"host": "localhost", "port": 5432, "creds": {"username": "foo", "password": "bar"}}'}
    resolver = SecretsManagerResolver()

    actual = resolver.resolve(Config({}), 'myKey', value)

    assert actual == expected
    mock_secretsmanager.get_secret_value.assert_called_once_with(SecretId='MySecret')


@pytest.mark.parametrize('value, expected', [
    [
        '{{resolve:secretsmanager:arn:aws:secretsmanager:us-east-1:12345678910:secret:SecretName-ABC123}}',
        {'host': 'localhost', 'port': 5432, 'creds': {'username': 'foo', 'password': 'bar'}}
    ], [
        ('{{resolve:secretsmanager:arn:aws:secretsmanager:us-east-1:12345678910:secret:SecretName-ABC123'
         ':SecretString:host}}'),
        'localhost'
    ], [
        ('{{resolve:secretsmanager:arn:aws:secretsmanager:us-east-1:12345678910:secret:SecretName-ABC123'
         ':SecretString:port}}'),
        5432
    ], [
        ('{{resolve:secretsmanager:arn:aws:secretsmanager:us-east-1:12345678910:secret:SecretName-ABC123'
         ':SecretString:creds}}'),
        {'username': 'foo', 'password': 'bar'}
    ], [
        ('{{resolve:secretsmanager:arn:aws:secretsmanager:us-east-1:12345678910:secret:SecretName-ABC123'
         ':SecretString:creds.username}}'),
        'foo'
    ], [
        ('{{resolve:secretsmanager:arn:aws:secretsmanager:us-east-1:12345678910:secret:SecretName-ABC123'
         ':SecretString:creds.password}}'),
        'bar'
    ]
])
@mock.patch('boto3.client')
def test_secrets_manager_resolver_secret_arn(mock_boto3, value, expected):
    mock_secretsmanager = mock.Mock()
    mock_boto3.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = \
        {'SecretString': '{"host": "localhost", "port": 5432, "creds": {"username": "foo", "password": "bar"}}'}
    resolver = SecretsManagerResolver()

    actual = resolver.resolve(Config({}), 'myKey', value)

    assert actual == expected
    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId='arn:aws:secretsmanager:us-east-1:12345678910:secret:SecretName-ABC123')


@pytest.mark.parametrize('value', [
    '{{resolve:secretmanager:MySecret}}',
    '{{resolve:secretsmanager:arn:aws:lambda:us-east-1:12345678910:function:SecretName-ABC123}}',
    '{{resolve:secretsmanager:::}}',
    '{{resolve:secretsmanager}}',
    '{{resolve:secretsmanager:}}'
])
@mock.patch('boto3.client')
def test_secrets_manager_resolver_bad_format(mock_boto3, value):
    mock_secretsmanager = mock.Mock()
    mock_boto3.return_value = mock_secretsmanager
    resolver = SecretsManagerResolver()

    with pytest.raises(ValueError):
        resolver.resolve(Config({}), 'myKey', value)


@mock.patch('boto3.client')
def test_secrets_manager_resolver_binary_decryption(mock_boto3):
    mock_secretsmanager = mock.Mock()
    mock_boto3.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {'SecretString': '{"host": "localhost"}'}
    resolver = SecretsManagerResolver()

    with pytest.raises(ValueError, match='SecretString is the only supported decryption type'):
        resolver.resolve(Config({}), 'myKey', '{{resolve:secretsmanager:MySecret:SecretBinary}}')


@mock.patch('boto3.client')
def test_secrets_manager_resolver_secret_id_with_version(mock_boto3):
    mock_secretsmanager = mock.Mock()
    mock_boto3.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {'SecretString': '{"host": "localhost"}'}
    resolver = SecretsManagerResolver()

    actual = resolver.resolve(Config({}), 'myKey', '{{resolve:secretsmanager:MySecret:SecretString:host:1234}}')

    assert actual == 'localhost'
    mock_secretsmanager.get_secret_value.assert_called_once_with(SecretId='MySecret', VersionId='1234')


@mock.patch('boto3.client')
def test_secrets_manager_resolver_secret_arn_with_version(mock_boto3):
    mock_secretsmanager = mock.Mock()
    mock_boto3.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {'SecretString': '{"host": "localhost"}'}
    resolver = SecretsManagerResolver()

    value = '{{resolve:secretsmanager:arn:aws:secretsmanager:us-east-1:12345678910:secret:' \
            'SecretName-ABC123:SecretString:host:1234}}'
    actual = resolver.resolve(Config({}), 'myKey', value)

    assert actual == 'localhost'
    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId='arn:aws:secretsmanager:us-east-1:12345678910:secret:SecretName-ABC123', VersionId='1234')


def test_secrets_manager_resolver_test():
    assert SecretsManagerResolver.test('{{resolve:secretsmanager:MySecret}}') is True
    assert SecretsManagerResolver.test(
        '{{resolve:secretsmanager:secretsmanager:arn:aws:secretsmanager:us-east-1:12345678910:secret:SecretName-ABC12}}'
    ) is True
    assert SecretsManagerResolver.test('{{resolve:ssm:MySecret:SecretString:host:1234}}') is False
    assert SecretsManagerResolver.test('resolve:secretsmanager:MySecret') is False


@mock.patch('boto3.client')
def test_ssm_resolve(mock_boto3):
    mock_ssm = mock.Mock()
    mock_boto3.return_value = mock_ssm
    mock_ssm.get_parameter.return_value = {'Parameter': {'Value': 'localhost'}}
    resolver = SystemsManagerResolver()

    actual = resolver.resolve(Config({}), 'myKey', '{{resolve:ssm:MyParameter}}')

    assert actual == 'localhost'
    mock_ssm.get_parameter.assert_called_once_with(Name='MyParameter')


@mock.patch('boto3.client')
def test_ssm_secure_resolve(mock_boto3):
    mock_ssm = mock.Mock()
    mock_boto3.return_value = mock_ssm
    mock_ssm.get_parameter.return_value = {'Parameter': {'Value': 'localhost'}}
    resolver = SystemsManagerResolver()

    actual = resolver.resolve(Config({}), 'myKey', '{{resolve:ssm-secure:MyParameter}}')

    assert actual == 'localhost'
    mock_ssm.get_parameter.assert_called_once_with(Name='MyParameter', WithDecryption=True)


@mock.patch('boto3.client')
def test_ssm_resolve_with_version(mock_boto3):
    mock_ssm = mock.Mock()
    mock_boto3.return_value = mock_ssm
    mock_ssm.get_parameter.return_value = {'Parameter': {'Value': 'localhost'}}
    resolver = SystemsManagerResolver()

    actual = resolver.resolve(Config({}), 'myKey', '{{resolve:ssm:MyParameter:123}}')

    assert actual == 'localhost'
    mock_ssm.get_parameter.assert_called_once_with(Name='MyParameter:123')


@pytest.mark.parametrize('value', [
    '{{resolve:foo:MySecret}}',
    'resolve:ssm-secure:MySecret',
    '{{resolve:ssm-secure:MySecret:version}}',
    '{{resolve:ssm-secure:MySecret:version:1:23}}',
])
@mock.patch('boto3.client')
def test_ssm_resolve_bad_format(mock_boto3, value):
    mock_ssm = mock.Mock()
    mock_boto3.return_value = mock_ssm
    mock_ssm.get_parameter.return_value = {'Parameter': {'Value': 'localhost'}}
    resolver = SystemsManagerResolver()

    with pytest.raises(ValueError):
        resolver.resolve(Config({}), 'myKey', value)


def test_ssm_resolver_test():
    assert SystemsManagerResolver.test('{{resolve:ssm:MyParam}}') is True
    assert SystemsManagerResolver.test('{{resolve:ssm-secure:MySecret}}') is True
    assert SystemsManagerResolver.test('{{resolve:ssm}}') is False


@mock.patch('boto3.client')
def test_cloudformation_resolve(mock_boto3):
    mock_cfn = mock.Mock()
    mock_boto3.return_value = mock_cfn
    mock_cfn.describe_stacks.return_value = {
        'Stacks': [{
            'Outputs': [
                {'OutputKey': 'MyOutput', 'OutputValue': 'MyOutput'}
            ]
        }]
    }
    resolver = CloudFormationResolver()

    actual = resolver.resolve(Config({}), 'myKey', '{{resolve:cloudformation:MyStack:MyOutput}}')

    assert actual == 'MyOutput'
    mock_cfn.describe_stacks.assert_called_once_with(StackName='MyStack')


@mock.patch('boto3.client')
def test_cloudformation_resolve_stack_not_found(mock_boto3):
    mock_cfn = mock.Mock()
    mock_boto3.return_value = mock_cfn
    mock_cfn.describe_stacks.return_value = {'Stacks': []}
    resolver = CloudFormationResolver()
    with pytest.raises(ValueError, match='CloudFormation stack "MyStack" does not exist'):
        resolver.resolve(Config({}), 'myKey', '{{resolve:cloudformation:MyStack:MyOutput}}')


@mock.patch('boto3.client')
def test_cloudformation_resolve_output_not_found(mock_boto3):
    mock_cfn = mock.Mock()
    mock_boto3.return_value = mock_cfn
    mock_cfn.describe_stacks.return_value = {
        'Stacks': [{
            'Outputs': [
                {'OutputKey': 'MyOutput1', 'OutputValue': 'MyOutput'}
            ]
        }]
    }
    resolver = CloudFormationResolver()
    with pytest.raises(ValueError, match='CloudFormation stack "MyStack" does not have output "MyOutput"'):
        resolver.resolve(Config({}), 'myKey', '{{resolve:cloudformation:MyStack:MyOutput}}')


@mock.patch('boto3.client')
def test_cloudformation_resolve_bad_format(mock_boto3):
    mock_cfn = mock.Mock()
    mock_boto3.return_value = mock_cfn
    resolver = CloudFormationResolver()
    with pytest.raises(ValueError, match='Value .* is not a valid CloudFormation format'):
        resolver.resolve(Config({}), 'myKey', '{{resolve:cloudformation:My_Stack:MyOutput}}')


def test_cloudformation_resolver_test():
    assert CloudFormationResolver.test('{{resolve:cloudformation:MyStack:MyOutput}}') is True
    assert CloudFormationResolver.test('{{resolve:cfm:MyStack:MyOutput}}') is False


@mock.patch('boto3.resource')
def test_config_reader_find_subclass_s3(mock_boto3):
    mock_s3 = mock.Mock()
    mock_boto3.return_value = mock_s3

    actual = ConfigReader.find_subclass('s3://bucket/key')

    assert actual.is_present()
    assert isinstance(actual.get(), S3ConfigReader)


@mock.patch('boto3.client')
def test_config_resolver_find_subclass_secretsmanager(mock_boto3):
    mock_sm = mock.Mock()
    mock_boto3.return_value = mock_sm

    actual = ConfigValueResolver.find_subclass('{{resolve:secretsmanager:MySecret}}')

    assert actual.is_present()
    assert isinstance(actual.get(), SecretsManagerResolver)


@mock.patch('boto3.client')
def test_config_resolver_find_subclass_ssm(mock_boto3):
    mock_ssm = mock.Mock()
    mock_boto3.return_value = mock_ssm

    actual = ConfigValueResolver.find_subclass('{{resolve:ssm:MyParameter}}')

    assert actual.is_present()
    assert isinstance(actual.get(), SystemsManagerResolver)


@mock.patch('boto3.client')
def test_config_resolver_find_subclass_ssm_secure(mock_boto3):
    mock_ssm = mock.Mock()
    mock_boto3.return_value = mock_ssm

    actual = ConfigValueResolver.find_subclass('{{resolve:ssm-secure:MyParameter}}')

    assert actual.is_present()
    assert isinstance(actual.get(), SystemsManagerResolver)


@mock.patch('boto3.client')
def test_config_resolver_find_subclass_cloudformation(mock_boto3):
    mock_cfn = mock.Mock()
    mock_boto3.return_value = mock_cfn

    actual = ConfigValueResolver.find_subclass('{{resolve:cloudformation:MyStack:MyOutput}}')

    assert actual.is_present()
    assert isinstance(actual.get(), CloudFormationResolver)

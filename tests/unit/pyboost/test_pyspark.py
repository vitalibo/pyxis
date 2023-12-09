from unittest import mock

import pytest
from pyspark import SparkConf, SparkContext
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as fn
from pyspark.sql.types import StructType

from pyboost.pyspark import Job, LocalTestSpark, Sink, Source, Spark


def test_submit():
    spark = Spark(mock.Mock(spec=SparkSession))
    mock_job = mock.Mock(spec=Job)

    spark.submit(mock_job)

    mock_job.transform.assert_called_with(spark)


def test_extract():
    spark = Spark(mock.Mock(spec=SparkSession))
    mock_source = mock.Mock(spec=Source)
    mock_dataframe = mock.Mock(spec=DataFrame)
    mock_source.extract.return_value = mock_dataframe

    actual = spark.extract(mock_source, 123, foo='bar')

    assert actual == mock_dataframe
    mock_source.extract.assert_called_with(spark, 123, foo='bar')


def test_load():
    spark = Spark(mock.Mock(spec=SparkSession))
    mock_sink = mock.Mock(spec=Sink)
    mock_dataframe = mock.Mock(spec=DataFrame)

    spark.load(mock_sink, mock_dataframe, 123, foo='bar')

    mock_sink.load.assert_called_with(spark, mock_dataframe, 123, foo='bar')


def test_create_dataframe():
    mock_spark_session = mock.Mock(spec=SparkSession)
    spark = Spark(mock_spark_session)
    mock_dataframe = mock.Mock(spec=DataFrame)
    mock_spark_session.createDataFrame.return_value = mock_dataframe

    actual = spark.create_dataframe(123, foo='bar')

    assert actual == mock_dataframe
    mock_spark_session.createDataFrame.assert_called_with(123, foo='bar')


def test_spark_session():
    mock_spark_session = mock.Mock(spec=SparkSession)
    spark = Spark(mock_spark_session)

    actual = spark.spark_session

    assert actual == mock_spark_session


def test_spark_context():
    mock_spark_session = mock.Mock(spec=SparkSession)
    mock_spark_context = mock.Mock(spec=SparkContext)
    mock_spark_session.sparkContext = mock_spark_context
    spark = Spark(mock_spark_session)

    actual = spark.spark_context

    assert actual == mock_spark_context


def test_spark_conf():
    mock_spark_session = mock.Mock(spec=SparkSession)
    mock_spark_context = mock.Mock(spec=SparkContext)
    mock_spark_conf = mock.Mock(spec=SparkConf)
    mock_spark_session.sparkContext = mock_spark_context
    mock_spark_context.getConf.return_value = mock_spark_conf
    spark = Spark(mock_spark_session)

    actual = spark.spark_conf

    assert actual == mock_spark_conf


def test_executor_instances():
    mock_spark_session = mock.Mock(spec=SparkSession)
    mock_spark_context = mock.Mock(spec=SparkContext)
    mock_spark_conf = mock.Mock(spec=SparkConf)
    mock_spark_session.sparkContext = mock_spark_context
    mock_spark_context.getConf.return_value = mock_spark_conf
    mock_spark_conf.get.return_value = 3
    spark = Spark(mock_spark_session)

    actual = spark.executor_instances

    assert actual == 3
    mock_spark_conf.get.assert_called_with('spark.executor.instances', '1')


def test_executor_cores():
    mock_spark_session = mock.Mock(spec=SparkSession)
    mock_spark_context = mock.Mock(spec=SparkContext)
    mock_spark_conf = mock.Mock(spec=SparkConf)
    mock_spark_session.sparkContext = mock_spark_context
    mock_spark_context.getConf.return_value = mock_spark_conf
    mock_spark_conf.get.return_value = 3
    spark = Spark(mock_spark_session)

    actual = spark.executor_cores

    assert actual == 3
    mock_spark_conf.get.assert_called_once_with('spark.executor.cores', '1')


def test_total_cores():
    mock_spark_session = mock.Mock(spec=SparkSession)
    mock_spark_context = mock.Mock(spec=SparkContext)
    mock_spark_conf = mock.Mock(spec=SparkConf)
    mock_spark_session.sparkContext = mock_spark_context
    mock_spark_context.getConf.return_value = mock_spark_conf
    mock_spark_conf.get.side_effect = [3, 2]
    spark = Spark(mock_spark_session)

    actual = spark.total_cores

    assert actual == 6
    assert mock_spark_conf.get.call_args_list == \
           [mock.call('spark.executor.instances', '1'), mock.call('spark.executor.cores', '1')]


def test_stop_spark_context():
    mock_spark_session = mock.Mock(spec=SparkSession)
    mock_spark_context = mock.Mock(spec=SparkContext)
    mock_spark_session.sparkContext = mock_spark_context
    spark = Spark(mock_spark_session)

    with spark as actual:
        assert spark == actual
        mock_spark_context.stop.assert_not_called()
    mock_spark_context.stop.assert_called_once()


def test_column_get_name(spark):  # pylint: disable=unused-argument
    column = fn.col('col1')

    actual = column.getName()

    assert isinstance(actual, str)
    assert actual == 'col1'


def test_dataframe_get_num_partitions(spark):
    df = spark.create_dataframe([{'col1': i} for i in range(100)]) \
        .repartition(18)

    assert df.getNumPartitions() == 18


def test_struct_type_from_json():
    schema = { # @formatter:off
        'fields': [
            {'name': 'col1', 'type': 'byte', 'nullable': False, 'metadata': {'foo': 'bar'}},
            {'name': 'col2', 'type': 'short'},
            {'name': 'col3', 'type': 'integer'},
            {'name': 'col4', 'type': 'long'},
            {'name': 'col5', 'type': 'float'},
            {'name': 'col6', 'type': 'double'},
            {'name': 'col7', 'type': 'string'},
            {'name': 'col8', 'type': 'boolean'},
            {'name': 'col9', 'type': 'timestamp'},
            {'name': 'col10', 'type': 'date'},
            {'name': 'col11', 'type': {'containsNull': False, 'elementType': 'string', 'type': 'array'}},
            {'name': 'col12', 'type': {'fields': [{'name': 'f1', 'type': 'string'}, {'name': 'f2', 'type': 'integer'}], 'type': 'struct'}},  # pylint: disable=line-too-long
            {'name': 'col13', 'type': {'type': 'map', 'keyType': 'string', 'valueType': 'integer', 'valueContainsNull': True}}  # pylint: disable=line-too-long
        ],
        'type': 'struct'
    }  # @formatter:on

    actual = StructType.from_json(schema)

    assert actual['col1'].dataType.typeName() == 'byte'
    assert not actual['col1'].nullable
    assert actual['col1'].metadata == {'foo': 'bar'}
    assert actual['col2'].dataType.typeName() == 'short'
    assert actual['col2'].nullable
    assert actual['col2'].metadata == {}
    assert actual['col3'].dataType.typeName() == 'integer'
    assert actual['col4'].dataType.typeName() == 'long'
    assert actual['col5'].dataType.typeName() == 'float'
    assert actual['col6'].dataType.typeName() == 'double'
    assert actual['col7'].dataType.typeName() == 'string'
    assert actual['col8'].dataType.typeName() == 'boolean'
    assert actual['col9'].dataType.typeName() == 'timestamp'
    assert actual['col10'].dataType.typeName() == 'date'
    assert actual['col11'].dataType.simpleString() == 'array<string>'
    assert actual['col12'].dataType.simpleString() == 'struct<f1:string,f2:int>'
    assert actual['col13'].dataType.simpleString() == 'map<string,int>'


@pytest.fixture(scope='module', name='spark')
def spark_fixture():
    session = SparkSession.builder \
        .appName('PyTest') \
        .config('spark.sql.session.timeZone', 'UTC') \
        .getOrCreate()

    with LocalTestSpark(session) as spark:
        yield spark


class SampleJob(Job):  # pylint: disable=missing-class-docstring

    def __init__(
            self,
            people_source: Source,
            department_source: Source,
            wage_sink: Sink,
            threshold: int
    ) -> None:
        self.people_source = people_source
        self.department_source = department_source
        self.wage_sink = wage_sink
        self.threshold = threshold

    def transform(self, spark: Spark) -> None:
        people = spark.extract(self.people_source)
        department = spark.extract(self.department_source)

        df = people \
            .filter(people.age > self.threshold) \
            .join(department, people.dept_id == department.id) \
            .groupBy(department.name, people.gender) \
            .agg(
                fn.avg(people.salary).alias('avg_salary'),
                fn.max(people.age).alias('max_age'))

        spark.load(self.wage_sink, df)


@pytest.mark.parametrize('case', [
    pytest.param(f'case{i}', id=f'Case #{i}: {item}') for i, item in enumerate([
        'age is less than 20',
        'age equals to 20',
        'age is more than 20',
        'no dept id for joining',
        'group by department',
        'group by gender',
        'average salary',
        'maximum age',
        'empty dataframes'
    ])
])
def test_sample_job(case, spark):
    job = SampleJob(
        spark.create_source_from_resource(
            __file__,
            f'data/pyspark/{case}/people_source.json',
            'data/pyspark/people_schema.json'),
        spark.create_source_from_resource(
            __file__,
            f'data/pyspark/{case}/department_source.json',
            'data/pyspark//department_schema.json'),
        spark.create_sink_from_resource(
            __file__,
            f'data/pyspark/{case}/wage_sink.json',
            'data/pyspark/wage_schema.json'),
        20)

    spark.submit(job)

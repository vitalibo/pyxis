from __future__ import annotations

import abc
import json
import os
from operator import itemgetter
from typing import Any, Dict, List

from pyspark import SparkConf, SparkContext
from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql.types import StructType

from pyboost import resources

__all__ = [
    'Job',
    'Source',
    'Sink',
    'Spark',
    'LocalTestSpark'
]


class Job(abc.ABC):
    """
    Abstract base class representing a Spark job.
    """

    @abc.abstractmethod
    def transform(self, spark: Spark) -> None:
        """
        Abstract method to define transformation logic.

        :param spark: :class:`pyboost.pyspark.Spark` instance.
        """


class Source(abc.ABC):
    """
    Abstract base class representing a data source from which data can be extracted.
    """

    @abc.abstractmethod
    def extract(self, spark: Spark, *args, **kwargs) -> DataFrame:
        """
        Abstract method to define extraction logic from source.

        :param spark: :class:`pyboost.pyspark.Spark` instance.
        :return: Extracted data as a :class:`pyspark.sql.DataFrame`.
        """


class Sink(abc.ABC):
    """
    Abstract base class representing a data sink to which transformed data can be loaded.
    """

    @abc.abstractmethod
    def load(self, spark: Spark, df: DataFrame, *args, **kwargs) -> None:
        """
        Abstract method to define loading logic to sink.

        :param spark: :class:`pyboost.pyspark.Spark` instance.
        :param df: :class:`pyspark.sql.DataFrame` to be loaded to sink.
        """


class Spark(abc.ABC):
    """
    Represents an Apache Spark instance.
    """

    def __init__(self, session: SparkSession):
        """
        Initializes a new instance of :class:`pyboost.pyspark.Spark`.

        :param session: :class:`pyspark.sql.SparkSession` instance.

        >>> from pyboost.pyspark import Spark
        >>> from pyspark.sql import SparkSession
        >>>
        >>> spark = Spark(SparkSession.builder.getOrCreate())
        """

        self.__session: SparkSession = session
        self.__sc: SparkContext = session.sparkContext

    def submit(self, job: Job) -> None:
        """
        Submits the given job to Apache Spark.

        :param job: :class:`pyboost.pyspark.Job` instance.
        """

        job.transform(self)

    def extract(self, source: Source, *args, **kwargs) -> DataFrame:
        """
        Extracts data from the given source.

        :param source: :class:`pyboost.pyspark.Source` instance.
        :return: Extracted data as a :class:`pyspark.sql.DataFrame`.
        """

        return source.extract(self, *args, **kwargs)

    def load(self, sink: Sink, df: DataFrame, *args, **kwargs) -> None:
        """
        Loads the given :class:`pyspark.sql.DataFrame` to the given sink.

        :param sink: :class:`pyboost.pyspark.Sink` instance.
        :param df: :class:`pyspark.sql.DataFrame` to be loaded to sink.
        """

        sink.load(self, df, *args, **kwargs)

    def create_dataframe(self, *args, **kwargs) -> DataFrame:
        """
        Creates a :class:`pyspark.sql.DataFrame` from the given data.

        :return: :class:`pyspark.sql.DataFrame` instance.
        """

        return self.__session.createDataFrame(*args, **kwargs)

    @property
    def spark_session(self) -> SparkSession:
        """
        :return: :class:`pyspark.sql.SparkSession` instance.
        """

        return self.__session

    @property
    def spark_context(self) -> SparkContext:
        """
        :return: :class:`pyspark.SparkContext` instance.
        """

        return self.__sc

    @property
    def spark_conf(self) -> SparkConf:
        """
        :return: :class:`pyspark.SparkConf` instance.
        """

        return self.__sc.getConf()

    @property
    def executor_instances(self) -> int:
        """
        :return: Number of executors.
        """

        return int(self.spark_conf.get('spark.executor.instances', '1'))

    @property
    def executor_cores(self) -> int:
        """
        :return: Number of cores per executor.
        """

        return int(self.spark_conf.get('spark.executor.cores', '1'))

    @property
    def total_cores(self) -> int:
        """
        :return: Total number of cores.
        """

        return self.executor_instances * self.executor_cores

    def __enter__(self) -> Spark:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.__sc.stop()


class LocalTestSpark(Spark):
    """
    The `LocalTestSpark` class is a subclass of :class:`pyboost.pyspark.Spark` and provides additional functionalities
    for creating sources, sinks, and dataframes from resources for testing purposes.
    """

    @classmethod
    def create_source_from_resource(  # pylint: disable=keyword-arg-before-vararg
            cls, root: str, path: str, schema_path: str = None, *args, **kwargs
    ) -> Source:
        """
        Creates a :class:`pyboost.pyspark.Source` instance from the given resource.

        :param root: The root directory containing the resources.
        :param path: The path to the resource within the root directory.
        :param schema_path: The path to the schema file for the resource.
        :param args: Additional arguments passed to the source.
        :param kwargs: Additional keyword arguments passed to the source.
        :return: A :class:`pyboost.pyspark.Source` object that can be used to extract data using the given resource.
        """

        class _TestSource(Source):
            def extract(self, spark: LocalTestSpark, *_args, **_kwargs) -> DataFrame:
                return spark.create_dataframe_from_resource(
                    root, path, schema_path, *_args, *args, **_kwargs, **kwargs)

        return _TestSource()

    @classmethod
    def create_sink_from_resource(  # pylint: disable=keyword-arg-before-vararg
            cls, root: str, path: str, schema_path: str = None, *args, **kwargs
    ) -> Sink:
        """
        Creates a :class:`pyboost.pyspark.Sink` instance from the given resource.

        :param root: The root directory containing the resources.
        :param path: The path to the resource within the root directory.
        :param schema_path: The path to the schema file for the resource.
        :param args: Additional arguments passed to the sink.
        :param kwargs: Additional keyword arguments passed to the sink.
        :return: A :class:`pyboost.pyspark.Sink` object that can be used to load data using the given resource.
        """

        class _TestSink(Sink):
            def load(self, spark: LocalTestSpark, df: DataFrame, *_args, **_kwargs) -> None:
                expected = spark.create_dataframe_from_resource(
                    root, path, schema_path, *_args, *args, **_kwargs, **kwargs)
                cls.assert_dataframe_equals(df, expected, *_args, *args, **_kwargs, **kwargs)

        return _TestSink()

    def create_dataframe_from_resource(  # pylint: disable=keyword-arg-before-vararg
            self, root: str, path: str, schema_path: str = None, *args, **kwargs
    ) -> DataFrame:
        """
        Creates a :class:`pyspark.sql.DataFrame` instance from the given resource.

        :param root: The root directory containing the resources.
        :param path: The path to the resource within the root directory.
        :param schema_path: The path to the schema file for the resource.
        :return: A :class:`pyspark.sql.DataFrame` instance.
        """

        if schema_path is None:
            schema_path = os.path.splitext(path)[0] + '.schema.json'

        rdd = self \
            .spark_context \
            .wholeTextFiles(resources.resource(root, path), 1) \
            .map(itemgetter(1))

        df = self \
            .spark_session.read \
            .option('multiLine', True) \
            .schema(StructType.from_json(resources.resource_as_json(root, schema_path))) \
            .json(rdd)

        # reformat json to make it more readable
        # WARNING: this code overrides the original json file
        if os.environ.get('PYBOOST_PYSPARK_REFORMAT_JSON', '').lower() not in ['true', '1']:
            return df

        formatted_json = json.dumps(json.loads(str(df.toJSON().collect()).replace("'", '')), indent=2)
        with open(resources.resource(root, path), 'w', encoding='utf-8') as f:
            f.write(formatted_json + '\n')

        return df

    @staticmethod
    def assert_dataframe_equals(
            actual: DataFrame, expected: DataFrame, *args, ignore_schema: bool = False, order_by: List[str] = None,
            **kwargs
    ) -> None:
        """
        Asserts that two :class:`pyspark.sql.DataFrame` instances are equal.

        :param actual: :class:`pyspark.sql.DataFrame` instance.
        :param expected: :class:`pyspark.sql.DataFrame` instance.
        :param ignore_schema: Flag indicating whether to ignore schema.
        :param order_by: List of columns to order by.
        """

        if order_by is not None:
            actual = actual.orderBy(*order_by)

        if not ignore_schema:
            assert actual.schema == expected.schema

        assert actual.collect() == expected.collect()


def __get_num_partitions(self: DataFrame) -> int:
    """
    :return: Number of partitions for the :class:`pyspark.sql.DataFrame`.
    """

    return self.rdd.getNumPartitions()


def __get_name(self: Column) -> str:
    """
    :return: Name of the column.
    """

    return self._jc.toString()  # noqa pylint: disable=protected-access


def __json_as_struct_type(schema: Dict[str, Any]) -> StructType:
    """
    Converts JSON schema object to :class:`pyspark.sql.types.StructType` instance.

    :param schema: JSON schema.
    :return: :class:`pyspark.sql.types.StructType` instance.
    """

    def fill_nullable_fields(node):
        for field in node['fields']:
            if 'metadata' not in field:
                field['metadata'] = {}
            if 'nullable' not in field:
                field['nullable'] = True
            if isinstance(field['type'], dict) and 'type' in field['type']:
                if field['type']['type'] == 'struct':
                    field['type'] = fill_nullable_fields(field['type'])
                if field['type']['type'] == 'array' and 'type' in field['type']['elementType'] and \
                        field['type']['elementType']['type'] == 'struct':
                    field['type']['elementType'] = fill_nullable_fields(field['type']['elementType'])

        return node

    return StructType.fromJson(fill_nullable_fields(schema))


DataFrame.getNumPartitions = __get_num_partitions
Column.getName = __get_name
StructType.from_json = __json_as_struct_type

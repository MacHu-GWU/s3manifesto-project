# -*- coding: utf-8 -*-

import random

from s3manifesto.constants import KeyEnum
from s3manifesto.manifest import ManifestFile
from s3manifesto.tests.mock_aws import BaseMockAwsTest


class TestManifestFile(BaseMockAwsTest):
    use_mock: bool = True

    def test(self):
        # [start1]
        # make dummy manifest file
        n_file = 1000
        uri = f"s3://{self.bucket}/manifest.json"
        uri_summary = f"s3://{self.bucket}/manifest-summary.json"

        # collect data file metadata
        data_file_list = list()
        total_size = 0
        total_record = 0
        for ith in range(1, 1 + n_file):
            uri = f"s3://{self.bucket}/data/{ith}.parquet"
            n_record = random.randint(1000, 10 * 1000)
            size = n_record * 1000
            total_size += size
            total_record += n_record
            data_file = dict(
                uri=uri,
                etag="...",
                size=size,
                n_record=n_record,
            )
            data_file_list.append(data_file)

        # test write and read
        # create manifest file object
        manifest_file = ManifestFile.new(
            uri=uri, # uri is the manifest-data.parquet file uri
            uri_summary=uri_summary, # uri_summary is the manifest-summary.json file uri
            data_file_list=data_file_list,
            # if True, then calculate the size and n_record using the data_file_list
            # otherwise, you need to set the size and n_record manually like this
            # ManifestFile.new(size=total_size, n_record=total_record)
            calculate=True,
        )
        assert manifest_file.size == total_size
        assert manifest_file.n_record == total_record
        assert isinstance(manifest_file.fingerprint, str)

        # write the manifest file to S3
        manifest_file.write(s3_client=self.s3_client)

        # [end1]
        # [start2]
        # read the manifest file from S3
        # you only need to provide the uri_summary, it will read the
        # manifest-summary.json file to locate the manifest-data.parquet
        manifest_file1 = ManifestFile.read(
            uri_summary=uri_summary,
            s3_client=self.s3_client,
        )
        assert manifest_file1.size == manifest_file.size
        assert manifest_file1.n_record == manifest_file.n_record
        assert len(manifest_file1.data_file_list) == len(manifest_file.data_file_list)
        assert manifest_file1.fingerprint == manifest_file.fingerprint
        # [end2]

        # [start3]
        # test group files into tasks by size
        target_size = 100_000_000  # 100MB
        data_file_group_list = manifest_file.group_files_into_tasks_by_size(
            target_size=target_size,
        )
        for data_file_group in data_file_group_list:
            assert (
                sum([data_file[KeyEnum.SIZE] for data_file in data_file_group])
                <= target_size * 2
            )

        # test group files into tasks by n_record
        target_n_record = 10_000_000  # 10M
        data_file_group_list = manifest_file.group_files_into_tasks_by_n_record(
            target_n_record=target_n_record,
        )
        for data_file_group in data_file_group_list:
            assert (
                sum([data_file[KeyEnum.N_RECORD] for data_file in data_file_group])
                <= target_n_record * 2
            )
        # [end3]


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(__file__, "s3manifesto.manifest", preview=False)

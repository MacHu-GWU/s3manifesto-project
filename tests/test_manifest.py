# -*- coding: utf-8 -*-

import random

from s3manifesto.manifest import ManifestFile
from s3manifesto.tests.mock_aws import BaseMockAwsTest


class TestManifestFile(BaseMockAwsTest):
    use_mock: bool = True

    def test(self):
        # make dummy manifest file
        n_file = 1000
        uri = f"s3://{self.bucket}/manifest.json"
        uri_summary = f"s3://{self.bucket}/manifest-summary.json"

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
                md5="...",
                size=size,
                n_record=n_record,
            )
            data_file_list.append(data_file)

        # test write and read
        manifest_file = ManifestFile.new(
            uri=uri,
            uri_summary=uri_summary,
            data_file_list=data_file_list,
            calculate=True,
        )
        assert manifest_file.size == total_size
        assert manifest_file.n_record == total_record

        manifest_file.write(s3_client=self.s3_client)

        manifest_file1 = ManifestFile.read(
            uri_summary=uri_summary, s3_client=self.s3_client
        )
        assert manifest_file1.size == manifest_file.size
        assert manifest_file1.n_record == manifest_file.n_record
        assert len(manifest_file1.data_file_list) == len(manifest_file.data_file_list)

        # test group files into tasks
        target_size = 100_000_000  # 100MB
        data_file_group_list = manifest_file.group_files_into_tasks(
            target_size=target_size,
        )
        for data_file_group in data_file_group_list:
            assert (
                sum([data_file["size"] for data_file in data_file_group])
                <= target_size * 2
            )


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(__file__, "s3manifesto.manifest", preview=False)

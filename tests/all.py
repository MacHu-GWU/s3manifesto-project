# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(__file__, "s3manifesto", is_folder=True, preview=False)

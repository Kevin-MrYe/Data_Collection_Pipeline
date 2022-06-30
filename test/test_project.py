import unittest
from HTMLTestRunner import HTMLTestRunner
from .test_scraper import TestScraper
from .test_transformer import TestTransformerMixin
from .test_loader import TestLoaderMixinn
from .test_asos_scraper import TestAsosScraper


def test_suite():
    #get the directory path to output report file

    #get all tests from Test class
    scraper_test = unittest.TestLoader().loadTestsFromTestCase(TestScraper)
    transformer_test = unittest.TestLoader().loadTestsFromTestCase(TestTransformerMixin)
    loader_test = unittest.TestLoader().loadTestsFromTestCase(TestLoaderMixinn)
    asos_scraper_test = unittest.TestLoader().loadTestsFromTestCase(TestAsosScraper)

    #create a test suite combine all test case
    test_suite = unittest.TestSuite([
        scraper_test, 
        transformer_test, 
        loader_test,
        asos_scraper_test,
        ])


    # configure HTMLTestRunner options
    runner = HTMLTestRunner(
        output='test/test_report',
        title='Data Collection Pipeline Test Report',
        open_in_browser=True,
        report_name='DataCollectionTest',
        tested_by='Kevin Ye',
        description='Unit test for ASOS web scraping project'

        )

    # #run the test suite using HTMLTestRunner
    # runner.run(test_suite)

    #run the test suite using TextTestRunner
    unittest.TextTestRunner(verbosity=2).run(test_suite)

if __name__ == '__main__':
    test_suite()
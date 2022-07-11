# Data_Collection_Pipeline
As shopping online becomes a household lifestyle, ecommerce affects people in all walks of life. Online sellers, storefront retailers and even consumers are all ecommerce data collectors. ASOS is a British online fashion and cosmetic retailer which sells over 850 brands as well as its own range of clothing and accessories. 

For any e-commerence business, it is important to analyse competitor's product information, including brand, prices, review scores, review numbers and product photos. This is a web scraper project which scrapes product information from [ASOS website](https://www.asos.com/). 

## Table of Contents
* [1.Project Overview](#1project-overview)
* [2.Classes Design](#2classes-design)
* [3.Methods Design](#3methods-design)
* [4.Unit Testing](#4unit-testing)
* [5.Containerising and Cloud Deployment](#5containerising-and-cloud-deployment)
* [6.Monitoring](#6monitoring)
* [7.CI/CD pipelines](#7cicd-pipelines)
* [8.Conclusion](#8conclusion)
* [9.Future Improvements](#9future-improvements)

## 1.Project Overview
The scraper will extract information from target website and then store tabular data on AWS RDS and store other format data on AWS S3. To make this project can be implemented on any OS system, this application was containerised using docker. The scraper will deployed on AWS EC2 instance, that means that will not consume resourse of local machine. Finally, the docker container metrics and EC2 metrics was monitored by Prometheus and visualized by Grafana.

<img src ="https://github.com/Kevin-MrYe/Data_Collection_Pipeline/blob/main/asos/img/overview.png" width = '700px'>


To make the project structure more clear, all scraper related modules are included in the asos folder and all the test module are included in the test folder. In addition to this, methods with different functionality are included in different class files.
The following is project structure:

```
.
├── .github
│   └── workflows
├── asos
│   ├── __init__.py
│   ├── __main__.py
│   ├── asos_scraper.py
│   ├── loader.py
│   ├── scraper.py
│   └── transformer.py
├── test
│   ├── __init__.py
│   ├── test_asos_scraper.py
│   ├── test_loader.py
│   ├── test_project.py
│   ├── test_scraper.py
│   └── test_transformer.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```

## 2.Classes Design
<img src ="https://github.com/Kevin-MrYe/Data_Collection_Pipeline/blob/main/asos/img/classes_design.png" width = '500px'>
Python does not have interfaces, but by using multiple inheritance, there is a similar mechanism in Python is referred to as a mixin. a mixin is a class that contains methods for use by other classes without having to be the parent class of those other classes. In this project, there are four classes as follows:

* __Scraper(Extractor)__

    The base class can be regarded as Extractor of ETL, which can extract information from website. In addition, it includes some interactive actions with broswer, e.g. accept cookie, searching and turn to next page.

* __TransformaerMixin__

    The Mixin can be regardes as Transformer of ETL, which can tranform the infortiom in dictionary into local files.

* __LoderMixin__

    The Mixin can be regarded as Loder of ETL, which can load the data to the cloud.

* __AsosScraper__

    The AsosScraper will inherited from the first three classes, so that it can be a multifunctional scraper.

Generally speaking, TransformaerMixin and LoderMixin will not be instantiated directly, they are only supplementary to the class to increase the functions of transformation and loading.


## 3.Methods Design
To achieve separation of concerns, each method is designed to perform a single function. The purpose of modularization is to make the program structure clearer and to make testing more accurate. The methods of all class are listed from the following figure:

<img src='https://github.com/Kevin-MrYe/Data_Collection_Pipeline/blob/main/asos/img/methods_design.png' width=700px>

The AsosScraper constructor has four arguments:

- homepage: Homepage url of ASOS
- save_locally: True means save data locally, otherwise on the cloud
- stream_process: True means stream process, otherwise batch process 
- target_nums: The number of items to be extracted

Either save_locally or stream_process has two options. So there are four modes of the scraper:
- Save data locally by batch
- Save data locally by stream
- Save data on the cloud by batch
- Save data on the cloud by stream

### Batch process Vs Stream process
Batch process means processing all the data in one time in the final stage. However, Stream process means processing data item by item. Although sometimes batch process has higher average process speed, stream process will be more stable. If batch process and there is an error before uploading data, all data will lose. 


## 4.Unit Testing
As the project grows, adding more functionality to the flexible code can cause problems. Testing is the process of verifying that software behaves as expected. A lower level of granularity is unit testing. Unit testing is used to test a single unit of code. This project uses Python's built-in Unittest module to implement unit testing.

For regular method, given an input, test the functionality of the method by comparing the expected and actual results.
For methods with external dependencies, mocking is recommended. The purpose of mocking is to isolate and focus on the code under test, not the behavior or state of the external dependencies.

An example of testing regular method:
```python
def test_search_for(self):
    self.scraper.driver.get("https://www.asos.com/")
    self.scraper.search_for("T-Shirt For Women")
    expected_url = "https://www.asos.com/search/?q=t-shirt+for+women"
    result_url = self.scraper.driver.current_url
    self.assertEqual(expected_url, result_url)
```
An example of testing with mocking
```python
@patch('asos.loader.pd.DataFrame.to_sql')
def test_upload_item_data_to_rds(self, mock_to_sql):
    item_dict = {'id':'AAA'}
    mock_to_sql.return_value = 1
    result = self.loader.upload_item_data_to_rds(item_dict)
    self.assertEqual(result,1)
```

For testing for each test class, TestSuite was used to create a test suite which combines all the test cases. In addition, using HTMLTestRunner-rv module to generate HTML report for the testcase. 
The [HTMLTestRunner](https://ravikiranb36.github.io/htmltestrunner-rv.github.io/api-documentation/#class-htmltestrunner) provides easy way to generate HTML Test Reports, which is easy to find errors and reduce the debug time.

## 5.Containerising and Cloud Deployment

## 6.Monitoring

## 7.CI/CD pipelines

## 8.Conclusion

## 9.Future Improvements





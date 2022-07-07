# Data_Collection_Pipeline
As shopping online becomes a household lifestyle, ecommerce affects people in all walks of life. Online sellers, storefront retailers and even consumers are all ecommerce data collectors. ASOS is a British online fashion and cosmetic retailer which sells over 850 brands as well as its own range of clothing and accessories. 

For any e-commerence business, it is important to analyse competitor's product information, including brand, prices, review scores, review numbers and product photos. This is a web scraper project which scrapes product information from [ASOS website](https://www.asos.com/). 

## Table of Contents
* [Project Overview](#project-overview)
* [Classes Design](#classes-design)
* [Methods Design](#methods-design)
* [Unit Testing](#unit-testing)
* [Containerising and Cloud Deployment](#containerising-and-cloud-deployment)
* [Monitoring](#monitoring)
* [CI/CD pipelines](#cicd-pipelines)
* [Conclusion](#conclusion)
* [Future Improvements](#future-improvements)

## Project Overview
<img src ="https://github.com/Kevin-MrYe/Data_Collection_Pipeline/blob/main/asos/img/overview.png" width = '700px'>
The scraper will extract information from target website and then store tabular data on AWS RDS and store other format data on AWS S3. To make this project can be implemented on any OS system, this application was containerised using docker. The scraper will deployed on AWS EC2 instance, that means that will not consume resourse of local machine. Finally, the docker container metrics and EC2 metrics was monitored by Prometheus and visualized by Grafana.


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

## Classes Design
<img src ="https://github.com/Kevin-MrYe/Data_Collection_Pipeline/blob/main/asos/img/classes_design.png" width = '700px'>
Python does not have interfaces, but by using multiple inheritance, there is a similar mechanism in Python is referred to as a mixin. a mixin is a class that contains methods for use by other classes without having to be the parent class of those other classes. In this project, there are four classes as follows:

* Scraper(Extractor)

The base class can be regarded as Extractor of ETL, which can extract information from website. In addition, it includes some interactive actions with broswer, e.g. accept cookie, searching and turn to next page.

* TransformaerMixin

The Mixin can be regardes as Transformer of ETL, which can tranform the infortiom in dictionary into local files.

* LoderMixin

The Mixin can be regarded as Loder of ETL, which can load the data to the cloud.

* AsosScraper

The AsosScraper will inherited from the first three classes, so that it can be a multifunctional scraper.

Generally speaking, TransformaerMixin and LoderMixin will not be instantiated directly, they are only supplementary to the class to increase the functions of transformation and loading.


## Methods Design
<img src ="https://github.com/Kevin-MrYe/Data_Collection_Pipeline/blob/main/asos/img/methods_design.png" width = '700px'>

## Unit Testing

## Containerising and Cloud Deployment

## Monitoring

## CI/CD pipelines

## Conclusion

## Future Improvements





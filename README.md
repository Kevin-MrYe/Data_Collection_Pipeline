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

Here is an example about uploading row data to AWS RDS:
```python
 def upload_item_data_to_rds(self, item_dict: dict) -> int:
    """Upload one item data to AWS RDS.

    Args:
        item_dict (dict): The dictionary to be uploaded to AWS RDS.

    Returns:
        int: Number of rows affected by to_sql
    """
    df = pd.DataFrame.from_dict(item_dict,orient='index').transpose()
    df.set_index('id',inplace=True)
    affected_rows = df.to_sql(self.rds_table_name, self.engine, if_exists='append')
    return affected_rows
```
An example about uploading item data to AWS S3:
```python
 def upload_item_data_to_s3(self, item_dict: dict) -> None:
    """Upload json and images for one itme to S3..

    Args:
        item_dict (dict): The dictionary to be uploaded to AWS S3.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id = self.s3_creds['aws_access_key_id'],
        aws_secret_access_key = self.s3_creds['aws_secret_access_key']
        )
    ##upload json data to S3
    json_object = json.dumps(item_dict, indent=4)
    json_path = os.path.join(self.s3_folder_anme,item_dict['id'],'data.json')
    s3_client.put_object(Body=json_object, Bucket=self.bucket_name, Key=json_path)

    ##Upload images data to S3
    image_links = item_dict['image_links']
    i=0
    for link in image_links:
        img_object = request.urlopen(link).read()
        img_name = str(i)+'.jpg'
        img_path = os.path.join(self.s3_folder_anme,item_dict['id'],'images',img_name)
        s3_client.put_object(Body=img_object, Bucket=self.bucket_name, Key=img_path)
        i +=1
```

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
An example of testing with mocking:
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
The following is the screenshot the test report:

<img src="https://github.com/Kevin-MrYe/Data_Collection_Pipeline/blob/main/asos/img/test_report.png" width=700px>

## 5.Containerising and Cloud Deployment
To give this application more scalability, containerize the application through Docker so that the application can run in any environment.

Docker images are essentially a set of steps that Docker engine will take to create the environment where will run the application. Those steps are declared in Dockerfile, which is a special type of file that Docker will look for to build an image. The following is the dockerfile that build our scraper image:
```
FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y gnupg\
    && apt-get install -y wget \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -\
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'\
    && apt-get -y update\
    && apt-get install -y google-chrome-stable

COPY . .

RUN pip install -r requirements.txt

CMD [ "python","-m","asos.asos_scraper" ]
```
At first the project is built from Python:3.8, but it will cost too much space because most of the modules will not be used. Therefore using Python:3.8-slim-buster to replace Python:3.8. Then install the google chrome to run the scraper.
The next step is copy everything in the Dockerfile directory inside the docker container. One more thing is to install dependencies so that scraper can work well.

After checking the dockerfile, run the following code to build and push the image to the docker hub:
```
docker build -t mrkevinye/asos_scraper:latest .
docker push mrkevinye/asos_scraper:latest
```

To run this docker image on EC2 instance, need to install docker on EC2 instance first.
```
sudo apt-get update
sudo apt-get install docker.io
```

Finally run the scraper container on EC2 instance:
```
docker run --name scraper --rm -v /home/kevin/.aws:/home/kevin/.aws mrkevinye/asos_scraper:latest
```
It's not wise to put credential in a docker image, because if making the image public, anyone who downloads the image will know about the credential. To avoid this, put credential in the folder of EC2 instance and share the folder containing credential between EC2 instance and Docker container via a volume bind mount. Volumes are the preferred mechanism for persisting data generated by and used by Docker containers.

## 6.Monitoring
Prometheus is an open source monitoring and alerting toolkit for gathering and processing data locally. This project will monitor EC2 instance metrics and Docker container metrics. Node exporter is a prometheus exporter for hardware and OS metrics exposed by \*NIX kernels, written in Go with pluggable metric collectors.

### Run Node exporter on AWS EC2
* Create a user for Prometheus Node Exporter
```
sudo useradd --no-create-home node_exporter
```
* install Node Exporter binaries
```
wget https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz
tar xzf node_exporter-1.0.1.linux-amd64.tar.gz
sudo cp node_exporter-1.0.1.linux-amd64/node_exporter /usr/local/bin/node_exporter
rm -rf node_exporter-1.0.1.linux-amd64.tar.gz node_exporter-1.0.1.linux-amd64
```
* Create a service and configure systemd
```
sudo systemctl daemon-reload
sudo systemctl enable node-exporter
sudo systemctl start node-exporter
sudo systemctl status node-exporter
```
### Configure prometheus yaml
```
global:
  scrape_interval: 10s
  external_labels:
    monitor: 'codelab-monitor'

scrape_configs:
  # The job name added as a label `job=<job_name>` to any timeseries scraped
  - job_name: 'prometheus'
    scrape_interval: '5s'
    static_configs:
      - targets: ['localhost:9090','18.134.5.215:9090']

  #node_exporter
  - job_name: 'node_exporter'
    
    static_configs:
      - targets: ['18.134.5.215:9100']

  #docker
  - job_name: 'docker'
    static_configs:
      - targets: ['172.17.0.1:9323']
```

Finally run the prometheus on EC2 instance:
```
sudo docker run --rm -d \
    --network=host \
    --name prometheus\
    -v /root/prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --web.enable-lifecycle 
```

The Grafana could get metrics from Node Exporter and Docker, then generate visualization:
<img src="https://github.com/Kevin-MrYe/Data_Collection_Pipeline/blob/main/asos/img/prometheus.png" width=700px>


## 7.CI/CD pipelines
### Github Actions
GitHub Actions allow us to automate various stages of software development. Whenever we make changes to the code, we always need to do a code test to make sure that the changes are correct without creating other bugs. Therefore, this project creates a workflow with two jobs:
1. When code is pushed or pull requests to the main branch, execute unit tests.
2. When code is pushed or pull requests to the main branch, build the docker image and push to the docker hub.

Details about the workflow can be seen [here](https://github.com/Kevin-MrYe/Data_Collection_Pipeline/blob/main/.github/workflows/scraper_ci.yml).

### Crontab
Running the scraper manually is not considered as true automation. This project triggers the scraper periodically by setting up Cron jobs. Since this project uses Linux in an EC2 instance, scheduled tasks can be managed through Crontab.

In order to be able to run the latest scraper every day, the cron job must be able to delete the old image, pull the latest image from the docker hub and run it. Here is the script that should run:

```
#/home/kevin/scraper.sh
EXPORT TZ=Europe/London

/usr/bin/docker rmi mrkevinye/asos_scraper:latest;
/usr/bin/docker run --name scraper --rm -v /home/kevin/.aws:/home/kevin/.aws mrkevinye/asos_scraper:latest
```

Then the Cron job is as follows:
```
CRON_TZ=Europe/London

0 10 * * * /home/kevin/scraper.sh

```
Usually, Cron jobs run using the local time defined in the system. Sometime we may prefer to run the Cron job in a different timezone without necessarily changing the server's time and date. By setting TZ = Europe/London, this project will run the scraper at 10:00 everyday at London timezone.

## 8.Conclusion

## 9.Future Improvements





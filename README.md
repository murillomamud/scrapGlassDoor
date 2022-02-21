# Scrap Data Engineer Salaries from Glassdoor

It's a test about scraping data from Glassdoor to check salaries and companies for Data Engineers in São Paulo/Brazil

## Recommendations:

To run this application, I recommend using virtualenv:

```bash

pip install virtualenv

virtualenv .venv

source .venv/bin/activate

pip install -r requirements.txt

```

# Sending data to S3 bucket

## Configurating AWS CLI:
[AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)


1. Create a bucket in AWS
2. Create a file named 'config' in root folder
3. File Content:
```bash
[AWS]
bucket = bucket_name
```

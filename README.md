# Finance Q&A Chatbot Development

## Objective

Develop a generative Q&A chatbot that provides factual answers to user queries by referring to a knowledge base created from the PDF files of financial reports from major public companies. The chatbot should use proper grounding techniques to minimize hallucinations and ensure the accuracy of the information.

## Problem Statement

- Develop a generative Q&A chatbot capable of answering questions related to financial reports of large public companies.
- The chatbot should utilize a knowledge base derived from the provided PDF files of financial reports.
- Ensure the chatbot is grounded in the knowledge base to minimize hallucinations and provide accurate responses.

## Data

Use PDF files containing financial reports from major public companies:

- [Alphabet 2023](https://abc.xyz/assets/investor/static/pdf/20230203_alphabet_10K.pdf)
- [Microsoft 2023](https://www.microsoft.com/investor/reports/ar23/)
- [NVIDIA 2023](https://s201.q4cdn.com/141608511/files/doc_financials/2023/ar/2023-Annual-Report-1.pdf)



Project Organization
------------
```bash
📦 
├─ `.DS_Store`
├─ `.dvc`
│  ├─ `.gitignore`
│  └─ `config`
├─ `.dvcignore`
├─ `.github`
│  └─ `workflows`
│     └─ `main.yml`
├─ `HELPER.md`
├─ `README.md`
├─ `backend`
│  ├─ `.gitignore`
│  ├─ `Dockerfile`
│  ├─ `configs`
│  │  └─ `app_config.yml`
│  ├─ `requirements.txt`
│  └─ `serve.py`
├─ `docker-compose.yaml`
├─ `frontend`
│  ├─ `.gitignore`
│  ├─ `Dockerfile`
│  ├─ `app.py`
│  ├─ `configs`
│  │  └─ `app_config.yml`
│  ├─ `data`
│  │  ├─ `.gitignore`
│  │  ├─ `docs.dvc`
│  │  └─ `vectordb`
│  │     ├─ `.gitignore`
│  │     ├─ `processed.dvc`
│  │     └─ `uploaded.dvc`
│  ├─ `images`
│  │  ├─ `chatbot.png`
│  │  └─ `user.png`
│  ├─ `requirements.txt`
│  └─ `src`
│     ├─ `__init__.py`
│     ├─ `chatbot.py`
│     ├─ `load_config.py`
│     ├─ `prepare_vectordb.py`
│     ├─ `ui_settings.py`
│     ├─ `upload_data_manually.py`
│     ├─ `upload_file.py`
│     └─ `utilities.py`
├─ `log.txt`
└─ `notebooks`
   ├─ `config`
   │  └─ `config.yml`
   └─ `langsmith_groq_openaiembed.ipynb`

```


## Demo Testing on HuggingFace Available

You can directly test the 
```bash
Chatbot here: [HuggingFace RAGFinanceChatbot](https://huggingface.co/spaces/sxandie/RAGFinanceChatbot)
```

## Run Locally
1. Clone the project:

    ```bash
    # Insert the repository clone command here
    ```

2. Create a `.env` file in the `frontend` folder with the following content:

    ```env
    HF_TOKEN=
    OPENAI_API_KEY=
    GROQ_API_KEY=
    LANGCHAIN_API_KEY=
    PINECONE_API_KEY=
    ```

### Set Up and Run the App with Docker

1. Open Docker Desktop application.

2. Build the Docker container:

    ```bash
    docker-compose build
    ```

3. Run the Docker container:

    ```bash
    docker-compose up
    ```

4. Open your preferred browser and navigate to [http://127.0.0.1:7860/](http://127.0.0.1:7860/) to start using the application.



## Deployment & Continous Integration & Continous Delivery & Continous Deployment

#### 1. Login to AWS console.
#### 2. Create IAM user for deployment

```bash
#with specific access
1. EC2 access : It is virtual machine
2. ECR: Elastic Container registry to save your docker image in aws

#Description: About the deployment

1. Build docker image of the source code
2. Push your docker image to ECR
3. Launch Your EC2 
4. Pull Your image from ECR in EC2
5. Lauch your docker image in EC2

#Policy:
1. AmazonEC2ContainerRegistryFullAccess
2. AmazonEC2FullAccess
```

#### 3. Create ECR repo to store/save docker image
```bash
- Save the URI: 136566696263.dkr.ecr.us-east-1.amazonaws.com/mlproject
```
#### 4. Create EC2 machine (Ubuntu)
#### 5. Open EC2 and Install docker in EC2 Machine:

```bash
#optinal
sudo apt-get update -y
sudo apt-get upgrade
#required
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
```
#### 6. Configure EC2 as self-hosted runner:

### 7. Setup github secrets:
```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION = us-east-1
AWS_ECR_LOGIN_URI = 
ECR_REPOSITORY_NAME = 
```

### Run Tests
These tests ensure that the code handles different scenarios correctly:
- Producing valid results for correct input ranges.
Run the tests:

```bash
pytest
```

## Data Version Control (DVC) Setup

The dataset has been added to the AWS S3 bucket.

## Managing Data Versions with DVC

To manage your data versions with DVC using the below commands:

1. **Add a remote storage**:
    ```bash
    dvc remote add -d myremote s3://mybucket
    ```
2. **Set your AWS credentials**:
    ```bash
    export AWS_ACCESS_KEY_ID='myid'
    export AWS_SECRET_ACCESS_KEY='mysecret'
    ```
3. **Push your data to the remote storage**:
    ```bash
    dvc push
    ```

## Presentation 
[Presentation Available]()

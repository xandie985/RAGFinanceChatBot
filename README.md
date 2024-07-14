# DVC

To manage your data versions with DVC, follow these steps:

1. **Add a remote storage**:

```bash
dvc remote add -d myremote s3://mybucket
export AWS_ACCESS_KEY_ID='myid'
export AWS_SECRET_ACCESS_KEY='mysecret'
dvc push
```

2. Pytest
pytest -v

3. Cloud API & CI/CD with AWS Cloud
# AWS-CICD-Deployment-with-Github-Actions

## 1. Login to AWS Console

## 2. Create an IAM User for Deployment with Specific Access

- **EC2 Access**: EC2 is a virtual machine.
- **ECR**: Elastic Container Registry to save your Docker image in AWS.

### Policies:
- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonEC2FullAccess`

## 3. Create an ECR Repository

Create an ECR repository to store/save your Docker image. Save the repository URI.

## 4. Create an EC2 Instance (Ubuntu)

## 5. Install Docker on EC2 Machine

Run the following commands to install Docker:

```bash
sudo apt-get update -y
sudo apt-get upgrade
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
```

6. Configure EC2 as a Self-Hosted Runner
Go to Settings > Actions > Runners > New self-hosted runner.
Choose the operating system and run the provided commands one by one.

7. Setup GitHub Secrets
Configure the following GitHub secrets:
```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_ECR_LOGIN_URI=
ECR_REPOSITORY_NAME=
```

8. Configure Git
Set your global Git user name:

bash
Copy code
git config --global user.name " "

9. CI/CD Setup with GitHub Actions
Follow the steps to set up GitHub Actions for CI/CD.


# Project Structure 

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
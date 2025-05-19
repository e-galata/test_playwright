# 🚀 Python Playwright Automation Project

**Tech Stack**:  
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pytest](https://img.shields.io/badge/Pytest-Test%20Framework-green)
![Playwright](https://img.shields.io/badge/Playwright-Browser%20Automation-orange)
![Pydantic](https://img.shields.io/badge/Pydantic-Data%20Validation-brightgreen)

## 📌 Project Overview
Automated test framework for web applications featuring:
- **Playwright** for reliable browser automation
- **Pytest** for scalable test structure
- **Pydantic** for request/response validation
- API mocking and UI testing integration

## 🛠 Setup
1. Clone repo
```bash
git clone https://github.com/e-galata/test_playwright.git
cd test_playwright
```

If you have Docker, execute the following command. Allure report will be available on localhost:8080  
Ctrl+c to terminate the Allure report server and stop the container
```bash
docker-compose up --build
```
OR

2. Create virtual env (Python 3.10+ required). Linux/Mac
```bash
python -m venv venv
source venv/bin/activate
```
OR (Windows)
```bash
venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Install Playwright browsers
```bash
playwright install
```

## 🚀 Run tests
```bash
pytest -s -v ./tests --headed --alluredir=./allureres
```

## Also install Allure CLI for reports:

macOS:
```bash
brew install allure
```
Linux:
```bash
sudo apt install allure
```
Windows:
```bash 
scoop install allure
```

View the reports with command:
```bash
allure serve ./allureres
```

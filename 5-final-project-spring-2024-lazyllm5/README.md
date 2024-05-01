[![log github events](https://github.com/software-students-spring2024/5-final-project-spring-2024-lazyllm5/actions/workflows/event-logger.yml/badge.svg)](https://github.com/software-students-spring2024/5-final-project-spring-2024-lazyllm5/actions/workflows/event-logger.yml)
[![webapp CI/CD](https://github.com/software-students-spring2024/5-final-project-spring-2024-lazyllm5/actions/workflows/webapp.yml/badge.svg)](https://github.com/software-students-spring2024/5-final-project-spring-2024-lazyllm5/actions/workflows/webapp.yml)
[![MongoDB CI/CD](https://github.com/software-students-spring2024/5-final-project-spring-2024-lazyllm5/actions/workflows/mongodb.yml/badge.svg)](https://github.com/software-students-spring2024/5-final-project-spring-2024-lazyllm5/actions/workflows/mongodb.yml)

# Spending Tracker Application

## Introduction
The Spending Tracker is a web-based application designed to help users record their personal transactions. It allows users to track their expenses, categorize transactions, and view detailed spending summaries by day, week, month, and year. This tool aims to provide users with clear insights into their consumption habits, promoting future spending management and planning.

## Docker
### Docker hub link
`https://hub.docker.com/u/wc2182`
### Pull from docker hub
```
docker pull wc2182/webapp:latest
docker pull wc2182/mongodb:latest
```
### Use the docker-compose file to run
```
docker compose up --build
```

## Testing with pytest

1. **Clone the Repository**
  ```
  git clone https://github.com/software-students-spring2024/5-final-project-spring-2024-lazyllm5
  ```
2. **Activate Pipenv**
Navigate to the directory where you cloned the repository and activate Pipenv:
  ```
  cd test
  pipenv shell
  ```
3. **Install Required Packages**
Install all the required packages using Pipenv:
  ```
  pipenv install
  ```
4. **Run Tests**
Execute the tests using pytest within the Pipenv environment:
  ```
pipenv run pytest
  ```
5. **Check Coverage**
To see the test coverage, run pytest with the coverage option:
  ```
pipenv run pytest --cov
  ```
After running this command, check the coverage report listed for `webapp/test/app.py` to see the actual coverage for the webapp.


## System Architecture
This application is composed of two primary subsystems:

### Subsystem 1: MongoDB Database
**Purpose:** Stores and manages all application data including user credentials, transaction records, and categorization details.
- **Features:**
  - CRUD operations for transactions and user profiles.
  - Efficient data retrieval for reporting and analysis.

### Subsystem 2: Flask Web Application
**Purpose:** Provides the user interface and handles all interactions with the MongoDB database. It processes user requests, performs business logic, and delivers data presentation.
- **Features:**
  - **User Authentication:** Secure registration and login mechanism, session management.
  - **Transaction Management:** Interfaces for adding, editing, and deleting transactions.
  - **Data Visualization:** Detailed spending summaries displayed by various time frames and categories.

## Functionality
- **Registration and Login:** Users can register an account and log in securely to manage their personal transactions.
- **Transaction Handling:** Users can enter transactions with details such as the date, amount, category, and a description of the spend.
- **Financial Summaries:** The application provides reports on spending:
  - **Detailed Summaries:** Users can select specific years or months to retrieve financial data, which is then displayed with percentages showing the distribution of spending across categories.
  - **Periodic Reports:** Automatically generated weekly, monthly, and yearly spending reports help users track their budget compliance over time.

## How It Works
1. **User Interaction:** Through the web interface, users interact with forms and views to enter and manage data.
2. **Data Processing:** The Flask backend processes this data, handling business logic and interacting with the MongoDB database.
3. **Data Storage and Retrieval:** Transactions and user data are stored in MongoDB, which provides fast and reliable access to the data.
4. **Reporting:** Aggregation queries are used to compile spending data into meaningful reports, which are rendered to the user through the Flask application.

## Contributors
1. [Angel Wu](https://github.com/angelWu2002)
2. [Weilin Cheng](https://github.com/M1stery232)
3. [Ruichen Wang](https://github.com/rcwang937)
4. [Haoyang Li](https://github.com/LeoLi727)
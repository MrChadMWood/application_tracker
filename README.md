# Job Application Tracker

## Overview

Preface: This project is not complete and should not be considered stable. It's still a work in progress.

The Job Application Tracker is a web-based application designed to help users track their job applications, postings, resumes, and responses. It offers a streamlined interface for users to input data, view their job search history, and organize related information. The application is built using modern web technologies like FastAPI and Pydantic for the backend, Streamlit for the user interface, PostgreSQL for data storage, and Docker for portability. The system is designed with a focus on dynamic CRUD (Create, Read, Update, Delete) operations, RESTful principles, and allow for easy data tracking by job seekers.

### Technologies Used

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- **PostgreSQL**: An open-source relational database management system (RDBMS).
- **Streamlit**: An open-source app framework for Machine Learning and Data Science projects.
- **Docker**: Containerization platform to simplify deployment and development.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [User Interface (UI)](#user-interface)
3. [Backend](#backend)
4. [Storage](#storage)
5. [Hot-Reloading](#hot-reloading)

## Quick Start Guide

### Prerequisites

- **Docker**: Make sure Docker is installed on your system.

### Setup and Run

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/MrChadMWood/application_tracker.git
   cd job-application-tracker
   ```

2. **Start the Application**:
   ```bash
   docker-compose up
   ```

3. **Access the UI**:
   - Open your browser and go to `http://localhost:8501` for the Streamlit interface.
   - The API will be accessible at `http://localhost:8000`.

### Application Structure

- **UI**: Built using Streamlit, running on port `8501`.
- **API**: FastAPI backend, running on port `8000`.
- **Database**: PostgreSQL, running on port `5432`.

## User Interface

### Overview

The UI is built with **Streamlit**, providing a simple and interactive interface for managing job application data. The UI focuses on presenting forms for CRUD operations and visualizing the stored data. 

[Applications Form Basic](docs/images/applications-create-flat-2024_08_29T10_39_27.png)

### Unique Form Concept

The UI employs a dynamic form concept, where fields are generated based on the selected entity (e.g., Resumes, Postings, Applications). The forms are designed to allow users to create new records and, if necessary, dynamically add related fields based on foreign key relationships.

[Applications Form Expanded](docs/images/applications-create-expanded-all-2024_08_29T10_39_27.png)

#### Form Structure

- **Form Rows**: Each form is divided into rows where each row corresponds to a database field. For foreign key fields, users have the option to create a new related record by selecting a "New" checkbox, which dynamically inserts the necessary fields into the form.

  
#### Future Goals

- **Stabilize Form Layout**: Currently, when a new related field is added, it appears at the end of the form. The goal is to make the form more intuitive by placing new fields directly after the triggering field.
- **Improve Form Row Stability**: Ensure that fields that are not changing position remain stable to avoid a jarring user experience.
- **Multiform Transactions**: The the API could utilize transactions to ensure that all required forms are filled in a single operation, minimizing the chances of incomplete data entry.

### Page Layout

- **Sidebar**: Used for selecting the entity (e.g., Resumes, Postings) the user wants to interact with.
- **Main Area**: Displays the selected entity’s data and the corresponding CRUD forms.
- **Expander**: Allows users to expand sections to view or hide data tables.

### UI Components

- **TableDisplay**: Handles the rendering of data in tabular form, fetching data from the API and displaying it using Streamlit’s dataframe component.
- **Form Management**: Each entity has a corresponding dynamic form class that handles the creation and submission of forms.

## Backend

### Overview

The backend is built using **FastAPI** and focuses on implementing RESTful CRUD operations. The backend is organized into modules for better maintainability and scalability.

### Code Structure

- **main.py**: The entry point for the API, where routes are defined dynamically based on models and schemas.
- **src/**: Contains the core application logic including models, schemas, CRUD operations, and database connections.
  - **crud.py**: Implements the base CRUD functionality that is reused across different models.
  - **models.py**: Contains SQLAlchemy models that define the database schema.
  - **schemas/**: Defines Pydantic models for data validation and serialization.
  - **database.py**: Handles database connections and session management.
  - **dependancies.py**: Defines dependency injection for database sessions.
  - **settings.py**: Manages configuration settings including environment variables and database connection details.

### CRUD and REST

The backend is designed to adhere to RESTful principles with a strong focus on CRUD operations. Each model has its own set of CRUD endpoints, which are dynamically generated using a utility function in `main.py`.

#### Dynamic CRUD Route Generation

- **generate_crud_routes()**: This function dynamically generates and registers CRUD endpoints (POST, GET, PUT, DELETE) for each model. This allows developers to quickly add new models without manually defining each endpoint.

#### Database Session Management

- **get_db()**: Synchronously manages the lifecycle of database sessions, ensuring that sessions are properly opened and closed.
- **get_async_db()**: Manages asynchronous database sessions.

## Storage

### Overview

The storage layer is powered by **PostgreSQL** and managed via SQLAlchemy ORM in the backend. The database schema is designed to store job application data, including resumes, job postings, applications, and responses.

### Database Schema

- **resume**:
  - **id**: Primary key.
  - **data**: JSONB column storing resume data.
  
- **posting**:
  - **id**: Primary key.
  - **platform**: Text field for the job platform (e.g., LinkedIn).
  - **company**: Company name.
  - **title**: Job title.
  - **salary**: Optional salary field.
  - **description**: Job description.
  - **responsibilities**: Key responsibilities for the job.
  - **qualifications**: Required qualifications.
  - **remote**: Boolean indicating if the job is remote.

- **application**:
  - **id**: Primary key.
  - **posting_id**: Foreign key to `posting`.
  - **resume_id**: Foreign key to `resume`.
  - **date_submitted**: Date when the application was submitted.

- **response_type**:
  - **id**: Primary key.
  - **name**: Name of the response type (e.g., email, call).

- **response**:
  - **id**: Primary key.
  - **application_id**: Foreign key to `application`.
  - **response_type_id**: Foreign key to `response_type`.
  - **date_received**: Date when the response was received.
  - **data**: Optional field to store additional response information.

## Hot-Reloading

### Overview

Hot-reloading is configured for both the FastAPI backend and the Streamlit UI, facilitating a streamlined development experience. docker-compose is utilized to mount the project into its container rather than copy, which wouldn't allow for hot reloading.

### API Hot-Reloading

- **Uvicorn**: The API server runs using Uvicorn with the `--reload` flag enabled using the `hot_reload` variable imported from its settings file. This will soon take an enviroment variable.
  ```python
  uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=hot_reload)
  ```
- **Environment Configuration**: The `hot_reload` setting in `settings.py` enables or disables hot-reloading.

### UI Hot-Reloading

- **Streamlit Configuration**: The `config.toml` file in the `.streamlit` directory sets up hot-reloading for the Streamlit app, using the `fileWatcherType` set to "poll" to handle file changes even in Docker.
  ```toml
  [server]
  runOnSave = true
  fileWatcherType = "poll"
  ```
  

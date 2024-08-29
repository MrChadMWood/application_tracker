# Job Application Tracker

## Overview

**Note**: This project is still under development and should not be considered stable.

The Job Application Tracker started as a simple tool to track job applications, facilitating easy data entry with minimal constraints. The goal was to create a system that allows users to focus on their job hunt without being bogged down by the tracking process.

Initially, the project aimed to include domain-specific features like resume parsing, full-text search on applications, and trend analysis based on keywords. While these remain objectives, the project's scope has expanded. The current focus is on making the UI and API as generic and reusable as possible, inspired by React's component philosophy. This is to provide a streamlined development experience for simple applications meant to facillitate data entry, such as a job application tracker (or, an ice-cream machine repair tracker [looking at you, McDonalds...]).

The UI implements a dynamic form system that is agnostic to the specific form fields or their number. Similarly, the API generates CRUD endpoints with minimal configuration.

### Technologies Used

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- **PostgreSQL**: An open-source relational database management system (RDBMS).
- **Streamlit**: An open-source app framework for Data Science projects.
- **Docker**: Containerization platform to simplify deployment and development.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [User Interface (UI)](#user-interface)
3. [Backend](#backend)
4. [Storage](#storage)
5. [Hot-Reloading](#hot-reloading)

## Quick Start Guide

### Prerequisites

- **Docker**: Ensure Docker is installed on your system.

### Setup and Run

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/MrChadMWood/application_tracker.git
   cd application_tracker
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

The UI is built with **Streamlit** and provides a simple, interactive interface for managing job application data. It includes forms for CRUD operations and data visualization.

![Applications Form Basic](docs/images/applications-create-flat-2024_08_29T10_39_27.png?raw=true)

### Dynamic Form Concept

The UI employs a dynamic form system where fields are generated based on the selected entity (e.g., Resumes, Postings, Applications). This allows users to create new records and, if necessary, dynamically add related fields from parent tables with foreign keys.

![Applications Form Expanded](docs/images/applications-create-expanded-all-2024_08_29T10_39_27.png?raw=true)

#### Future Goals

- **Multiform Transactions**: Implementing API-level transactions to ensure all required forms are completed in a single operation, reducing the chances of incomplete data en
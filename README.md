# API-Integration
A FastAPI-based application that fetches and combines weather, cryptocurrency, and dog breed data. The combined data is stored in a SQLite database and can be retrieved through various endpoints. Ideal for integrating multiple data sources into a single cohesive API

## Prerequisites

- Python 3.8 or higher
- SQLite

## Setup

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-name>
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Initialize the database:
    ```sh
    python init_db.py
    ```

5. Run the FastAPI application:
    ```sh
    uvicorn main:app --reload
    ```

## API Endpoints

### Fetch Combined Data

- **URL:** `/combined-data`
- **Method:** `POST`
- **Parameters:**
  - `city` (str): Name of the city
  - `crypto_id` (str): ID of the cryptocurrency
  - `breed` (str): Name of the dog breed

### Retrieve Historical Data

- **URL:** `/combined-data/history`
- **Method:** `GET`
- **Parameters (optional):**
  - `start_date` (str): Start date in ISO format (e.g., `2023-01-01T00:00:00`)
  - `end_date` (str): End date in ISO format (e.g., `2023-12-31T23:59:59`)

### Fetch Weather Data

- **URL:** `/weather`
- **Method:** `GET`
- **Parameters:**
  - `city` (str): Name of the city

### Fetch Cryptocurrency Data

- **URL:** `/crypto`
- **Method:** `GET`
- **Parameters:**
  - `crypto_id` (str): ID of the cryptocurrency

### Fetch Dog Data

- **URL:** `/dogs`
- **Method:** `GET`
- **Parameters:**
  - `breed` (str): Name of the dog breed

## Running Tests

To run the tests, use `pytest`:
```sh
pytest


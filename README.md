# Load Testing Serverless Functions on Kubernetes

## Overview

This project is designed to perform load testing on serverless functions running on a Kubernetes cluster. The script reads configuration data from a CSV file and sends HTTP requests to specified endpoints at rates calculated from the CSV data. The requests are sent concurrently, simulating real-world usage patterns. The response times and status of these requests are recorded in a CSV file for analysis.

## Features

- Reads input data from a CSV file.
- Supports multiple serverless functions, each with unique parameters.
- Calculates request rates per second based on invocations per minute.
- Sends HTTP POST requests concurrently using a thread pool.
- Retries failed requests up to three times.
- Logs response times and statuses to CSV files.

## Prerequisites

- Python 3.6+
- `requests` library
- `concurrent.futures` module
- `csv` module
- A Kubernetes cluster with deployed serverless functions

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/load-testing-k8s.git
    cd load-testing-k8s
    ```

2. Install the required Python packages:

    ```bash
    pip install requests
    ```

## Usage

1. Prepare your CSV file (`data.csv`) with the following columns:

    - `endpoint`: The URL of the serverless function.
    - `function`: The name of the function to be tested.
    - `data`: The input data for the function.
    - `1`, `2`, ...: Columns representing invocations per minute for each minute.

    Example CSV format:

    ```csv
    endpoint,function,data,1,2
    http://example.com/func,chameleon,num_of_rows:10|num_of_cols:20|uuid:1234,120,180
    http://example.com/func2,matmul,number:5|uuid:5678,90,150
    ```

2. Update the `file_path` variable in the `main` function to point to your CSV file:

    ```python
    file_path = '/path/to/your/data.csv'
    ```

3. Run the script:

    ```bash
    python load_test.py
    ```

## Explanation of the Code

### `read_csv(file_path)`

Reads the CSV file and returns the data as a list of dictionaries.

### `calculate_request_rate(row)`

Calculates the request rate per second for each minute based on the CSV data.

### `send_requests(endpoint, fn_name, data_in, request_rate, minutes)`

Sends requests to the specified endpoint at the calculated rate using a thread pool.

### `send_request(endpoint, fn_name, data_in, response_list)`

Sends a single HTTP POST request to the specified endpoint with the given data. Retries up to three times on failure and logs the response time.

### `main()`

- Reads data from the CSV file.
- Starts a separate thread for each row in the CSV file to send requests concurrently.
- Waits for all threads to finish.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.


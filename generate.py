import csv
import threading
import time
import requests
import json
import concurrent.futures


# Function to read CSV file and extract data
def read_csv(file_path):
    data = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

# Function to calculate request rate per second for each minute
def calculate_request_rate(row):
    minutes = 0
    request_rate = []
    for i in range(1, 3):  # Assuming headers represent minutes
        minutes += 1
        request_rate.append(int(int(row[str(i)]) / 60))  # Convert invocations per minute to invocations per second
    return request_rate, minutes


def send_requests(endpoint, fn_name, data_in, request_rate, minutes):
    response_list = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for minute in range(minutes):
            start_time = time.time()  # Record the start time for each minute
            for second in range(60):
                for _ in range(request_rate[minute]):
                    future = executor.submit(send_request, endpoint, fn_name, data_in, response_list)
                    futures.append(future)
            
                # Calculate the time taken for spawning threads
                thread_creation_time = time.time() - start_time
                
                # Adjust sleep time dynamically to ensure each second takes approximately 1 second
                sleep_time = max(0, 1 - thread_creation_time)
                time.sleep(1)
                
            
        # Wait for all minutes to finish before moving on
        for future in futures:
            future.result()


# Function to send a single request and handle its response
def send_request(endpoint, fn_name, data_in, response_list):
    start_time = time.time()
    response = requests.post(endpoint, data=f'{{"number": {data_in[0]}, "uuid": "{data_in[1]}"}}')
    response_time = time.time() - start_time
    response_list.append(response_time)
    
    # Append response time to CSV file
    with open(f'{fn_name}.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([response.ok,fn_name,response_time])

# Main function
def main():
    file_path = '/home/hpckurd/k8s-cluster/workload_generation/data.csv'  # Replace with your CSV file path

    data = read_csv(file_path)

    threads = []
    for row in data:
        data = row['number'], row['uuid']
        request_rate, minutes = calculate_request_rate(row)
        thread = threading.Thread(target=send_requests, args=(row['endpoint'], row['function'], data, request_rate, minutes))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
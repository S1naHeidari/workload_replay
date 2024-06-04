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
    # this must be determined by another script
    avg_latency = 7
    max_threads = max(request_rate) * avg_latency
    response_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for minute in range(minutes):
            for second in range(60):
                # Calculate the number of threads to spawn for this second
                threads_to_spawn = min(max_threads - executor._work_queue.qsize(), request_rate[minute])
                #print(executor._work_queue.qsize())
                for _ in range(threads_to_spawn):
                    future = executor.submit(send_request, endpoint, fn_name, data_in, response_list)
                    futures.append(future)
                time.sleep(1)  # Sleep for 1 second between each second

        # Wait for all minutes to finish before moving on
        for future in futures:
            future.result()

            
def send_request(endpoint, fn_name, data_in, response_list):
    start_time = time.time()
    data_dict = {}
    inputs = data_in.split('|')

    for input in inputs:
        split_input = input.split(':')
        data_dict[split_input[0]] = split_input[1]

    headers = {
        'Content-Type': 'application/json'
    }
    if fn_name == 'chameleon':
        json_dict = {
        "num_of_rows": int(f"{data_dict['num_of_rows']}"),
        "num_of_cols": int(f"{data_dict['num_of_cols']}"),
        "uuid": f"{data_dict['uuid']}"
        }
    elif fn_name == 'matmul':
        json_dict = {
        "number": int(f"{data_dict['number']}"),
        "uuid": f"{data_dict['uuid']}"
        }
    elif fn_name == 'float':
        json_dict = {
        "number": int(f"{data_dict['number']}"),
        "uuid": f"{data_dict['uuid']}"
        }
    elif fn_name == 'pyaes':
        json_dict = {
        "length_of_message": int(f"{data_dict['length_of_message']}"),
        "num_of_iterations": int(f"{data_dict['num_of_iterations']}"),
        "uuid": f"{data_dict['uuid']}"
        }
    elif fn_name == 'linpack':
        json_dict = {
        "number": int(f"{data_dict['number']}"),
        "uuid": f"{data_dict['uuid']}"
        }
    elif fn_name == 'gzip':
        json_dict = {
        "file_size": int(f"{data_dict['file_size']}"),
        "uuid": f"{data_dict['uuid']}"
        }
    elif fn_name == 'dd':
        json_dict = {
        "bs": int(f"{data_dict['bs']}"),
        "count": int(f"{data_dict['count']}"),
        "uuid": f"{data_dict['uuid']}"
        }
    elif fn_name == 's3':
        json_dict = {
            "input_bucket": f"{data_dict['input_bucket']}",
            "object_key": f"{data_dict['object_key']}",
            "output_bucket": f"{data_dict['output_bucket']}",
            "key_id": f"{data_dict['key_id']}",
            "access_key": f"{data_dict['access_key']}",
            "uuid": f"{data_dict['uuid']}"
        }
    elif fn_name == 'json':
        json_dict = {
            "link": f"http://{data_dict['link']}",
            "uuid": f"{data_dict['uuid']}"
        }
    elif fn_name == 'image-process':
        json_dict = {
            "input_bucket": f"{data_dict['input_bucket']}",
            "object_key": f"{data_dict['object_key']}",
            "output_bucket": f"{data_dict['output_bucket']}",
            "key_id": f"{data_dict['key_id']}",
            "access_key": f"{data_dict['access_key']}",
            "uuid": f"{data_dict['uuid']}"
        }

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.post(endpoint, json=json_dict, headers=headers)
            print(response.text)
            response_time = time.time() - start_time
            response_list.append(response_time)

            # Append response time to CSV file
            with open(f'{fn_name}.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([response.ok, fn_name, response_time])
            break  # Break the loop if request is successful
        except requests.exceptions.RequestException as e:
            print(f"Request failed on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(1)  # Wait for 1 second before retrying
            else:
                print("Max retries reached. Giving up.")

# Main function
def main():
    file_path = '/home/hpckurd/k8s-cluster/workload_generation/data.csv'  # Replace with your CSV file path

    data = read_csv(file_path)

    threads = []
    for row in data:
        data = row['data']
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

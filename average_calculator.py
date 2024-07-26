from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
third_party_api_url = "http://20.244.56.144/test/primes"
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzIxOTczODUzLCJpYXQiOjE3MjE5NzM1NTMsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6ImI3YmVjZjYyLTg3MTktNDJhOC05MmM1LTJmYmUzZmEzNTY5MiIsInN1YiI6ImdhbmppdmFyc2gxOEBnbWFpbC5jb20ifSwiY29tcGFueU5hbWUiOiJWaWduYW4iLCJjbGllbnRJRCI6ImI3YmVjZjYyLTg3MTktNDJhOC05MmM1LTJmYmUzZmEzNTY5MiIsImNsaWVudFNlY3JldCI6IkVJY3lDeVRhSGxMTW9lWFUiLCJvd25lck5hbWUiOiJHYW5qaVZhcnNoYSIsIm93bmVyRW1haWwiOiJnYW5qaXZhcnNoMThAZ21haWwuY29tIiwicm9sbE5vIjoiMjFVUDFBMDVGMSJ9.5eEdPAKt91GtL5WxFYqRUUNfvMZ267PupDcfumBDeHU"  # Replace with your actual access token

# In-memory store
window_prev_state = []
window_curr_state = []

# Utility functions
def fetch_numbers(number_id):
    headers = {
        "Authorization": f"Bearer {access_token} 1721973853"
    }
    try:
        url = f"{third_party_api_url}/{number_id}"
        response = requests.get(url, headers=headers, timeout=0.5)
        response.raise_for_status()
        return response.json()["numbers"]
    except (requests.exceptions.RequestException, KeyError):
        return []

def calculate_average(numbers):
    if not numbers:
        return 0
    return round(sum(numbers) / len(numbers), 2)

@app.route("/numbers/<number_id>", methods=["GET"])
def get_numbers(number_id):
    global window_prev_state, window_curr_state

    start_time = time.time()
    
    # Fetch numbers from third-party API
    new_numbers = fetch_numbers(number_id)
    
    if new_numbers:
        # Update the window states
        window_prev_state = window_curr_state.copy()
        
        # Add new numbers to current state ensuring uniqueness
        window_curr_state = list(set(window_curr_state + new_numbers))
        
        # Ensure the window size is maintained
        if len(window_curr_state) > WINDOW_SIZE:
            window_curr_state = window_curr_state[-WINDOW_SIZE:]
    
    avg = calculate_average(window_curr_state)
    
    # Print the average
    print(f"Average of numbers: {avg}")
    
    response = {
        "windowPrevState": window_prev_state,
        "windowCurrState": window_curr_state,
        "numbers": new_numbers,
        "avg": avg
    }
    
    # Check if the processing time is within the limit
    processing_time = (time.time() - start_time) * 1000
    if (processing_time > 500):
        response["warning"] = "Response time exceeded 500 milliseconds"
    
    return jsonify(response)

if __name__ == "_main_":
    app.run(debug=True)

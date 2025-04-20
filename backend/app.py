from flask import Flask, jsonify
from fetcher import retrieve_vacancies
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DATA_FILE = 'storage.csv'

def load_existing_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=['job_title', 'salary', 'vacancies', 'location', 'employment_type', 'posting_date'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def merge_and_deduplicate(new_data, existing_data):
    combined = pd.concat([existing_data, new_data])
    combined['posting_date'] = pd.to_datetime(combined['posting_date'])
    grouped = combined.groupby(['job_title', 'location', 'posting_date', 'employment_type'], as_index=False).agg({
        'salary': 'mean',
        'vacancies': 'sum'
    })
    return grouped

def update_daily():
    print("Fetching and updating job data...")
    existing_data = load_existing_data()
    new_data = retrieve_vacancies()
    combined_data = merge_and_deduplicate(new_data, existing_data)
    save_data(combined_data)

@app.route('/api/jobs')
def get_jobs():
    df = load_existing_data()
    return jsonify(df.to_dict(orient='records'))

# Schedule task
scheduler = BackgroundScheduler()
scheduler.add_job(update_daily, 'interval', days=1)
scheduler.start()

# Initial run (optional)
update_daily()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

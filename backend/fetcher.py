import requests
import pandas as pd

def retrieve_vacancies():
    url = "https://api.hh.ru/vacancies"
    params = {"text": "IT", "area": 113, "per_page": 100}

    all_vacancies = []
    page = 0

    while True:
        params['page'] = page
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            vacancies = data.get('items', [])
            if not vacancies:
                break
            all_vacancies.extend(vacancies)
            page += 1
        else:
            break

    extracted_data = []
    for vacancy in all_vacancies:
        job_title = vacancy.get('name', 'N/A')
        salary_info = vacancy.get('salary')
        salary_from = salary_info.get('from') if salary_info else None
        salary_to = salary_info.get('to') if salary_info else None
        location = vacancy.get('area', {}).get('name', 'N/A')
        employment_type = vacancy.get('employment', {}).get('name', 'N/A')
        posting_date = vacancy.get('published_at', 'N/A')[:10]

        salary_avg = None
        if salary_from and salary_to:
            salary_avg = (salary_from + salary_to) // 2
        elif salary_from:
            salary_avg = salary_from
        elif salary_to:
            salary_avg = salary_to

        extracted_data.append({
            'job_title': job_title,
            'salary': salary_avg if salary_avg else 0,
            'vacancies': 1,
            'location': location,
            'employment_type': employment_type,
            'posting_date': posting_date
        })

    return pd.DataFrame(extracted_data)

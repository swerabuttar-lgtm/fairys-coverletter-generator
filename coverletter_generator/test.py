import requests

response = requests.post(
    "http://127.0.0.1:8000/generate",
    json={
        "job_title": "Web Developer",
        "company_name": "Systems Ltd",
        "job_description": "Looking for a web developer with HTML, CSS and JavaScript experience.",
        "candidate_background": "CS student with 2 projects in web development.",
        "tone": "confident"
    }
)

print(response.text)
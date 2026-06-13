# TalentIQ: Resume Ranking & Job Matching Engine

TalentIQ is an AI-powered HR platform that automates candidate screening. It reads resumes, extracts skills using NLP/Regex, and matches candidates to job descriptions using a Greedy matching algorithm.

## Features
* **Resume Parsing:** Extracts data from PDFs and DOCX files.
* **Smart Matching Engine:** Scores candidates based on Skill, Experience, and Certifications.
* **Targeted Job Assignment:** Assign subsets of candidates to specific jobs for isolated evaluation.
* **Interactive Analytics:** Chart.js dashboards showing top skills, experience distributions, and score breakdowns.
* **Advanced Search:** O(1) Hash Table lookups for skills, and O(log N) Binary Search for experience.

## Installation
1. Clone this repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Apply migrations: `python manage.py migrate`
6. Run server: `python manage.py runserver`

## Built With
* Django (Backend Framework)
* SQLite (Database)
* PyMuPDF & pdfplumber (Parsing)
* Pandas & Numpy (Analytics)
* Chart.js (Frontend Data Visualization)
* Vanilla CSS / Bootstrap (Styling)

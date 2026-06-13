import os

BASE_DIR = r"E:\SIC1004\hackathon"
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Define all templates as a dictionary: { "relative_path": "html_content" }
templates = {
    "hr/base.html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TalentIQ — HR Portal</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
  <style>
    body { overflow-x: hidden; background-color: #f8f9fa; }
    #sidebar { width: 250px; min-height: 100vh; background: #212529; position: fixed; top: 0; left: 0; z-index: 100; }
    #sidebar .nav-link { color: #adb5bd; padding: .5rem 1rem; }
    #sidebar .nav-link:hover, #sidebar .nav-link.active { color: white; background: rgba(255,255,255,.1); border-radius: 4px; }
    #sidebar .nav-section { color: #6c757d; font-size: .7rem; text-transform: uppercase; letter-spacing: .1em; padding: 1rem 1rem .25rem; }
    #main-content { margin-left: 250px; padding: 0; }
    .topbar { background: white; border-bottom: 1px solid #dee2e6; padding: .75rem 1.5rem; }
  </style>
</head>
<body>
<nav id="sidebar">
  <div class="p-3 border-bottom border-secondary">
    <h5 class="text-white mb-0"><i class="bi bi-lightning-charge-fill text-warning"></i> TalentIQ</h5>
    <small class="text-secondary">HR Portal</small>
  </div>
  <div class="p-2">
    <div class="nav-section">Main</div>
    <a href="{% url 'candidates:dashboard' %}" class="nav-link"><i class="bi bi-speedometer2 me-2"></i>Dashboard</a>
    <div class="nav-section">Candidates</div>
    <a href="{% url 'candidates:list' %}" class="nav-link"><i class="bi bi-people me-2"></i>All Candidates</a>
    <a href="{% url 'resumes:upload' %}" class="nav-link"><i class="bi bi-cloud-upload me-2"></i>Upload Resume</a>
    <div class="nav-section">Jobs</div>
    <a href="{% url 'jobs:list' %}" class="nav-link"><i class="bi bi-briefcase me-2"></i>All Jobs</a>
    <a href="{% url 'jobs:add' %}" class="nav-link"><i class="bi bi-plus-circle me-2"></i>Create Job</a>
    <div class="nav-section">Intelligence</div>
    <a href="{% url 'search:index' %}" class="nav-link"><i class="bi bi-search me-2"></i>Smart Search</a>
    <a href="{% url 'analytics:dashboard' %}" class="nav-link"><i class="bi bi-bar-chart-line me-2"></i>Analytics</a>
    <a href="{% url 'simulator:index' %}" class="nav-link"><i class="bi bi-sliders me-2"></i>Hiring Simulator</a>
    <div class="border-top border-secondary mt-3 pt-3 px-2">
      <a href="/candidate/" class="nav-link text-info"><i class="bi bi-person-circle me-2"></i>Candidate Portal ↗</a>
    </div>
  </div>
</nav>
<div id="main-content">
  <div class="topbar d-flex justify-content-between align-items-center">
    <h6 class="mb-0 text-muted">{% block page_title %}TalentIQ{% endblock %}</h6>
    <small class="text-muted"><i class="bi bi-circle-fill text-success me-1"></i>System Online</small>
  </div>
  <div class="p-4">
    {% if messages %}{% for msg in messages %}<div class="alert alert-{{ msg.tags }} alert-dismissible fade show">{{ msg }}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>{% endfor %}{% endif %}
    {% block content %}{% endblock %}
  </div>
</div>
{% block extra_js %}{% endblock %}
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""",
    
    "hr/dashboard/index.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="row g-3 mb-4">
  <div class="col-md-3"><div class="card border-0 shadow-sm text-white bg-primary"><div class="card-body"><h6 class="card-subtitle mb-1">Total Candidates</h6><h2 class="card-title mb-0">{{ total_candidates }}</h2></div></div></div>
  <div class="col-md-3"><div class="card border-0 shadow-sm text-white bg-success"><div class="card-body"><h6 class="card-subtitle mb-1">Total Jobs</h6><h2 class="card-title mb-0">{{ total_jobs }}</h2></div></div></div>
  <div class="col-md-3"><div class="card border-0 shadow-sm text-white bg-warning"><div class="card-body"><h6 class="card-subtitle mb-1">Avg Match Score</h6><h2 class="card-title mb-0">{{ avg_match_score }}%</h2></div></div></div>
  <div class="col-md-3"><div class="card border-0 shadow-sm text-white bg-info"><div class="card-body"><h6 class="card-subtitle mb-1">Top Candidate</h6><h2 class="card-title mb-0 fs-5 mt-2">{{ top_candidate|default:"None" }}</h2></div></div></div>
</div>
<div class="row g-3 mb-4">
  <div class="col-md-6"><div class="card shadow-sm"><div class="card-header">Top Skills</div><div class="card-body text-center"><img src="data:image/png;base64,{{ chart_top_skills }}" class="img-fluid"></div></div></div>
  <div class="col-md-6"><div class="card shadow-sm"><div class="card-header">Experience Distribution</div><div class="card-body text-center"><img src="data:image/png;base64,{{ chart_exp_dist }}" class="img-fluid"></div></div></div>
</div>
<div class="row g-3">
  <div class="col-md-8">
    <div class="card shadow-sm"><div class="card-header">Top Ranked Candidates</div>
      <table class="table table-hover mb-0"><thead class="table-light"><tr><th>#</th><th>Name</th><th>Job</th><th>Match %</th><th>Action</th></tr></thead>
      <tbody>{% for m in top_ranked %}<tr><td>{{ m.rank }}</td><td>{{ m.candidate_name }}</td><td>{{ m.job_title }}</td><td><div class="progress" style="height:20px"><div class="progress-bar {% if m.match_percentage >= 70 %}bg-success{% elif m.match_percentage >= 40 %}bg-warning{% else %}bg-danger{% endif %}" style="width:{{ m.match_percentage }}%">{{ m.match_percentage }}%</div></div></td><td><a href="{% url 'candidates:detail' m.candidate_id %}" class="btn btn-sm btn-outline-primary">View</a></td></tr>{% endfor %}</tbody></table>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card shadow-sm"><div class="card-header">Recent Jobs</div><ul class="list-group list-group-flush">{% for job in recent_jobs %}<li class="list-group-item d-flex justify-content-between"><span>{{ job.title }}</span><a href="{% url 'matching:results' job.pk %}" class="btn btn-sm btn-outline-secondary">Rankings</a></li>{% endfor %}</ul></div>
  </div>
</div>
{% endblock %}""",

    "hr/resume/upload.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="card shadow-sm mx-auto" style="max-width: 600px;">
  <div class="card-header bg-primary text-white"><i class="bi bi-cloud-upload"></i> Upload Resume</div>
  <div class="card-body">
    <form method="post" action="{% url 'resumes:upload' %}" enctype="multipart/form-data">
      {% csrf_token %}
      <div class="mb-3">
        <label class="form-label">Select File (.pdf, .docx, .txt)</label>
        <input type="file" name="resume_file" class="form-control" required accept=".pdf,.docx,.txt">
      </div>
      <button type="submit" class="btn btn-primary w-100">Upload & Analyze</button>
    </form>
  </div>
</div>
{% endblock %}""",

    "hr/resume/preview.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="row">
  <div class="col-md-7">
    <div class="card shadow-sm mb-3">
      <div class="card-header bg-primary text-white">Extracted Candidate Data</div>
      <div class="card-body">
        <form method="post" action="{% url 'resumes:confirm' resume.pk %}">{% csrf_token %}
          <div class="mb-3"><label class="form-label">Full Name</label><input type="text" name="name" class="form-control" required></div>
          <div class="row mb-3"><div class="col-md-6"><label class="form-label">Email</label><input type="email" name="email" class="form-control" required></div><div class="col-md-6"><label class="form-label">Phone</label><input type="text" name="phone" class="form-control"></div></div>
          <div class="mb-3"><label class="form-label">Education</label><input type="text" name="education" class="form-control" value="{{ extracted.education }}"></div>
          <div class="mb-3"><label class="form-label">Experience (years)</label><input type="number" name="experience_years" class="form-control" value="{{ extracted.experience }}" step="0.5"></div>
          <div class="mb-3"><label class="form-label">Detected Skills</label><div class="d-flex flex-wrap gap-2">{% for skill in extracted.skills %}<div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" name="skills" value="{{ skill.skill_name }}" checked><label class="form-check-label badge bg-info text-dark">{{ skill.skill_name }}</label></div>{% endfor %}</div></div>
          <div class="mb-3"><label class="form-label">Certifications</label>{% for cert in extracted.certifications %}<div class="form-check"><input class="form-check-input" type="checkbox" name="certifications" value="{{ cert }}" checked><label class="form-check-label">{{ cert }}</label></div>{% endfor %}</div>
          <button type="submit" class="btn btn-success">Confirm & Save</button> <a href="{% url 'resumes:upload' %}" class="btn btn-outline-danger">Discard</a>
        </form>
      </div>
    </div>
  </div>
  <div class="col-md-5"><div class="card shadow-sm"><div class="card-header">Raw Text</div><div class="card-body"><textarea class="form-control" rows="20" readonly>{{ extracted.raw_text }}</textarea></div></div></div>
</div>
{% endblock %}""",

    "hr/candidates/list.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="card shadow-sm"><div class="card-header">All Candidates ({{ total_count }})</div>
<div class="card-body p-0">
  <table class="table mb-0"><thead class="table-light"><tr><th>Name</th><th>Email</th><th>Exp</th><th>Action</th></tr></thead>
  <tbody>{% for c in candidates %}<tr><td>{{ c.name }}</td><td>{{ c.email }}</td><td>{{ c.experience_years }}</td><td><a href="{% url 'candidates:detail' c.pk %}" class="btn btn-sm btn-outline-primary">View</a></td></tr>{% endfor %}</tbody></table>
</div></div>
{% endblock %}""",

    "hr/candidates/detail.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="row mb-4"><div class="col-md-8"><div class="card shadow-sm"><div class="card-body"><h3>{{ candidate.name }}</h3><p class="text-muted">{{ candidate.email }} | {{ candidate.phone }}</p><p><strong>Edu:</strong> {{ candidate.education }}</p><p><strong>Exp:</strong> {{ candidate.experience_years }} yrs</p></div></div></div></div>
<div class="card shadow-sm mb-3"><div class="card-header">Skills</div><table class="table mb-0"><tbody>{% for cs in skills %}<tr><td><span class="badge bg-info text-dark">{{ cs.skill.skill_name }}</span></td><td>{{ cs.proficiency_level }}</td></tr>{% endfor %}</tbody></table></div>
<div class="card shadow-sm mb-3"><div class="card-header">Job Matches</div><table class="table mb-0"><tbody>{% for m in matches %}<tr class="{% if m.match_percentage >= 70 %}table-success{% endif %}"><td>{{ m.job.title }}</td><td>{{ m.match_percentage }}%</td><td><a href="{% url 'matching:explain' m.job.pk candidate.pk %}" class="btn btn-sm btn-outline-primary">Explain</a></td></tr>{% endfor %}</tbody></table></div>
{% endblock %}""",

    "hr/jobs/list.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="card shadow-sm"><div class="card-header d-flex justify-content-between"><span>All Jobs</span><a href="{% url 'jobs:add' %}" class="btn btn-sm btn-primary">Create Job</a></div>
<table class="table mb-0"><thead class="table-light"><tr><th>Title</th><th>Min Exp</th><th>Actions</th></tr></thead>
<tbody>{% for j in jobs %}<tr><td>{{ j.title }}</td><td>{{ j.min_experience }}</td><td><a href="{% url 'matching:run' j.pk %}" class="btn btn-sm btn-warning">Run Match</a> <a href="{% url 'matching:results' j.pk %}" class="btn btn-sm btn-outline-secondary">Rankings</a></td></tr>{% endfor %}</tbody></table>
</div>
{% endblock %}""",

    "hr/jobs/add.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="card shadow-sm mx-auto" style="max-width: 800px;">
  <div class="card-header">Create New Job</div>
  <div class="card-body">
    <form method="post">{% csrf_token %}
      <div class="mb-3"><label>Job Title</label><input type="text" name="title" class="form-control" required></div>
      <div class="mb-3"><label>Min Experience (years)</label><input type="number" name="min_experience" class="form-control" step="0.5" required></div>
      <div class="mb-3"><label>Description</label><textarea name="description" class="form-control"></textarea></div>
      <div class="mb-3"><label>Required Skills & Weights (1.0 = normal, 2.0 = critical)</label>
        <div class="row g-2">{% for skill, category in all_skills.items %}<div class="col-md-4"><div class="input-group input-group-sm"><div class="input-group-text"><input type="checkbox" name="required_skills" value="{{ skill }}"></div><span class="form-control">{{ skill }}</span><input type="number" name="weight_{{ skill }}" class="form-control" value="1.0" step="0.5"></div></div>{% endfor %}</div>
      </div>
      <button class="btn btn-success">Save Job</button>
    </form>
  </div>
</div>
{% endblock %}""",

    "hr/jobs/detail.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="card shadow-sm"><div class="card-header">{{ job.title }}</div><div class="card-body"><p>Min Exp: {{ job.min_experience }} yrs</p><a href="{% url 'matching:run' job.pk %}" class="btn btn-primary">Run Match Engine</a> <a href="{% url 'matching:results' job.pk %}" class="btn btn-secondary">View Rankings</a></div></div>
{% endblock %}""",

    "hr/matching/explain.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="card shadow-sm mb-4"><div class="card-header">Score Breakdown: {{ candidate.name }} vs {{ job.title }}</div><div class="card-body">
  <h4>Overall: <span class="badge bg-primary">{{ match.match_percentage }}%</span></h4>
  <p>Skill: {{ match.skill_score|floatformat:1 }}% | Exp: {{ match.experience_score|floatformat:1 }}% | Cert: {{ match.certification_score|floatformat:1 }}%</p>
  <table class="table mt-3"><thead><tr><th>Skill</th><th>Matched?</th></tr></thead><tbody>{% for s in skill_breakdown %}<tr><td>{{ s.skill }}</td><td>{% if s.matched %}Yes{% else %}No{% endif %}</td></tr>{% endfor %}</tbody></table>
</div></div>
{% endblock %}""",

    "hr/matching/results.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="card shadow-sm"><div class="card-header">Rankings for {{ job.title }}</div>
<table class="table mb-0"><thead class="table-light"><tr><th>Rank</th><th>Candidate</th><th>Match %</th><th>Details</th></tr></thead>
<tbody>{% for m in matches %}<tr><td>#{{ m.rank }}</td><td>{{ m.candidate.name }}</td><td>{{ m.match_percentage }}%</td><td><a href="{% url 'matching:explain' job.pk m.candidate.pk %}" class="btn btn-sm btn-info">Explain</a></td></tr>{% endfor %}</tbody></table></div>
{% endblock %}""",

    "hr/search/index.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="card shadow-sm mb-3"><div class="card-header">Smart Search</div><div class="card-body">
  <form method="get" class="d-flex gap-2">
    <input type="text" name="skill" class="form-control" placeholder="Search by Skill (e.g. Python)" value="{{ params.skill }}">
    <button class="btn btn-primary">Search</button>
  </form>
</div></div>
{% if results is not None %}
<div class="card shadow-sm"><div class="card-header">Results ({{ algo_used }})</div><table class="table mb-0"><tbody>{% for c in results %}<tr><td>{{ c.name }}</td><td><a href="{% url 'candidates:detail' c.pk %}">View</a></td></tr>{% endfor %}</tbody></table></div>
{% endif %}
{% endblock %}""",

    "hr/analytics/index.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="row g-3">
  <div class="col-md-6"><div class="card shadow-sm"><div class="card-header">Top Skills</div><img src="data:image/png;base64,{{ chart_skills }}" class="img-fluid"></div></div>
  <div class="col-md-6"><div class="card shadow-sm"><div class="card-header">Match Scores</div><img src="data:image/png;base64,{{ chart_match }}" class="img-fluid"></div></div>
</div>
{% endblock %}""",

    "hr/simulator/index.html": """{% extends "hr/base.html" %}
{% block content %}
<div class="row">
  <div class="col-md-4"><div class="card shadow-sm"><div class="card-header">Simulator Controls</div><div class="card-body">
    <select id="sim-job" class="form-select mb-3">{% for j in jobs %}<option value="{{ j.pk }}">{{ j.title }}</option>{/for %}</select>
    <label>Exp Weight</label><input type="range" id="exp-weight" value="20" class="form-range">
    <label>Cert Weight</label><input type="range" id="cert-weight" value="10" class="form-range">
    <button class="btn btn-warning w-100 mt-3" onclick="runSimulation()">Recalculate (In-Memory)</button>
  </div></div></div>
  <div class="col-md-8"><div class="card shadow-sm"><div class="card-header">Live Rankings</div><table class="table" id="sim-results"></table></div></div>
</div>
{% endblock %}
{% block extra_js %}
<script>
async function runSimulation() {
  const jobId = document.getElementById('sim-job').value;
  const expW = document.getElementById('exp-weight').value / 100;
  const certW = document.getElementById('cert-weight').value / 100;
  const res = await fetch('/api/simulator/recalculate/', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({job_id: jobId, exp_weight: expW, cert_weight: certW})
  });
  const data = await res.json();
  const html = data.rankings.map(r => `<tr><td>#${r.rank}</td><td>${r.candidate_name}</td><td>${r.total_score}%</td></tr>`).join('');
  document.getElementById('sim-results').innerHTML = html;
}
</script>
{% endblock %}""",

    "candidate/base.html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><title>Candidate Portal</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<nav class="navbar navbar-dark bg-dark"><div class="container"><a class="navbar-brand">TalentIQ Portal</a><span class="text-muted">Ephemeral Session (24h)</span></div></nav>
<div class="container py-4">{% block content %}{% endblock %}</div>
</body>
</html>""",

    "candidate/index.html": """{% extends "candidate/base.html" %}
{% block content %}
<div class="card shadow-sm mx-auto mt-5" style="max-width: 500px;"><div class="card-header bg-primary text-white">Upload Resume for Analysis</div><div class="card-body">
  <form method="post" action="{% url 'portal:upload' %}" enctype="multipart/form-data">{% csrf_token %}
    <input type="file" name="resume_file" class="form-control mb-3" required>
    <button type="submit" class="btn btn-primary w-100">Analyze My Resume</button>
  </form>
</div></div>
{% endblock %}""",

    "candidate/results.html": """{% extends "candidate/base.html" %}
{% block content %}
<div class="row">
  <div class="col-md-4"><div class="card shadow-sm text-center py-5"><h3>Resume Score</h3><h1 class="text-primary">{{ session.resume_score }}</h1></div></div>
  <div class="col-md-8"><div class="card shadow-sm"><div class="card-header">Detected Skills</div><div class="card-body">{% for s in session.extracted_skills %}<span class="badge bg-info text-dark m-1 fs-6">{{ s }}</span>{% endfor %}</div></div></div>
</div>
{% endblock %}"""
}

# Ensure directories exist and write files
for rel_path, content in templates.items():
    full_path = os.path.join(TEMPLATES_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Created {len(templates)} template files.")

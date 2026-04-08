from flask import Flask, render_template_string, request, redirect, url_for, session
import csv
import os

app = Flask(__name__)
app.secret_key = "ftc_championship_key"

# --- File Setup ---
user_file = 'users.csv'
pit_file = 'pit_data.csv'
match_file = 'match_data.csv'

for f_path, headers in [
  (user_file, ['username', 'password']),
  (pit_file, ['scout', 'team_num', 'drive_type', 'notes']),
  (match_file, ['scout', 'team_num', 'match_num', 'points'])
]:
  if not os.path.exists(f_path):
    with open(f_path, 'w', newline='') as f:
      csv.writer(f).writerow(headers)

# --- Modern UI Theme (CSS) ---
base_style = '''
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  :root {
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --text-main: #1e293b;
    --text-muted: #64748b;
    --nav-bg: #0f172a;
    --border: #e2e8f0;
  }
  body { 
    font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: var(--bg); color: var(--text-main); 
    background-image: radial-gradient(circle at 2px 2px, #1e293b 1px, transparent 0); background-size: 40px 40px;
  }
  nav { 
    background: var(--nav-bg); padding: 0 20px; display: flex; gap: 25px; justify-content: center; 
    height: 60px; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
  }
  nav a { color: #94a3b8; text-decoration: none; font-weight: 500; font-size: 14px; transition: color 0.2s; }
  nav a:hover { color: white; }
  .container { padding: 40px 20px; max-width: 900px; margin: auto; }
  .card { 
    background: var(--card-bg); padding: 32px; border-radius: 12px; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid var(--border); margin-bottom: 24px; 
  }
  input, select, textarea { 
    width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid var(--border); 
    border-radius: 8px; box-sizing: border-box; font-size: 16px;
  }
  button { 
    background: var(--primary); color: white; border: none; padding: 14px; 
    border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; width: 100%;
  }
  button:hover { background: var(--primary-hover); }
  .table-container { overflow-x: auto; border-radius: 12px; border: 1px solid var(--border); }
  table { width: 100%; border-collapse: collapse; background: white; }
  th { background: #f1f5f9; color: var(--text-muted); font-size: 12px; text-transform: uppercase; padding: 16px; text-align: left; }
  td { padding: 16px; border-top: 1px solid var(--border); }
  .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; background: #e0e7ff; color: #4338ca; }
</style>
'''

nav_bar = '''
<nav>
  <div style="display: flex; gap: 25px;">
    <a href="/">Home</a>
    <a href="/pit">Pit Scout</a>
    <a href="/match">Match Scout</a>
    <a href="/data">Analysis</a>
  </div>
  <div style="margin-left: auto;">
    <a href="/logout" style="color: #ef4444;">Logout</a>
  </div>
</nav>
'''

# --- Page Templates ---

home_page = base_style + nav_bar + '''
<div class="container">
  <div class="card">
    <h1>FTC Scouting Dashboard</h1>
    <p style="color: var(--text-muted);">Welcome back, <strong>{{ user }}</strong></p>
    <hr style="border: 0; border-top: 1px solid var(--border); margin: 20px 0;">
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div style="padding: 15px; border: 1px solid var(--border); border-radius: 8px;">
            <h4 style="margin: 0;">Pit Scouting</h4>
            <p style="font-size: 13px; color: var(--text-muted);">Record robot specs and hardware.</p>
        </div>
        <div style="padding: 15px; border: 1px solid var(--border); border-radius: 8px;">
            <h4 style="margin: 0;">Analysis</h4>
            <p style="font-size: 13px; color: var(--text-muted);">View averages and performance.</p>
        </div>
    </div>
  </div>
</div>
'''

pit_form = base_style + nav_bar + '''
<div class="container">
  <div class="card">
    <h2>Pit Report</h2>
    <form method="POST">
      <label>Drivetrain Type</label>
      <select name="drive_type">
        <option value="Mecanum">Mecanum</option>
        <option value="Tank">Tank</option>
        <option value="Swerve">Swerve</option>
        <option value="Other">Other</option>
      </select>
      <label>Robot Notes</label>
      <textarea name="notes" placeholder="Strengths, weaknesses, etc." rows="4" style="width:100%; border-radius:8px; border:1px solid var(--border); padding:10px;"></textarea>
      <button type="submit">Submit Report</button>
    </form>
  </div>
</div>
'''

match_form = base_style + nav_bar + '''
<div class="container">
  <div class="card">
    <h2>Match Performance</h2>
    <form method="POST">
      <input type="number" name="team_num" placeholder="Team Number" required>
      <input type="number" name="match_num" placeholder="Match Number" required>
      <input type="number" name="points" placeholder="Points Scored" required>
      <button type="submit">Save Match Data</button>
    </form>
  </div>
</div>
'''

analysis_page = base_style + nav_bar + '''
<div class="container">
  <div class="card">
    <h2>Team Rankings</h2>
    <form method="GET" action="/data" style="display: flex; gap: 10px; margin-bottom: 20px;">
      <input type="number" name="filter_team" placeholder="Filter by Team #" style="margin-bottom:0;">
      <button type="submit" style="width: auto; padding: 0 20px;">Filter</button>
    </form>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Team #</th>
            <th>Avg Points</th>
            <th>Matches</th>
            <th>Drive</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {% for team, stats in results.items() %}
          <tr>
            <td><strong>{{ team }}</strong></td>
            <td><span class="badge">{{ stats.avg }}</span></td>
            <td>{{ stats.count }}</td>
            <td>{{ stats.drive_type }}</td>
            <td style="color: var(--text-muted); font-size: 13px;">{{ stats.notes }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
'''

# --- Helper Logic ---

def get_pit_info():
  info = {}
  if os.path.exists(pit_file):
    with open(pit_file, 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
        info[row['team_num']] = {'drive_type':row['drive_type'], 'notes':row['notes']}
  return info

# --- Routes ---

@app.route('/')
def home():
  if 'user' not in session: return redirect('/login')
  return render_template_string(home_page, user=session['user'])

@app.route('/pit', methods=['GET', 'POST'])
def pit():
  if 'user' not in session: return redirect('/login')
  if request.method == 'POST':
    with open(pit_file, 'a', newline='') as f:
      csv.writer(f).writerow([session['user'], request.form['team_num'], request.form['drive_type'], request.form['notes']])
    return redirect('/data')
  return render_template_string(pit_form)

@app.route('/match', methods=['GET', 'POST'])
def match():
  if 'user' not in session: return redirect('/login')
  if request.method == 'POST':
    with open(match_file, 'a', newline='') as f:
      csv.writer(f).writerow([session['user'], request.form['team_num'], request.form['match_num'], request.form['points']])
    return redirect('/data')
  return render_template_string(match_form)

@app.route('/data')
def data_view():
  if 'user' not in session: return redirect('/login')
  filter_team = request.args.get('filter_team')
  pit_dict = get_pit_info()
  team_stats = {}

  # Process pit info first
  for t, info in pit_dict.items():
    if filter_team and t != filter_team: continue
    team_stats[t] = {'total': 0, 'count': 0, 'avg': 0.0, 'drive_type': info['drive_type'], 'notes': info['notes']}

  # Merge match info
  if os.path.exists(match_file):
    with open(match_file, 'r') as f:
      reader = csv.DictReader(f)
      for row in reader:
        t = row['team_num']
        if filter_team and t != filter_team: continue
        if t not in team_stats:
          team_stats[t] = {'total': 0, 'count': 0, 'avg': 0, 'drive_type': 'Unknown', 'notes': 'N/A'}
        team_stats[t]['total'] += int(row['points'])
        team_stats[t]['count'] += 1
        team_stats[t]['avg'] = round(team_stats[t]['total'] / team_stats[t]['count'], 1)

  return render_template_string(analysis_page, results=team_stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    u, p = request.form['username'], request.form['password']
    with open(user_file, 'r') as f:
      for row in csv.reader(f):
        if row and row[0] == u and row[1] == p:
          session['user'] = u
          return redirect('/')
    return "Invalid login"
  return render_template_string(base_style + '<div class="container"><div class="card"><h2>Login</h2><form method="POST"><input name="username" placeholder="Team Name"><input name="password" placeholder="Team Number"><button>Login</button></form><a href="/register" style="font-size:13px; color:var(--text-muted);">Create Account</a></div></div>')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    with open(user_file, 'a', newline='') as f:
      csv.writer(f).writerow([request.form['username'], request.form['password']])
    return redirect('/login')
  return render_template_string(base_style + '<div class="container"><div class="card"><h2>Register</h2><form method="POST"><input name="username" placeholder="Username"><input type="password" name="password" placeholder="Password"><button>Create Account</button></form></div></div>')

@app.route('/logout')
def logout():
  session.clear()
  return redirect('/login')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)

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
    (pit_file, ['scout', 'team_num', 'drive_type', 'turret', 'indexer', 'auto', 'teleop', 'notes']),
    (match_file, ['scout', 'team_num', 'match_num', 'points', 'parking', 'fouls', 'match_notes'])
]:
    if not os.path.exists(f_path):
        with open(f_path, 'w', newline='') as f:
            csv.writer(f).writerow(headers)

# --- THE CYBER STYLE ---
# This block MUST be at the top of every page string
base_style = '''
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --primary: #6366f1; --accent: #06b6d4; --bg: #0f172a; --card-bg: #1e293b;
    --text-main: #f1f5f9; --text-muted: #94a3b8; --border: #334155;
  }
  body { 
    font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: var(--bg); color: var(--text-main); 
    background-image: radial-gradient(circle at 2px 2px, #1e293b 1px, transparent 0); background-size: 40px 40px;
  }
  nav { 
    background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(10px); padding: 0 30px; display: flex; 
    height: 70px; align-items: center; border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100;
  }
  nav a { color: var(--text-muted); text-decoration: none; font-weight: 600; font-size: 14px; margin-right: 25px;}
  nav a:hover { color: var(--accent); }

  .container { padding: 40px 20px; max-width: 1100px; margin: auto; }
  .card { 
    background: var(--card-bg); padding: 30px; border-radius: 16px; border: 1px solid var(--border); 
    margin-bottom: 24px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  }

  button { 
    background: var(--accent); color: white; border: none; padding: 16px; border-radius: 10px; 
    cursor: pointer; font-size: 14px; font-weight: 700; width: 100%; transition: 0.2s;
  }
  button:hover { opacity: 0.8; }

  input, select, textarea { 
    width: 100%; padding: 14px; margin-bottom: 20px; border: 1px solid var(--border); 
    border-radius: 10px; background: #0f172a; color: white; font-size: 16px; box-sizing: border-box;
  }
  label { color: var(--accent); font-size: 11px; letter-spacing: 2px; font-weight: 800; display: block; margin-bottom: 8px; }

  table { width: 100%; border-collapse: collapse; }
  th { color: var(--text-muted); font-size: 11px; text-transform: uppercase; padding: 15px; text-align: left; border-bottom: 1px solid var(--border); }
  td { padding: 18px 15px; border-bottom: 1px solid rgba(51, 65, 85, 0.5); }

  .progress-bg { background: #0f172a; width: 80px; height: 8px; border-radius: 4px; display: inline-block; vertical-align: middle; }
  .progress-fill { background: var(--accent); height: 100%; border-radius: 4px; box-shadow: 0 0 10px var(--accent); }
  .rank-badge { background: #334155; padding: 4px 10px; border-radius: 6px; font-weight: 800; color: var(--accent); }
</style>
'''

nav_bar = '''
<nav>
  <a href="/" style="font-size: 20px; color: white; margin-right: 40px;">SQUID // <span style="color:var(--accent)">NETWORK</span></a>
  <a href="/">DASHBOARD</a> <a href="/pit">ABOUT MY ROBOT</a> <a href="/match">MY MATCHES</a> <a href="/data">ANALYSIS</a>
  <a style="margin-left: auto; color: #f87171;" href="/logout">LOGOUT</a>
</nav>
'''

# --- PAGES ---

home_page = base_style + nav_bar + '''
<div class="container">
  <h1>SYSTEM DASHBOARD</h1>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
    <div class="card">
      <h3 style="margin-top:0">Active Session</h3>
      <p style="color: var(--text-muted)">User: <span style="color:var(--accent)">{{ user }}</span></p>
      <p style="color: var(--text-muted)">Team Number: <span style="color:var(--accent)">{{ team_num }}</span></p>
    </div>
    <div class="card">
      <h3 style="margin-top:0">Quick Actions</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <a href="/pit"><button>ABOUT MY ROBOT</button></a>
        <a href="/match"><button>MY MATCHES</button></a>
      </div>
    </div>
  </div>
  <div class="card" style="margin-top: 20px;">
    <h3>Fleet Overview</h3>
    <p style="color: var(--text-muted);">Welcome to Squid Network. Track your robot data here.</p>
  </div>
</div>
'''

pit_form = base_style + nav_bar + '''
<div class="container" style="max-width: 600px;">
  <div class="card">
    <h2>ROBOT DATA</h2>
    <form method="POST">
      <label>DRIVE BASE TYPE</label>
      <select name="drive_type">
        <option value="Mecanum">MECANUM</option>
        <option value="Tank">TANK</option>
        <option value="Swerve">SWERVE</option>
      </select>
      <label>TURRET PRESENT?</label>
      <select name="turret">
        <option value="yes">YES</option>
        <option value="no">NO</option>
      </select>
      <label>INDEXER PRESENT?</label>
      <select name="indexer">
        <option value="yes">YES</option>
        <option value="no">NO</option>
      </select>
      <label>AUTONOMOUS</label>
      <select name="auto">
        <option value="nothing">DOES NOTHING</option>
        <option value="leaves">LEAVES AREA</option>
        <option value="scores">SCORES</option>
      </select>
      <label>TELEOP</label>
      <select name="teleop">
        <option value="nothing">NO SCORING</option>
        <option value="scores">SCORES</option>
        <option value="patterns">SCORES PATTERNS</option>
      </select>
      <label>OTHER NOTES</label>
      <textarea name="notes" placeholder="ROBOT CAPABILITIES..." rows="5"></textarea>
      <button type="submit">SAVE ROBOT DATA</button>
    </form>
  </div>
</div>
'''

match_form = base_style + nav_bar + '''
<div class="container" style="max-width: 600px;">
  <div class="card">
    <h2>NEW MATCH REPORT</h2>
    <form method="POST">
      <div style="display: flex; gap: 10px;">
        <div style="flex:1"><label>MATCH #</label><input type="number" name="match_num" required></div>
        <div style="flex:1"><label>POINTS</label><input type="number" name="points" required></div>
      </div>
      <label>PARKING STATUS</label>
      <select name="parking">
        <option value="Fully">FULLY</option>
        <option value="Partially">PARTIALLY</option>
        <option value="No Parking">NO_PARKING</option>
      </select>
      <label>FOULS INCURRED</label>
      <select name="fouls">
        <option value="None">NONE</option>
        <option value="Minor">MINOR</option>
        <option value="Major">MAJOR</option>
      </select>
      <label>PATTERNS SCORED</label>
      <input type='number' name='patterns' required>
      <label>INDIVIDUAL ARTEFACTS SCORED (IF RECORDED, ELSE SKIP)</label>
      <input type='number' name='patterns'>
      <label>MATCH OBSERVATIONS</label>
      <textarea name="match_notes" rows="3"></textarea>
      <button type="submit">SAVE MATCH DATA</button>
    </form>
  </div>
</div>
'''

analysis_page = base_style + nav_bar + '''
<div class="container">
  <div class="card">
    <h2>BATTLE_ANALYTICS</h2>
    <table>
      <thead>
        <tr><th>TEAM</th><th>AVG_SCORE</th><th>RUNS</th><th>BASE</th><th>INTEL</th></tr>
      </thead>
      <tbody>
        {% for team, stats in results.items() %}
        <tr>
          <td><span class="rank-badge">{{ stats.team_name }}: {{team}}</span></td>
          <td>
            {{ stats.avg }}
            <div class="progress-bg"><div class="progress-fill" style="width: {{ stats.avg if stats.avg < 100 else 100 }}%"></div></div>
          </td>
          <td>{{ stats.count }}</td>
          <td><code>{{ stats.drive_type }}</code></td>
          <td style="font-size: 11px; color: var(--text-muted);">{{ stats.notes }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
'''


# --- LOGIC ---

def get_pit_info():
    info = {}
    if os.path.exists(pit_file):
        with open(pit_file, 'r') as f:
            # strip() helps ignore accidental spaces in your manual header update
            reader = csv.DictReader(f)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            for row in reader:
                t = row.get('team_num')
                if t:
                    info[t] = {
                        'team_name': row.get('scout', 'UNKNOWN'),
                        'drive_type': row.get('drive_type', 'UNKNOWN'),
                        'notes': row.get('notes', 'N/A')
                    }
    return info


@app.route('/')
def home():
    if 'user' not in session or 'team_num' not in session: return redirect('/login')
    return render_template_string(home_page, user=session['user'], team_num=session['team_num'])


@app.route('/pit', methods=['GET', 'POST'])
def pit():
    if 'user' not in session or 'team_num' not in session: return redirect('/login')
    if request.method == 'POST':
        with open(pit_file, 'a', newline='') as f:
            csv.writer(f).writerow([
                session['user'], session['team_num'],
                request.form['drive_type'],
                request.form['turret'],
                request.form['indexer'],
                request.form['auto'],
                request.form['teleop'],
                request.form['notes']
            ])
        return redirect('/data')
    return render_template_string(pit_form)


@app.route('/match', methods=['GET', 'POST'])
def match():
    if 'user' not in session or 'team_num' not in session: return redirect('/login')
    if request.method == 'POST':
        with open(match_file, 'a', newline='') as f:
            csv.writer(f).writerow([
                session['user'], session['team_num'], request.form['match_num'],
                request.form['points'], request.form['parking'], request.form['fouls'], request.form['match_notes']
            ])
        return redirect('/data')
    return render_template_string(match_form)


@app.route('/data')
def data_view():
    if 'user' not in session or 'team_num' not in session: return redirect('/login')
    pit_dict = get_pit_info()
    team_stats = {}

    filter_team = request.args.get('filter_team')
    for t, info in pit_dict.items():
        if filter_team and t != filter_team: continue
        team_stats[t] = {'team_name': info['team_name'], 'total': 0, 'count': 0, 'avg': 0.0, 'drive_type': info['drive_type'], 'notes': info['notes']}

    if os.path.exists(match_file):
        with open(match_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                t = row['team_num']
                if t not in team_stats:
                    p_info = pit_dict.get(t, {'team_name':row['scout'], 'drive_type': 'UNKNOWN', 'notes': 'N/A'})
                    team_stats[t] = {'team_name': p_info['team_name'], 'total': 0, 'count': 0, 'drive_type': p_info['drive_type'], 'notes': p_info['notes']}
                team_stats[t]['total'] += int(row['points'])
                team_stats[t]['count'] += 1
                team_stats[t]['avg'] = round(team_stats[t]['total'] / team_stats[t]['count'], 1)

    sorted_stats = dict(sorted(team_stats.items(), key=lambda x: x[1].get('avg', 0), reverse=True))
    return render_template_string(analysis_page, results=sorted_stats)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'].upper().strip(), request.form['password'].upper().strip()
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                for row in csv.reader(f):
                    if row and row[0].upper() == u and row[1] == p:
                        session['user'] = u
                        session['team_num'] = p
                        return redirect('/')
        return render_template_string(
            base_style + '<div class="container" style="max-width:400px"><div class="card"><h2>LOGIN</h2><form method="POST"><input name="username" placeholder="Team Name"><input name="password" placeholder="Team Number"><button>LOGIN</button></form><a href="/register" style="font-size:13px; color:var(--text-muted);">Create Account</a><h4>INVALID LOGIN - have you created an account yet?</h4></div></div>')
    return render_template_string(
        base_style + '<div class="container" style="max-width:400px"><div class="card"><h2>LOGIN</h2><form method="POST"><input name="username" placeholder="Team Name"><input name="password" placeholder="Team Number"><button>LOGIN</button></form><a href="/register" style="font-size:13px; color:var(--text-muted);">Create Account</a></div></div>')

@app.route('/register', methods=['GET', 'POST'])
def register():
  error = ' '
  if request.method == 'POST':
    u = request.form['username'].upper().strip()
    p = request.form['password'].upper().strip()

    user_exists = False
    if os.path.exists(user_file):
      with open(user_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
          if row and row[0].upper() == u.upper() and row[1] == p:
            user_exists = True
            break

    if user_exists:
      error = 'Account already registered'
    else:
      with open(user_file, 'a', newline='') as f:
        csv.writer(f).writerow([u, p])
      session['user'] = u
      session['team_num'] = p
      return redirect('/')

  return render_template_string(base_style + f'<div class="container" style="max-width:400px"><div class="card"><h2>REGISTER</h2><form method="POST"><input name="username" placeholder="Team Name"><input name="password" placeholder="Team Number"><button>Create Account</button></form><h4>{error}</h4><a href="/login" style="font-size:13px; color:var(--text-muted);">Already have an account? LOGIN HERE</a></div></div>')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

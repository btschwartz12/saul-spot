from flask import Flask, request, render_template, send_from_directory
import os
from difflib import SequenceMatcher

app = Flask(__name__)

def is_similar(a, b, threshold):
    """Check if two strings are similar above a certain threshold."""
    return SequenceMatcher(None, a, b).ratio() >= threshold

def search_transcripts(root_dir, search_string, similarity_threshold=1.0):
    matches = []
    # Ensure the root directory path is correctly set relative to this script's location
    root_dir = os.path.join(os.path.dirname(__file__), root_dir)
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.txt'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, start=1):
                        if similarity_threshold < 1.0:
                            # Inexact match case
                            if is_similar(line.strip(), search_string, similarity_threshold):
                                season_number = root.split(os.sep)[-1]  # Assuming the season directory is the last directory in the path
                                episode_name = file.rsplit('.', 1)[0]
                                # Adjust here to include season/episode in the match path
                                match_path = os.path.join(season_number, file)  # Construct path with season and filename
                                matches.append((season_number, episode_name, i, match_path))
                        else:
                            # Exact match case
                            if search_string.lower() in line.lower():
                                season_number = root.split(os.sep)[-1]  # Assuming the season directory is the last directory in the path
                                episode_name = file.rsplit('.', 1)[0]
                                # Adjust here to include season/episode in the match path
                                match_path = os.path.join(season_number, file)  # Construct path with season and filename
                                matches.append((season_number, episode_name, i, match_path))
    for match in matches:
        print(match)
    return matches


@app.route('/', methods=['GET', 'POST'])
def index():
    root_directory = "transcripts"  # Base directory for transcripts
    season_structure = {}
    base_dir = os.path.join(app.root_path, root_directory)
    # Gather available seasons and episodes
    for season in os.listdir(base_dir):
        season_path = os.path.join(base_dir, season)
        if os.path.isdir(season_path):
            episodes = [ep.rsplit('.', 1)[0] for ep in os.listdir(season_path) if ep.endswith('.txt')]
            season_structure[season] = sorted(episodes)

    sorted_seasons = {season: season_structure[season] for season in sorted(season_structure.keys())}

    if request.method == 'POST':
        search_term = request.form['search_term']
        match_percentage = float(request.form['match_percentage']) / 100.0
        matches = search_transcripts(root_directory, search_term, match_percentage)
        return render_template('index.html', matches=matches, search_term=search_term, match_percentage=match_percentage*100, seasons=season_structure)
    else:
        return render_template('index.html', matches=None, seasons=sorted_seasons)


@app.route('/transcripts/<path:filename>')
def transcripts(filename):
    base_dir = os.path.join(app.root_path, 'transcripts')  # Ensure this is the correct path to your transcripts directory
    
    # Normalize and secure the filename
    secure_filename = os.path.normpath(filename)
    
    # Ensure the path starts within the intended directory structure
    if secure_filename.startswith('..') or os.path.isabs(secure_filename) or '..' in secure_filename.split(os.sep):
        return "Invalid path", 404
    
    # Construct the full path including the season directory
    filepath = os.path.join(base_dir, secure_filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        line_numbered_content = "".join(f"{i+1}. {line}<br>" for i, line in enumerate(lines))
        return f"<html><body>{line_numbered_content}</body></html>"
    except FileNotFoundError:
        return "File not found", 404

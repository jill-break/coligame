from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import func
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    scores = db.relationship('Score', backref='user', lazy=True)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_type = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    difficulty = db.Column(db.String(50))

class GameSuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    features = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Game Category Routes
@app.route('/word-games')
def word_games():
    return render_template('word_games.html')

@app.route('/card-games')
def card_games():
    return render_template('card_games.html')

@app.route('/puzzle-games')
def puzzle_games():
    return render_template('puzzle_games.html')

@app.route('/arcade-games')
def arcade_games():
    return render_template('arcade_games.html')

@app.route('/board-games')
def board_games():
    return render_template('board_games.html')

@app.route('/quiz-games')
def quiz_games():
    return render_template('quiz_games.html')

@app.route('/adventure-games')
def adventure_games():
    return render_template('adventure_games.html')

@app.route('/educational-games')
def educational_games():
    return render_template('educational_games.html')

# Individual Game Routes
@app.route('/games/number-guessing')
@login_required
def number_guessing():
    return render_template('games/number_guessing.html', 
                         game_name='Number Guessing Game',
                         game_type='number_guessing')

@app.route('/games/word-scramble')
@login_required
def word_scramble():
    return render_template('games/word_scramble.html',
                         game_name='Word Scramble',
                         game_type='word_scramble')

@app.route('/games/hangman')
@login_required
def hangman():
    return render_template('games/hangman.html',
                         game_name='Hangman',
                         game_type='hangman')

@app.route('/games/word-search')
@login_required
def word_search():
    return render_template('games/word_search.html',
                         game_name='Word Search',
                         game_type='word_search')

@app.route('/games/crossword')
@login_required
def crossword():
    return render_template('games/crossword.html',
                         game_name='Crossword Puzzle',
                         game_type='crossword')

@app.route('/games/anagrams')
@login_required
def anagrams():
    return render_template('games/anagrams.html',
                         game_name='Anagrams',
                         game_type='anagrams')

# Leaderboard Routes
@app.route('/leaderboard')
@login_required
def leaderboard():
    # Get all scores from the database
    scores = Score.query.order_by(Score.score.desc()).all()
    
    # Organize scores by game type
    leaderboards = {}
    
    for score in scores:
        game_type = score.game_type
        if game_type not in leaderboards:
            leaderboards[game_type] = []
        
        leaderboards[game_type].append({
            'player': score.user.username,
            'score': score.score,
            'date': score.timestamp,
            'difficulty': score.difficulty
        })
    
    # Sort each game's scores by score (descending)
    for game_type in leaderboards:
        leaderboards[game_type].sort(key=lambda x: x['score'], reverse=True)
    
    return render_template('leaderboard.html', 
                         leaderboards=leaderboards,
                         current_user=current_user)

@app.route('/global-leaderboard')
def global_leaderboard():
    scores = Score.query.order_by(Score.score.desc())\
        .limit(20)\
        .all()
    return render_template('global_leaderboard.html', scores=scores)

@app.route('/profile')
@login_required
def profile():
    # Get user statistics
    total_games = Score.query.filter_by(user_id=current_user.id).count()
    high_score = db.session.query(func.max(Score.score)).filter_by(user_id=current_user.id).scalar() or 0
    
    # Get user rank
    user_rank = db.session.query(func.count(Score.id) + 1).filter(
        Score.score > db.session.query(func.max(Score.score)).filter_by(user_id=current_user.id)
    ).scalar()
    
    # Get game statistics
    game_stats = []
    for game_type in ['memory_match', 'snake', 'tic_tac_toe', 'general_knowledge', 'text_adventure', 'spelling_bee']:
        scores = Score.query.filter_by(user_id=current_user.id, game_type=game_type).all()
        if scores:
            game_stats.append({
                'game_name': game_type.replace('_', ' ').title(),
                'games_played': len(scores),
                'high_score': max(score.score for score in scores),
                'average_score': sum(score.score for score in scores) / len(scores)
            })
    
    # Get recent activity
    recent_activity = []
    recent_scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.timestamp.desc()).limit(5).all()
    
    for score in recent_scores:
        recent_activity.append({
            'icon': 'trophy' if score.score > 50 else 'star',
            'text': f"Scored {score.score} points in {score.game_type.replace('_', ' ').title()}",
            'timestamp': score.timestamp.strftime('%Y-%m-%d %H:%M')
        })
    
    # Get achievements
    achievements = [
        {
            'name': 'First Victory',
            'description': 'Win your first game',
            'icon': 'medal',
            'unlocked': total_games > 0
        },
        {
            'name': 'High Roller',
            'description': 'Score over 100 points in any game',
            'icon': 'star',
            'unlocked': high_score >= 100
        },
        {
            'name': 'Dedicated Player',
            'description': 'Play 50 games',
            'icon': 'gamepad',
            'unlocked': total_games >= 50
        },
        {
            'name': 'Master of All',
            'description': 'Play every game type',
            'icon': 'crown',
            'unlocked': len(game_stats) >= 6
        },
        {
            'name': 'Perfect Score',
            'description': 'Get a perfect score in any game',
            'icon': 'trophy',
            'unlocked': high_score >= 1000
        }
    ]
    
    return render_template('profile.html',
                         user=current_user,
                         total_games=total_games,
                         high_score=high_score,
                         rank=user_rank,
                         game_stats=game_stats,
                         recent_activity=recent_activity,
                         achievements=achievements)

@app.route('/api/save_score', methods=['POST'])
@login_required
def save_score():
    data = request.get_json()
    game_type = data.get('game_type')
    score = data.get('score')
    difficulty = data.get('difficulty', 'easy')
    
    if not game_type or not score:
        return jsonify({'status': 'error', 'message': 'Missing required fields'})
    
    new_score = Score(
        user_id=current_user.id,
        game_type=game_type,
        score=score,
        difficulty=difficulty
    )
    
    db.session.add(new_score)
    db.session.commit()
    
    return jsonify({'status': 'success'})

# Card Games
@app.route('/games/memory-match')
@login_required
def memory_match():
    return render_template('games/memory_match.html',
                         game_name='Memory Match',
                         game_type='memory_match')

@app.route('/games/solitaire')
@login_required
def solitaire():
    return render_template('games/solitaire.html',
                         game_name='Solitaire',
                         game_type='solitaire')

@app.route('/games/blackjack')
@login_required
def blackjack():
    return render_template('games/blackjack.html',
                         game_name='Blackjack',
                         game_type='blackjack')

# Puzzle Games
@app.route('/games/sliding-puzzle')
@login_required
def sliding_puzzle():
    return render_template('games/sliding_puzzle.html',
                         game_name='Sliding Puzzle',
                         game_type='sliding_puzzle')

@app.route('/games/sudoku')
@login_required
def sudoku():
    return render_template('games/sudoku.html',
                         game_name='Sudoku',
                         game_type='sudoku')

@app.route('/games/tetris')
@login_required
def tetris():
    return render_template('games/tetris.html',
                         game_name='Tetris',
                         game_type='tetris')

# Arcade Games
@app.route('/games/snake')
@login_required
def snake():
    return render_template('games/snake.html',
                         game_name='Snake',
                         game_type='snake')

@app.route('/games/space-invaders')
@login_required
def space_invaders():
    return render_template('games/space_invaders.html',
                         game_name='Space Invaders',
                         game_type='space_invaders')

@app.route('/games/pacman')
@login_required
def pacman():
    return render_template('games/pacman.html',
                         game_name='Pac-Man',
                         game_type='pacman')

# Board Games
@app.route('/games/chess')
@login_required
def chess():
    return render_template('games/chess.html',
                         game_name='Chess',
                         game_type='chess')

@app.route('/games/checkers')
@login_required
def checkers():
    return render_template('games/checkers.html',
                         game_name='Checkers',
                         game_type='checkers')

@app.route('/games/tic-tac-toe')
@login_required
def tic_tac_toe():
    return render_template('games/tic_tac_toe.html',
                         game_name='Tic Tac Toe',
                         game_type='tic_tac_toe')

# Quiz Games
@app.route('/games/general-knowledge')
@login_required
def general_knowledge():
    return render_template('games/general_knowledge.html',
                         game_name='General Knowledge Quiz',
                         game_type='general_knowledge')

@app.route('/games/math-quiz')
@login_required
def math_quiz():
    return render_template('games/math_quiz.html',
                         game_name='Math Quiz',
                         game_type='math_quiz')

@app.route('/games/word-quiz')
@login_required
def word_quiz():
    return render_template('games/word_quiz.html',
                         game_name='Word Quiz',
                         game_type='word_quiz')

# Adventure Games
@app.route('/games/text-adventure')
@login_required
def text_adventure():
    return render_template('games/text_adventure.html',
                         game_name='Text Adventure',
                         game_type='text_adventure')

@app.route('/games/treasure-hunt')
@login_required
def treasure_hunt():
    return render_template('games/treasure_hunt.html',
                         game_name='Treasure Hunt',
                         game_type='treasure_hunt')

@app.route('/games/escape-room')
@login_required
def escape_room():
    return render_template('games/escape_room.html',
                         game_name='Escape Room',
                         game_type='escape_room')

# Educational Games
@app.route('/games/spelling-bee')
@login_required
def spelling_bee():
    return render_template('games/spelling_bee.html',
                         game_name='Spelling Bee',
                         game_type='spelling_bee')

@app.route('/games/geography-quiz')
@login_required
def geography_quiz():
    return render_template('games/geography_quiz.html',
                         game_name='Geography Quiz',
                         game_type='geography_quiz')

@app.route('/games/science-quiz')
@login_required
def science_quiz():
    return render_template('games/science_quiz.html',
                         game_name='Science Quiz',
                         game_type='science_quiz')

@app.route('/suggest-game', methods=['POST'])
@login_required
def suggest_game():
    data = request.get_json()
    
    suggestion = GameSuggestion(
        name=data['name'],
        category=data['category'],
        description=data['description'],
        features=data['features'],
        user_id=current_user.id
    )
    
    db.session.add(suggestion)
    db.session.commit()
    
    return jsonify({'message': 'Suggestion submitted successfully'})

@app.route('/admin/suggestions')
@login_required
def view_suggestions():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    suggestions = GameSuggestion.query.order_by(GameSuggestion.created_at.desc()).all()
    return render_template('admin/suggestions.html', suggestions=suggestions)

@app.route('/admin/suggestions/<int:id>/<action>')
@login_required
def handle_suggestion(id, action):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    suggestion = GameSuggestion.query.get_or_404(id)
    
    if action == 'approve':
        suggestion.status = 'approved'
        # Here you would typically create the game template
        # and add it to your game collection
        flash('Game suggestion approved!', 'success')
    elif action == 'reject':
        suggestion.status = 'rejected'
        flash('Game suggestion rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('view_suggestions'))

@app.route('/api/suggestions/<int:id>')
@login_required
def get_suggestion(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    suggestion = GameSuggestion.query.get_or_404(id)
    return jsonify({
        'name': suggestion.name,
        'category': suggestion.category,
        'user': suggestion.user.username,
        'created_at': suggestion.created_at.isoformat(),
        'status': suggestion.status,
        'description': suggestion.description,
        'features': suggestion.features
    })

# Game data structure
GAMES = {
    'card': [
        {'name': 'memory_match', 'title': 'Memory Match', 'description': 'Test your memory by matching pairs of cards'},
        {'name': 'solitaire', 'title': 'Solitaire', 'description': 'Classic card game of patience'},
        {'name': 'blackjack', 'title': 'Blackjack', 'description': 'Try your luck against the dealer'}
    ],
    'arcade': [
        {'name': 'snake', 'title': 'Snake', 'description': 'Classic snake game with modern graphics'},
        {'name': 'tetris', 'title': 'Tetris', 'description': 'Arrange falling blocks to clear lines'}
    ],
    'board': [
        {'name': 'tic_tac_toe', 'title': 'Tic Tac Toe', 'description': 'Classic two-player game'},
        {'name': 'chess', 'title': 'Chess', 'description': 'Strategic board game for two players'}
    ],
    'puzzle': [
        {'name': 'sliding_puzzle', 'title': 'Sliding Puzzle', 'description': 'Arrange tiles in order'},
        {'name': 'word_search', 'title': 'Word Search', 'description': 'Find hidden words in a grid'}
    ],
    'quiz': [
        {'name': 'general_knowledge', 'title': 'General Knowledge', 'description': 'Test your knowledge across various subjects'},
        {'name': 'math_quiz', 'title': 'Math Quiz', 'description': 'Challenge yourself with mathematical problems'}
    ],
    'adventure': [
        {'name': 'text_adventure', 'title': 'Text Adventure', 'description': 'Embark on an interactive story adventure'}
    ],
    'educational': [
        {'name': 'spelling_bee', 'title': 'Spelling Bee', 'description': 'Improve your spelling skills'}
    ]
}

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = []
    
    # Search through all games
    for category, games in GAMES.items():
        for game in games:
            if (query in game['name'].lower() or 
                query in game['title'].lower() or 
                query in game['description'].lower() or 
                query in category.lower()):
                results.append({
                    'name': game['name'],
                    'title': game['title'],
                    'category': category,
                    'description': game['description']
                })
    
    return jsonify(results)

@app.route('/')
def home():
    if current_user.is_authenticated:
        # Get user's recent games
        recent_games = Score.query.filter_by(user_id=current_user.id)\
            .order_by(Score.timestamp.desc())\
            .limit(5).all()
        
        # Get user's high scores
        high_scores = db.session.query(
            Score.game_type,
            func.max(Score.score).label('high_score')
        ).filter_by(user_id=current_user.id)\
        .group_by(Score.game_type).all()
        
        # Get user's rank
        user_rank = db.session.query(func.count(Score.id) + 1).filter(
            Score.score > db.session.query(func.max(Score.score))
            .filter_by(user_id=current_user.id)
        ).scalar()
        
        return render_template('home.html',
                             recent_games=recent_games,
                             high_scores=high_scores,
                             user_rank=user_rank,
                             games=GAMES)
    return render_template('home.html', games=GAMES)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
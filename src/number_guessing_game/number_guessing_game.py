import random
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime
import re

class Player:
    def __init__(self, username):
        self.username = username
        self.wins = 0
        self.losses = 0
        self.games_played = 0
        self.daily_wins = 0
        self.last_played_date = None
        self.current_target = 5
        self.registration_date = datetime.now().isoformat()

class NumberGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Game variables
        self.secret_number = random.randint(1, 10)
        self.attempts = 3
        self.game_active = True
        self.current_player = None
        self.players = {}
        
        # Load saved players
        self.load_players()
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")
        
        # Create left and right frames for layout
        self.left_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.left_frame.pack(side=tk.LEFT, expand=True, fill="both", padx=(0, 10))
        
        self.right_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.right_frame.pack(side=tk.RIGHT, fill="y", padx=(10, 0))
        
        # Title
        title_label = tk.Label(
            self.left_frame,
            text="Number Guessing Game",
            font=("Helvetica", 20, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=10)
        
        # Player management frame
        self.player_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.player_frame.pack(pady=10)
        
        # Username entry
        self.player_entry = tk.Entry(
            self.player_frame,
            font=("Helvetica", 12),
            width=20
        )
        self.player_entry.pack(side=tk.LEFT, padx=5)
        
        # Login/Register button
        self.login_button = tk.Button(
            self.player_frame,
            text="Login/Register",
            command=self.login_player,
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            padx=10
        )
        self.login_button.pack(side=tk.LEFT, padx=5)
        
        # Current player label
        self.player_label = tk.Label(
            self.left_frame,
            text="No player logged in",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.player_label.pack(pady=5)
        
        # Milestone frame (Subway Surfers style)
        self.milestone_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.milestone_frame.pack(pady=10)
        
        # Create milestone indicators
        self.milestone_labels = []
        for i in range(3):
            frame = tk.Frame(self.milestone_frame, bg="#f0f0f0")
            frame.pack(side=tk.LEFT, padx=5)
            
            # Circle background
            canvas = tk.Canvas(frame, width=40, height=40, bg="#f0f0f0", highlightthickness=0)
            canvas.pack()
            canvas.create_oval(5, 5, 35, 35, fill="#e0e0e0")
            
            # Number label
            label = tk.Label(
                frame,
                text=str([5, 10, 20][i]),
                font=("Helvetica", 12, "bold"),
                bg="#e0e0e0",
                fg="#666666"
            )
            label.pack()
            self.milestone_labels.append((canvas, label))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.milestone_frame,
            length=200,
            mode='determinate',
            maximum=20
        )
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        
        # Rules text (initially hidden)
        self.rules_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.rules_frame.pack(pady=10)
        
        rules_text = """
        Game Rules:
        1. Guess a number between 1 and 10
        2. You have 3 attempts
        3. Get hints if your guess is too high or low
        4. Win by guessing the correct number!
        5. Daily targets: 5 → 10 → 20 wins
        6. Usernames must be 3-15 characters long
        7. Only letters, numbers, and underscores allowed
        """
        self.rules_label = tk.Label(
            self.rules_frame,
            text=rules_text,
            font=("Helvetica", 10),
            bg="#f0f0f0",
            justify="left"
        )
        self.rules_label.pack()
        
        # Skip rules button
        self.skip_rules_button = tk.Button(
            self.rules_frame,
            text="Skip Rules",
            command=self.hide_rules,
            font=("Helvetica", 10),
            bg="#ff9800",
            fg="white"
        )
        self.skip_rules_button.pack(pady=5)
        
        # Initially hide rules
        self.rules_frame.pack_forget()
        
        # Attempts counter
        self.attempts_label = tk.Label(
            self.left_frame,
            text=f"Attempts remaining: {self.attempts}",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.attempts_label.pack(pady=10)
        
        # Entry field
        self.guess_entry = tk.Entry(
            self.left_frame,
            font=("Helvetica", 14),
            width=10
        )
        self.guess_entry.pack(pady=10)
        
        # Button frame for guess and new game
        self.button_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.button_frame.pack(pady=10)
        
        # Guess button
        self.guess_button = tk.Button(
            self.button_frame,
            text="Make Guess",
            command=self.make_guess,
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        self.guess_button.pack(side=tk.LEFT, padx=5)
        
        # New game/Forfeit button
        self.new_game_button = tk.Button(
            self.button_frame,
            text="New Game",
            command=self.new_game,
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=10
        )
        self.new_game_button.pack(side=tk.LEFT, padx=5)
        
        # Result label
        self.result_label = tk.Label(
            self.left_frame,
            text="",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.result_label.pack(pady=10)
        
        # Leaderboard frame (right side)
        leaderboard_frame = tk.LabelFrame(
            self.right_frame,
            text="🏆 Leaderboard",
            font=("Helvetica", 12, "bold"),
            bg="#f0f0f0"
        )
        leaderboard_frame.pack(fill="y")
        
        # Create Treeview for leaderboard
        self.leaderboard = ttk.Treeview(
            leaderboard_frame,
            columns=("Player", "Wins", "Losses", "Win Rate", "Daily Wins"),
            show="headings",
            height=15
        )
        
        # Configure column widths and headings
        self.leaderboard.heading("Player", text="Player")
        self.leaderboard.heading("Wins", text="Wins")
        self.leaderboard.heading("Losses", text="Losses")
        self.leaderboard.heading("Win Rate", text="Win Rate")
        self.leaderboard.heading("Daily Wins", text="Daily Wins")
        
        # Set column widths
        self.leaderboard.column("Player", width=120)
        self.leaderboard.column("Wins", width=60)
        self.leaderboard.column("Losses", width=60)
        self.leaderboard.column("Win Rate", width=80)
        self.leaderboard.column("Daily Wins", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(leaderboard_frame, orient="vertical", command=self.leaderboard.yview)
        self.leaderboard.configure(yscrollcommand=scrollbar.set)
        
        # Pack the leaderboard and scrollbar
        self.leaderboard.pack(side=tk.LEFT, pady=5, padx=5, fill="y")
        scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Style the leaderboard
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        
        # Bind Enter key to make_guess
        self.guess_entry.bind('<Return>', lambda event: self.make_guess())
        
        # Update leaderboard
        self.update_leaderboard()
        
    def hide_rules(self):
        self.rules_frame.pack_forget()
        
    def update_milestones(self, player):
        daily_wins = player.daily_wins
        self.progress_bar['value'] = daily_wins
        
        # Update milestone indicators
        for i, (canvas, label) in enumerate(self.milestone_labels):
            target = [5, 10, 20][i]
            if daily_wins >= target:
                canvas.itemconfig(1, fill="#4CAF50")  # Green for completed
                label.config(fg="white")
            elif daily_wins >= target - 2:
                canvas.itemconfig(1, fill="#ff9800")  # Orange for close
                label.config(fg="white")
            else:
                canvas.itemconfig(1, fill="#e0e0e0")  # Gray for not reached
                label.config(fg="#666666")
                
    def update_interface_for_login(self, username):
        # Hide login elements
        self.player_frame.pack_forget()
        
        # Show player name
        self.player_label.config(text=username)
        self.player_label.pack(pady=5)
        
        # Show rules
        self.rules_frame.pack(pady=10)
        
        # Update milestones
        self.update_milestones(self.players[username])
        
    def update_interface_for_logout(self):
        # Show login elements
        self.player_frame.pack(pady=10)
        
        # Hide player name
        self.player_label.pack_forget()
        
        # Hide rules
        self.rules_frame.pack_forget()
        
        # Reset milestones
        self.progress_bar['value'] = 0
        for canvas, label in self.milestone_labels:
            canvas.itemconfig(1, fill="#e0e0e0")
            label.config(fg="#666666")
            
    def toggle_forfeit_button(self):
        if self.game_active:
            self.new_game_button.config(text="Forfeit Game", bg="#f44336")
        else:
            self.new_game_button.config(text="New Game", bg="#2196F3")
            
    def forfeit_game(self):
        if self.game_active:
            if messagebox.askyesno("Forfeit Game", "Are you sure you want to forfeit this game?"):
                self.game_active = False
                self.players[self.current_player].losses += 1
                self.players[self.current_player].games_played += 1
                self.result_label.config(
                    text=f"Game Forfeited! The number was {self.secret_number}",
                    fg="red"
                )
                self.save_players()
                self.update_leaderboard()
                self.toggle_forfeit_button()
                
    def new_game(self):
        if not self.current_player:
            messagebox.showwarning("No Player", "Please login or register first!")
            return
            
        if self.game_active:
            self.forfeit_game()
        else:
            self.secret_number = random.randint(1, 10)
            self.attempts = 3
            self.game_active = True
            self.attempts_label.config(text=f"Attempts remaining: {self.attempts}")
            self.result_label.config(text="")
            self.guess_entry.delete(0, tk.END)
            self.guess_entry.focus()
            self.toggle_forfeit_button()
            
    def login_player(self):
        username = self.player_entry.get().strip()
        
        # If username exists, just log in
        if username in self.players:
            self.check_daily_reset(self.players[username])
            self.current_player = username
            self.update_interface_for_login(username)
            self.update_leaderboard()
            messagebox.showinfo("Welcome Back", f"Welcome back, {username}!")
            return
            
        # Validate new username
        is_valid, message = self.validate_username(username)
        if not is_valid:
            messagebox.showwarning("Invalid Username", message)
            return
            
        # Create new player
        self.players[username] = Player(username)
        self.current_player = username
        self.update_interface_for_login(username)
        self.update_leaderboard()
        self.save_players()
        messagebox.showinfo("Success", f"Welcome new player: {username}!")
        
    def update_leaderboard(self):
        # Clear current items
        for item in self.leaderboard.get_children():
            self.leaderboard.delete(item)
            
        # Sort players by wins
        sorted_players = sorted(
            self.players.items(),
            key=lambda x: (x[1].wins, -x[1].losses),
            reverse=True
        )
        
        # Add players to leaderboard
        for username, player in sorted_players:
            win_rate = f"{(player.wins / (player.wins + player.losses) * 100):.1f}%" if (player.wins + player.losses) > 0 else "0%"
            
            # Add crown emoji for top 3 players
            display_name = username
            if sorted_players.index((username, player)) < 3:
                crowns = ["👑", "🥈", "🥉"][sorted_players.index((username, player))]
                display_name = f"{crowns} {username}"
            
            # Highlight current player
            if username == self.current_player:
                self.leaderboard.insert("", "end", text=display_name, values=(
                    display_name, player.wins, player.losses, win_rate, player.daily_wins
                ), tags=("current_player",))
            else:
                self.leaderboard.insert("", "end", text=display_name, values=(
                    display_name, player.wins, player.losses, win_rate, player.daily_wins
                ))
        
        # Configure tag for current player
        self.leaderboard.tag_configure("current_player", background="#e3f2fd", foreground="#1976d2")
        
    def make_guess(self):
        if not self.game_active:
            return
            
        if not self.current_player:
            messagebox.showwarning("No Player", "Please login or register first!")
            return
            
        try:
            guess = int(self.guess_entry.get())
            
            if guess < 1 or guess > 10:
                messagebox.showwarning("Invalid Input", "Please enter a number between 1 and 10!")
                return
                
            self.attempts -= 1
            self.attempts_label.config(text=f"Attempts remaining: {self.attempts}")
            
            if guess == self.secret_number:
                self.result_label.config(
                    text=f"🎉 Congratulations! You've guessed the correct number!\nThe number was {self.secret_number}!",
                    fg="green"
                )
                self.game_active = False
                self.players[self.current_player].wins += 1
                self.players[self.current_player].daily_wins += 1
                self.players[self.current_player].games_played += 1
                self.update_target(self.players[self.current_player])
                self.update_milestones(self.players[self.current_player])
                self.toggle_forfeit_button()
                messagebox.showinfo("Success", "You've won! Start a new game to play again!")
            elif guess < self.secret_number:
                self.result_label.config(text="Too low! Try a higher number.", fg="blue")
            else:
                self.result_label.config(text="Too high! Try a lower number.", fg="red")
                
            if self.attempts == 0 and self.game_active:
                self.result_label.config(
                    text=f"Game Over! The number was {self.secret_number}",
                    fg="red"
                )
                self.game_active = False
                self.players[self.current_player].losses += 1
                self.players[self.current_player].games_played += 1
                self.toggle_forfeit_button()
                messagebox.showinfo("Game Over", "You've run out of attempts! Start a new game to play again!")
                
            self.save_players()
            self.update_leaderboard()
                
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number!")
            
    def validate_username(self, username):
        if not username:
            return False, "Username cannot be empty!"
        if len(username) < 3:
            return False, "Username must be at least 3 characters long!"
        if len(username) > 15:
            return False, "Username must be less than 15 characters!"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores!"
        if username in self.players:
            return False, "Username is already taken!"
        return True, "Username is valid!"
        
    def load_players(self):
        try:
            with open("players.json", "r") as f:
                data = json.load(f)
                for username, stats in data.items():
                    player = Player(username)
                    player.wins = stats["wins"]
                    player.losses = stats["losses"]
                    player.games_played = stats["games_played"]
                    player.daily_wins = stats.get("daily_wins", 0)
                    player.last_played_date = stats.get("last_played_date")
                    player.current_target = stats.get("current_target", 5)
                    player.registration_date = stats.get("registration_date", datetime.now().isoformat())
                    self.players[username] = player
        except FileNotFoundError:
            pass
            
    def save_players(self):
        data = {
            username: {
                "wins": player.wins,
                "losses": player.losses,
                "games_played": player.games_played,
                "daily_wins": player.daily_wins,
                "last_played_date": player.last_played_date,
                "current_target": player.current_target,
                "registration_date": player.registration_date
            }
            for username, player in self.players.items()
        }
        with open("players.json", "w") as f:
            json.dump(data, f)
            
    def check_daily_reset(self, player):
        today = datetime.now().date().isoformat()
        if player.last_played_date != today:
            player.daily_wins = 0
            player.current_target = 5
            player.last_played_date = today
            self.save_players()
            
    def update_target(self, player):
        if player.daily_wins >= player.current_target:
            if player.current_target == 5:
                player.current_target = 10
                messagebox.showinfo("Target Achieved!", "Congratulations! Your new daily target is 10 wins!")
            elif player.current_target == 10:
                player.current_target = 20
                messagebox.showinfo("Target Achieved!", "Congratulations! Your new daily target is 20 wins!")
            self.target_label.config(text=f"Daily Target: {player.current_target} wins")
            
def main():
    root = tk.Tk()
    app = NumberGuessingGame(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
from app import app, GAMES
import os

def validate_templates():
    print("Validating game templates...")
    missing_templates = []
    
    # Check all games in the GAMES constant
    for category, games in GAMES.items():
        for game in games:
            template_name = game['name'].replace('-', '_') + '.html'
            template_path = os.path.join('templates', 'games', template_name)
            
            if not os.path.exists(template_path):
                missing_templates.append(template_name)
                print(f"[-] Missing: {template_name}")
            else:
                print(f"[+] Found: {template_name}")
                
    if missing_templates:
        print(f"\nTotal missing templates: {len(missing_templates)}")
    else:
        print("\nAll game templates are present!")

if __name__ == "__main__":
    validate_templates()

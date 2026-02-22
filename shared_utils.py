import os
import json

def update_file_list(new_file=None):
    """
    Updates the file-list.json with all available files in /history and /root.
    This allows the frontend to know which files are available for download/viewing.
    """
    file_list_path = 'file-list.json'
    history_dir = 'history'
    
    # Collect all relevant JSON files from root
    root_files = [f for f in os.listdir('.') if f.endswith('.json') and f != 'file-list.json']
    
    # Collect all relevant JSON files from history
    history_files = []
    if os.path.exists(history_dir):
        # We store them with the path relative to root for the frontend fetch
        history_files = [f"history/{f}" for f in os.listdir(history_dir) if f.endswith('.json')]
    
    all_files = sorted(list(set(root_files + history_files)))
    
    with open(file_list_path, 'w', encoding='utf-8') as f:
        json.dump(all_files, f, ensure_ascii=False, indent=4)
    
    print(f"Updated {file_list_path} with {len(all_files)} files.")

if __name__ == "__main__":
    update_file_list()

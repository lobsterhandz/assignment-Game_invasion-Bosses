Dimensions & Layout:

Columns and Rows: Each sprite sheet should have 9 columns and 6 rows as per the current code in load_all_bosses():
python
Copy code
load_boss_animations(boss_name, sprite_sheet_path, columns=9, rows=6)
Consistent Frame Sizes: Each frame within the sheet should have consistent dimensions, as the script uses the number of columns and rows to calculate each frame's size.
Order of Animations: Each row of the sprite sheet corresponds to an action, such as:
Row 0: Idle
Row 1: Attack
Row 2: Hurt
Row 3: Die
Row 4: Taunt
Row 5: Special
This structure allows the script to correctly assign each animation type to an action.

Adding New Sprite Sheets:
To add a new boss sprite sheet:

Create a New Sprite Sheet:

Ensure the sprite sheet has 9 columns and 6 rows.
Each animation (like idle, attack, etc.) should be in a separate row.
Place in Bosses Directory:

Put the sprite sheet file (e.g., new_boss.png) into the Bosses directory.
The script will automatically load any .png file from this directory.
Naming:

The name of the .png file will be used as the boss name in your game.
For example, if you name the sprite sheet dragon_boss.png, the boss will be referred to as "dragon_boss" in the animation dictionary.
Modifying for More Flexibility:
If you want more flexibility in the future, such as different numbers of actions or animation rows, consider making the following changes:

Add Metadata for Each Boss:

Create a simple configuration file (e.g., JSON or a text file) in the Bosses folder to specify the number of rows and columns for each boss. This way, different bosses can have unique layouts.
Dynamic Loading:

Update load_all_bosses() to read the configuration and load each boss based on its specific structure. This could allow you to have bosses with different numbers of actions or more complex animations.
Example Workflow for Adding New Boss:
Create the Sprite Sheet: Make a .png file with 9 columns and 6 rows of frames, each row representing a specific action.
Name it Appropriately: For example, goblin_king.png.
Place it in the Bosses Folder: Add it to:
Copy code
TikTokLive-master/Game/Bosses/
Run the Script: The sprite_loader.py script will automatically detect and load the new boss, making it available for your game.
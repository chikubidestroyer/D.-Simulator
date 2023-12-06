# D. Simulator

## Building

Build the project and output the package in the `dist` directory:
```bash
pip install build
python3 -m build
```

## Testing

To test the project module locally, create a virtual environment first:
```bash
pip install virtualenv
python3 -m venv .venv
```

Then, activate the virtual environment:
```bash
source .venv/bin/activate # For Unix-like operating systems
.venv\bin\activate.bat    # For Windows
```

Finally, do a editable install using pip:
```bash
pip install -e .
```

Run the program by executing:
```bash
dsimulator
```

## TODO

### User Interface Design
- [x] Develop a visual user interface to represent vertex and edge tables, displaying their positions and connections. This could be a city map where each vertex represents a point of interest, and edges represent paths between them.
- [x] Display character and building information, showcasing details from the building, home, occupation, workplace, and inhabitant tables. This may include character profiles, homes, workplaces, etc.
- [x] Implement a system to show relationships between characters (relationship table) and track investigation status (status table) such as suspects, victims, and key events.

### Database Setup
- [x] Create an SQLite database using the provided schema, ensuring all constraints and relationships are correctly implemented.
- [x] Populate tables with initial data. Ensure diversity in characters, locations, and scenes for realism. Approximately 1000 records need to be populated (generate families, assign occupations, incomes, and addresses).

### Game Logic
- [x] Implement the killer's behavior algorithm based on the killer and killer_chara tables.
- [x] Develop a simulation system for roadblocks or impassable areas affecting the edge table.
- [x] Ensure interaction and updates between in-game actions (interrogation, evidence collection) and the database.
- [x] Calculate killer movement paths and required time.
- [x] Consider implementing a possible save/load mechanism.
- [x] Define characteristics of the killer and ordinary residents and their interactions.
- [x] Implement the sheriff's interrogation skills, road closure abilities, and suspect apprehension functionality.
- [x] If interrogation functionality is implemented, hide certain information from players and implement related features.

### SQLite Database Interaction
- [x] Implement functions to query the SQLite database to retrieve information about locations, characters, and events as needed.
- [x] Develop a mechanism to update the database based on player actions, including marking suspects, updating character statuses, or recording investigation progress.
- [x] Count the number of times each person was witnessed at a certain vertex.
- [x] List all possible via points given the start and end vertices and the time constraint.
- [x] List the inhabitants related to the victim.

### Player Feedback and Interaction
- [x] Provide clear feedback based on player actions and database updates. For example, if a player investigates a location, display relevant information from the database.

### Game Ending Determination
- [x] Implement a mechanism to determine the end of the game, whether by a specific date or through a reputation-based system.

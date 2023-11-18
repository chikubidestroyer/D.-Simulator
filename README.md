# D Simulator

## Building

Build the project and output the package in the `dist` directory:
```bash
pip install build
python3 -m build
```

To install and run the project locally, create a virtual environment first:
```bash
pip install virtualenv
python3 -m venv .venv
```

Then activate the virtual environment:
```bash
source .venv/bin/activate # For Unix-like operating systems
.venv\bin\activate.bat    # For Windows
```

Finally, install the .whl package and execute the program:
```bash
pip install dist/*.whl
dsimulator
```

## TODO

### User Interface Design
- [ ] Develop a visual user interface to represent vertex and edge tables, displaying their positions and connections. This could be a city map where each vertex represents a point of interest, and edges represent paths between them.
- [ ] Display character and building information, showcasing details from the building, home, occupation, workplace, and inhabitant tables. This may include character profiles, homes, workplaces, etc.
- [ ] Implement a system to show relationships between characters (relationship table) and track investigation status (status table) such as suspects, victims, and key events.
- [ ] Provide an interface overview as per the submitted proposal.
- [ ] Consider the uncertainty of the UI workload and address it towards the end.

### Database Setup
- [ ] Create an SQLite database using the provided schema, ensuring all constraints and relationships are correctly implemented.
- [ ] Populate tables with initial data. Ensure diversity in characters, locations, and scenes for realism. Approximately 1000 records need to be populated (generate families, assign occupations, incomes, and addresses).

### Python Programming for Game Logic
- [ ] Implement the killer's behavior algorithm based on the killer and killer_chara tables.
- [ ] Develop a simulation system for roadblocks or impassable areas affecting the edge table.
- [ ] Ensure real-time interaction and updates between in-game actions (interrogation, evidence collection) and the database.
- [ ] Calculate killer movement paths and required time.
- [ ] Consider implementing a possible save/load mechanism.
- [ ] Define characteristics of the killer and ordinary residents and their interactions.
- [ ] Implement the sheriff's interrogation skills, road closure abilities, and suspect apprehension functionality.
- [ ] If interrogation functionality is implemented, hide certain information from players and implement related features.

### SQLite Database Interaction
- [ ] Implement functions to query the SQLite database to retrieve information about locations, characters, and events as needed.
- [ ] Develop a mechanism to update the database based on player actions, including marking suspects, updating character statuses, or recording investigation progress.

### Player Feedback and Interaction
- [ ] Provide clear feedback based on player actions and database updates. For example, if a player investigates a location, display relevant information from the database.

### Game Ending Determination
- [ ] Implement a mechanism to determine the end of the game, whether by a specific date or through a reputation-based system.

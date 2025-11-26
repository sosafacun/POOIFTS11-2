# POOIFTS11
Final Project for OOP at IFTS N°11

## How to use
> [!NOTE]
> This was developed and tested on Python 3.8

1. Clone the repository
2. Create a venv
    - **On Windows**: 
        1. On a CMD write `python -m venv FacundoSosa`
        2. On the same cmd, activate the newly created venv `.\FacundoSosa\Scripts\Activate.ps1`
        3. Install the required dependencies by writing `pip install -r requirements.txt`
    - **On Linux**:
        - On a terminal write `python3 -m venv FacundoSosa`
        - On the same cmd, activate the newly created venv `.\FacundoSosa\Scripts\activate`
        3. Install the required dependencies by writing `pip install -r requirements.txt`
3. Run main.py from the venv


## Functional Requirements

- CMD execution
- No web frameworks
- No DBs.
- Data must be saved in a .csv file
- Read the data from the .csv file and turn it into a dictionary
- Must use OOP and *at least* the following classes:
    - Client
    - Appointment
    - Hairdresser or Appointment. This will manage all the main operations.
- The system must have an interactive main menu with options like:
    - Register new client
    - Schedule new appointment
    - Show all scheduled appointments
    - Re-schedule appointments
    - Save / Load data
    - Exit app

### How to handle data and data files

- Every time data is being saved, it must save the info into the dictionary and then save it to the csv
- The app must be able to convert from .csv to dict and from dict to .csv to achieve the feeling of a persistent database
- Whenever the app starts, it must load the .csv file automatically.

## Suggestions and personal goals
- Cannot make appointments at the same time for the same employee.
- Allow client, date or employee filtering.
- Handle exceptions.
- Use DateTime to handle schedules.
- Ask the user to confirm an old or new appointment. Once confirmed, the system has to save that date to the .csv, and load it.
- Whenever the user exits or cancels an operation, they have to confirm that there are unsaved changes that are going to be lost; as each time the main menu loads the .csv is read again to maintain data integrity.
- Does it have to be Python?
- Register the DOB of both clients and employees.
    - Employees' DOB will be used to grant them a full-pay free day.
    - Clients' DOB will be used to grant them a free haircut, available for the next 7 days (weekends included).
- CRUD clients
- CRUD employees
- CRUD appointments
- Check for valid (non-empty) data (no DOB, no name)
- Add some *color* to the CMD and make it look pretty.
- A week should be a vector that contains an array of possible schedules. One for each employee. This would turn a month into a 3D matrix, maybe?. <- This wasn't in the previous one and I was pulling my hair off thinking of ways to manage dates and schedules with datetime hours.
- The system will take the year it's currently in, and check for the file for that year.
    - If no file is in place, then it should create a new one (so in January 1st it should create 2026.csv) with all the possible weeks for the year.
    - So if February starts on a Wednesday, It will mark as Monday and Tuesday as non-working days (since they don't belong in February but in January) and mark Wednesday as the first working day.
- Using those generated yearly weeks, I can show the user during creation all the available and taken spots for each employee.
- The schedule should show only 2 weeks in advance (so the current week + 2 more) during schedule creation. 
- Any more weeks will not be shown unless the user wants to see the entire month or entire months selected.
- I have to check if 2 appointments happen at the same time to deny it happening.

@echo off
REM Check if the virtual environment folder exists
IF NOT EXIST "venv" (
    REM Create a virtual environment
    "C:\Users\Josh Benadiva\AppData\Local\Programs\Python\Python311\python.exe" -m venv venv
)

REM Activate the virtual environment
CALL venv\Scripts\activate


REM Run Flask app
flask run

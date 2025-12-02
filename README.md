# CookBook

## CookBook is a simple CRUD project, that was created for learning basics Flask functional

### Download repo
    git clone https://github.com/m1rstx/cookbook.git

### Create virtual environment
    python -m venv .venv

### Launch .venv
#### Windows
    PowerShell: 
    .venv\Scripts\Activate.ps1
    
    CMD: 
    .venv\Scripts\Activate.bat

#### Linux/MacOS
    source .venv/bin/activate


### Download requirements
    pip install -r requirements.txt


## Init DataBase
    flask --app flaskr init-db

## Launch app
    flask --app flaskr run

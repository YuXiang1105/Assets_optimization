# portfolio-optimization-poly-systems

## How to Run (Linux)

1. Clone the repository
``````
git clone https://github.com/YuXiang1105/portfolio-optimization-poly-systems.git
``````

2. Create virtual environment
``````
python -m venv venv
source venv/bin/activate
``````
You should see something like this
``````
(venv) USER: ~/Documentos/portfolio-optimization-poly-systems$
``````
To deactivate venv 
``````
deactivate
``````
3. Install dependencies
``````
pip install -r requirements.txt
``````
4. Install kernel for jupyter
``````
python -m ipykernel install --user --name=venv --display-name "Python (venv)"
``````
5. Run Jupyter
``````
jupyter lab
``````
## How to execute main
Instead of `python3 main.py` use
``````
python -m src.main
``````


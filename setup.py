from setuptools import setup, find_packages

setup(
    name="associacao-amigo-do-povo",
    version="0.1",
    packages=find_packages(),
    python_requires='>=3.11.0,<3.12',
    install_requires=[
        "Flask==2.3.3",
        "gunicorn==21.2.0",
        "Werkzeug==2.3.7",
        "psycopg2-binary==2.9.7",
        "SQLAlchemy==2.0.21",
        "numpy==1.24.3",
        "pandas==1.5.3",
        "openpyxl==3.1.2",
        "python-dotenv==1.0.0",
    ],
)
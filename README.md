# GUVI Honeypot Agent

A FastAPI-based honeypot agent for GUVI.

## Features

- FastAPI web server
- POST endpoint at `/guvi-honeypot`
- Google Generative AI integration support

## Requirements

- Python 3.7+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Mehtab-24/guvi-honeypot-agent.git
cd guvi-honeypot-agent
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the server using uvicorn:

```bash
uvicorn main:app --reload
```

The server will start on `http://127.0.0.1:8000`

Options:
- `--reload`: Enable auto-reload on code changes (development mode)
- `--host 0.0.0.0`: Make the server accessible externally
- `--port 8080`: Change the port (default is 8000)

Example with custom host and port:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## API Endpoints

- `GET /`: Root endpoint - Welcome message
- `POST /guvi-honeypot`: Placeholder honeypot endpoint

## Testing the API

You can test the API using curl:

```bash
# Test root endpoint
curl http://127.0.0.1:8000/

# Test honeypot endpoint
curl -X POST http://127.0.0.1:8000/guvi-honeypot
```

Or visit `http://127.0.0.1:8000/docs` for interactive API documentation (Swagger UI).

## License

See LICENSE file for details.
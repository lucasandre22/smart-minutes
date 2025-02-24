# SmartMinutes - Backend

This is the backend service for the SmartMinutes project. It provides APIs for transcribing, summarizing, and managing meeting-related data using **FastAPI** and locally running **Large Language Models (LLMs)**.

## 📂 Project Structure
```bash
├── action_items/     # All the classes related to the action items feature
├── api/              # Classes related to the FastAPI
├── core/             # config.py file and RAG database loading method
├── custom_request/   # Classes related to the Custom Request feature
├── databases/        # Where all the files consumed by the system are stored, like transcripts (Created when starting the project for the first )
├── llms/             # The standard LLM classes, used through the code
├── minutes/          # Classes related to the Meeting Minutes method
├── rag/              # Classes related to RAG
├── scripts/          # File parsers scripts
├── summarization/    # Classes related to the Summarization method
├── tests/            # Test classes
├── requirements.txt  # Python dependencies
├── utils.py          # Python file that stores some utilities used along the code
└── README.md         # This documentation file
```

## 📖 API Documentation
Once the backend is running, you can explore the API documentation:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
# 🤖 Single-Document FAQ Chatbot using RAG

A Retrieval-Augmented Generation (RAG) based chatbot that allows users to upload a PDF or TXT document and ask natural language questions. The chatbot retrieves the most relevant document chunks using semantic search and generates accurate, context-aware answers using the Groq Large Language Model (LLM).

This project demonstrates how Retrieval-Augmented Generation (RAG) can be used to build an intelligent document question-answering system.

---

# 📌 Features

- 📄 Upload PDF and TXT documents
- ✂️ Automatic document chunking
- 🧠 Semantic embeddings for document chunks
- 🔍 Cosine similarity-based retrieval
- 🤖 AI-generated answers using Groq LLM
- 💬 Chat history support
- 🔄 Follow-up question handling
- 📚 View retrieved source chunks
- 📄 Display PDF page number of the retrieved answer
- 📊 Similarity confidence progress bar
- ⚙️ Adjustable Top-K retrieval
- ⚙️ Adjustable similarity threshold
- 🧹 Clear session and chat history

---

# 🛠️ Tech Stack

## Frontend
- Streamlit

## Backend
- Python

## AI / Machine Learning
- Retrieval-Augmented Generation (RAG)
- Sentence Transformers
- Cosine Similarity

## LLM
- Groq API

## PDF Processing
- pdfplumber
- pypdf

## Environment Management
- python-dotenv

## Numerical Computing
- NumPy

---

# 📂 Project Structure

```
faq_bot_intern_challenge/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
│
├── data/
│   └── sample_docs/
│
├── src/
│   ├── extract.py
│   ├── chunk.py
│   ├── embed.py
│   ├── retrieve.py
│   ├── generate.py
│   └── utils.py
│
└── assets/
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/faq-chatbot-rag.git
```

---

## 2. Move into the Project

```bash
cd faq-chatbot-rag
```

---

## 3. Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Create a .env File

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_groq_api_key_here

TOP_K=3

SIMILARITY_THRESHOLD=0.25

CHUNK_SIZE=250

CHUNK_OVERLAP=50
```

---

# ▶️ Running the Project

Start the Streamlit application.

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 🚀 How It Works

## Step 1

Upload a PDF or TXT document.

↓

## Step 2

Extract text from the uploaded document.

↓

## Step 3

Split the document into overlapping chunks.

↓

## Step 4

Generate embeddings for each chunk.

↓

## Step 5

Generate an embedding for the user's question.

↓

## Step 6

Calculate cosine similarity between the question and document chunks.

↓

## Step 7

Retrieve the Top-K most relevant chunks.

↓

## Step 8

Send the retrieved chunks to the Groq LLM.

↓

## Step 9

Generate a grounded answer.

↓

## Step 10

Display

- AI-generated answer
- Retrieved chunks
- PDF page number
- Similarity score
- Similarity progress bar

---

# 📸 Screenshots

You can add screenshots here.

Example:

```
screenshots/

Home Page

Upload Document

Chat Interface

Retrieved Chunks

Page Number Display

Similarity Progress Bar
```

---

# 📊 Example Workflow

```
User uploads PDF
        │
        ▼
Extract Text
        │
        ▼
Chunk Document
        │
        ▼
Generate Embeddings
        │
        ▼
User Question
        │
        ▼
Question Embedding
        │
        ▼
Cosine Similarity Search
        │
        ▼
Top-K Retrieval
        │
        ▼
Groq LLM
        │
        ▼
Final Answer
```

---

# 📦 Dependencies

- streamlit
- numpy
- pdfplumber
- pypdf
- python-dotenv
- sentence-transformers
- groq

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

# 🌟 Future Enhancements

- 🟨 Highlight matched text
- 🔊 Voice output (Text-to-Speech)
- 🤖 Streaming responses
- 📥 Download chat as PDF
- 📥 Download chat as TXT
- 🌙 Dark mode
- 📈 Retrieval analytics
- 📚 Multi-document support
- 🖼️ OCR support for scanned PDFs
- 🔎 Hybrid Search (Semantic + Keyword)

---

# 👩‍💻 Author

**Vaishnavi H M**

Final Year BCA Student

AI & Machine Learning Enthusiast

---

# 📜 License

This project is created for educational and learning purposes.

Feel free to use, modify, and improve it.

---

# ⭐ Acknowledgements

- Streamlit
- Groq
- Sentence Transformers
- pdfplumber
- pypdf
- Python Community

---

## Thank You

If you found this project useful, consider giving it a ⭐ on GitHub.
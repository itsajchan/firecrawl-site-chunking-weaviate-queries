# 🚗 Car Rental Intelligence Engine

> *"Because nobody should have a bad experience with a rental car company... ever."*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Firecrawl](https://img.shields.io/badge/Firecrawl-Powered-orange.svg)](https://firecrawl.dev)
[![Weaviate](https://img.shields.io/badge/Weaviate-Vector%20DB-green.svg)](https://weaviate.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-Embeddings-purple.svg)](https://openai.com)

## 🎯 What This Does

This project creates an intelligent system that scrapes car rental reviews from the web, processes them into chunks, and stores them in a vector database, Weaviate, for lightning-fast semantic/hybrid search. Think of it as your personal car rental advisor that has read many reviews and can instantly answer questions like:

- *"What are the most common issues with rental car companies?"*
- *"How do customers rate the customer service at different locations?"*
- *"What should I watch out for when renting from a rental car company?"*

## 🏗️ Architecture

```
    A[🌐 Web Scraping] --> B[📝 Content Chunking]
    B --> C[🧠 Vector Embeddings]
    C --> D[💾 Weaviate Storage]
    D --> E[🔍 Semantic Search]
    E --> F[💬 Chat Interface]
```

## 🚀 Quick Start

### Prerequisites

1. **Firecrawl API Key** - Get yours at [firecrawl.dev](https://firecrawl.dev)
2. **Weaviate Cloud Instance** - Set up at [console.weaviate.cloud](https://console.weaviate.cloud)
3. **OpenAI API Key** - For embeddings at [platform.openai.com](https://platform.openai.com)

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd 4-firecrawl_scrape

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Update the API keys in each script:
- `0. firecrawl_example.py`: Set your Firecrawl API key
- `1. scrape_chunk_query.py`: Set Firecrawl, Weaviate, and OpenAI keys
- `2. weaviate_queries.py`: Set Weaviate and OpenAI keys

## 📁 Project Structure

### 🔥 `0. firecrawl_example.py`
**The Gentle Introduction**

A simple example showing how to scrape a TripAdvisor car rental review page using Firecrawl. Perfect for understanding the basics!

```python
# Example, scrapes this beauty:
# https://www.tripadvisor.co.nz/ShowUserReviews-g55711-d19346260-r944394581-SIXT_Rental_Car-Dallas_Texas.html
```

**What it does:**
- 🌐 Scrapes web content in both markdown and HTML formats
- 📄 Shows you the raw scraped data structure
- 🎯 Perfect starting point for understanding Firecrawl

---

### ⚡ `1. scrape_chunk_query.py`
**The Heavy Lifter**

This is where the magic happens! Scrapes content, intelligently chunks it, and stores it in Weaviate with semantic embeddings.

**Features:**
- 🕷️ **Smart Scraping**: Extracts markdown content from Firecrawl responses
- ✂️ **Dual Chunking Strategies**:
  - **Header-based**: Preserves document structure (great for organized content)
  - **Sentence-based**: Optimized for semantic search with configurable overlap
- 🧠 **Vector Storage**: Automatically generates embeddings and stores in Weaviate
- 📊 **Rich Metadata**: Tracks chunk types, word counts, and source information

**Chunking Methods:**
```python
# Method 1: Structure-preserving header chunks
header_chunks = chunk_markdown_by_headers(content, max_chunk_size=1000)

# Method 2: Semantic-optimized sentence chunks  
sentence_chunks = chunk_markdown_by_sentences(content, max_chunk_size=1000, overlap=100)
```

---

### 💬 `2. weaviate_queries.py`
**The Conversationalist**

An interactive chat interface that lets you query your scraped car rental data using natural language!

**Features:**
- 🗣️ **Interactive Chat**: Ask questions in plain English
- 🔍 **Semantic Search**: Finds relevant content using vector similarity
- 📈 **Relevance Scoring**: Shows how confident the system is in each answer
- 🎯 **Demo Mode**: Pre-built queries to showcase capabilities

**Usage:**
```bash
# Interactive mode
python "2. weaviate_queries.py"

# Demo mode
python "2. weaviate_queries.py" demo
```

## 🎮 Usage Examples

### Step 1: Test Basic Scraping
```bash
python "0. firecrawl_example.py"
```

### Step 2: Scrape, Chunk & Store
```bash
python "1. scrape_chunk_query.py"
```
This will:
- Scrape the TripAdvisor page
- Create both header-based and sentence-based chunks
- Store everything in your Weaviate instance
- Show you exactly what was processed

### Step 3: Query Your Data
```bash
python "2. weaviate_queries.py"
```

Then ask questions like:
- *"What are common complaints about car rentals?"*
- *"How is the customer service?"*
- *"What should I be careful about?"*

## 🛠️ Technical Details

### Chunking Strategies

**Header-Based Chunking** 📋
- Splits content by markdown headers (`#`, `##`, `###`)
- Preserves document hierarchy and structure
- Great for well-organized content like articles or documentation
- Each chunk includes header context and nesting level

**Sentence-Based Chunking** 🔄
- Splits by sentences with configurable overlap
- Optimized for semantic similarity search
- Prevents context loss at chunk boundaries
- Better for conversational AI and Q&A systems

### Vector Database Schema

```python
# Each chunk is stored with rich metadata:
{
    "content": "The actual text chunk",
    "chunk_type": "header" | "sentence",
    "word_count": 150,
    "char_count": 892,
    "header": "Customer Service Issues",  # For header chunks
    "level": 2,  # Header level
    "source_url": "https://..."
}
```

## 🎨 Customization

### Adjust Chunk Sizes
```python
# In scrape_chunk_query.py
header_chunks = chunk_markdown_by_headers(content, max_chunk_size=1500)  # Bigger chunks
sentence_chunks = chunk_markdown_by_sentences(content, max_chunk_size=800, overlap=150)  # More overlap
```

### Add New Data Sources
```python
# Just change the URL in scrape_chunk_query.py
scrape_status = app.scrape_url(
    'https://your-new-review-site.com/reviews',
    formats=['markdown', 'html']
)
```

### Customize Query Interface
```python
# In weaviate_queries.py, modify the search parameters
search_response = questions.query.near_text(
    query=user_query,
    limit=5,  # Get more results
    return_metadata=['score', 'distance']  # More metadata
)
```

## 🚨 Common Issues & Solutions

**"No markdown content found"**
- Check your Firecrawl API key
- Verify the target URL is accessible
- Some sites may block scraping

**"Weaviate connection failed"**
- Verify your Weaviate cluster URL and API key
- Check if your cluster is running
- Ensure OpenAI API key is valid for embeddings

**"Empty search results"**
- Make sure you've run step 1 to populate the database
- Try broader search terms
- Check if the collection name matches (`CarRentalChunks`)

## 🔮 Future Enhancements

- [ ] **Multi-site Scraping**: Scrape multiple review sites automatically
- [ ] **Sentiment Analysis**: Add emotion scoring to reviews
- [ ] **Company Comparison**: Side-by-side rental company analysis
- [ ] **Real-time Updates**: Periodic re-scraping for fresh data
- [ ] **Web Interface**: Beautiful dashboard for non-technical users
- [ ] **Export Features**: Generate reports and summaries

## 🤝 Contributing

Found a bug? Have an idea? Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this for your own car rental intelligence needs!

---

*Built with ❤️ and a healthy skepticism of car rental companies*
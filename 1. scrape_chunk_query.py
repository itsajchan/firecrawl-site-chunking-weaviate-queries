import re
from typing import List, Dict
from firecrawl import FirecrawlApp

import weaviate
from weaviate.classes.init import Auth
import weaviate.classes as wvc
import weaviate.classes.config as wc

def extract_markdown_from_scrape(scrape_result) -> str:
    """Extract markdown content from Firecrawl scrape result."""
    # Handle Firecrawl ScrapeResponse object
    if hasattr(scrape_result, 'markdown') and scrape_result.markdown:
        return scrape_result.markdown
    elif hasattr(scrape_result, 'data') and scrape_result.data and hasattr(scrape_result.data, 'markdown'):
        return scrape_result.data.markdown
    # Handle dict format
    elif isinstance(scrape_result, dict):
        if 'markdown' in scrape_result:
            return scrape_result['markdown']
        elif 'data' in scrape_result and 'markdown' in scrape_result['data']:
            return scrape_result['data']['markdown']
    
    # If no markdown found, check if we have HTML that we can convert
    html_content = None
    if hasattr(scrape_result, 'html') and scrape_result.html:
        html_content = scrape_result.html
    elif isinstance(scrape_result, dict) and 'html' in scrape_result:
        html_content = scrape_result['html']
    
    if html_content:
        # Basic HTML to markdown conversion for demonstration
        import re
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        # Convert basic HTML tags to markdown
        html_content = re.sub(r'<h([1-6])[^>]*>(.*?)</h[1-6]>', lambda m: '#' * int(m.group(1)) + ' ' + m.group(2), html_content)
        html_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', html_content)
        html_content = re.sub(r'<br[^>]*>', '\n', html_content)
        html_content = re.sub(r'<[^>]+>', '', html_content)  # Remove remaining HTML tags
        html_content = re.sub(r'\n\s*\n', '\n\n', html_content)  # Clean up extra newlines
        return html_content.strip()
    
    raise ValueError("No markdown or convertible HTML content found in scrape result")

def chunk_markdown_by_headers(markdown_content: str, max_chunk_size: int = 1000) -> List[Dict[str, str]]:
    """
    Chunk markdown content by headers while respecting max chunk size.
    Returns list of chunks with metadata.
    """
    chunks = []
    
    # Split by headers (# ## ### etc.)
    header_pattern = r'^(#{1,6})\s+(.+)$'
    lines = markdown_content.split('\n')
    
    current_chunk = ""
    current_header = ""
    current_level = 0
    
    for line in lines:
        header_match = re.match(header_pattern, line, re.MULTILINE)
        
        if header_match:
            # Save previous chunk if it exists
            if current_chunk.strip():
                chunks.append({
                    'content': current_chunk.strip(),
                    'header': current_header,
                    'level': current_level,
                    'word_count': len(current_chunk.split()),
                    'char_count': len(current_chunk)
                })
            
            # Start new chunk
            current_header = header_match.group(2)
            current_level = len(header_match.group(1))
            current_chunk = line + '\n'
        else:
            current_chunk += line + '\n'
            
            # Check if chunk is getting too large
            if len(current_chunk) > max_chunk_size:
                # Try to split at paragraph breaks
                paragraphs = current_chunk.split('\n\n')
                if len(paragraphs) > 1:
                    # Save all but the last paragraph
                    chunk_to_save = '\n\n'.join(paragraphs[:-1])
                    chunks.append({
                        'content': chunk_to_save.strip(),
                        'header': current_header,
                        'level': current_level,
                        'word_count': len(chunk_to_save.split()),
                        'char_count': len(chunk_to_save)
                    })
                    # Keep the last paragraph for the next chunk
                    current_chunk = paragraphs[-1] + '\n'
    
    # Add the final chunk
    if current_chunk.strip():
        chunks.append({
            'content': current_chunk.strip(),
            'header': current_header,
            'level': current_level,
            'word_count': len(current_chunk.split()),
            'char_count': len(current_chunk)
        })
    
    return chunks

def chunk_markdown_by_sentences(markdown_content: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[Dict[str, str]]:
    """
    Chunk markdown content by sentences with overlap.
    Better for semantic similarity in vector databases.
    """
    # Remove markdown formatting for sentence detection
    text_only = re.sub(r'[#*`_\[\]()]', '', markdown_content)
    
    # Split into sentences
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text_only)
    
    chunks = []
    current_chunk = ""
    
    i = 0
    while i < len(sentences):
        sentence = sentences[i].strip()
        
        # Add sentence if it fits
        if len(current_chunk + sentence) <= max_chunk_size:
            current_chunk += sentence + " "
            i += 1
        else:
            # Save current chunk
            if current_chunk.strip():
                chunks.append({
                    'content': current_chunk.strip(),
                    'word_count': len(current_chunk.split()),
                    'char_count': len(current_chunk),
                    'chunk_type': 'sentence_based'
                })
            
            # Start new chunk with overlap
            if overlap > 0 and chunks:
                # Get last few sentences for overlap
                overlap_words = current_chunk.split()[-overlap:]
                current_chunk = " ".join(overlap_words) + " "
            else:
                current_chunk = ""
            
            # Add current sentence if it's not too long by itself
            if len(sentence) <= max_chunk_size:
                current_chunk += sentence + " "
                i += 1
            else:
                # Split very long sentences by words
                words = sentence.split()
                word_chunk = ""
                for word in words:
                    if len(word_chunk + word) <= max_chunk_size:
                        word_chunk += word + " "
                    else:
                        if word_chunk.strip():
                            chunks.append({
                                'content': word_chunk.strip(),
                                'word_count': len(word_chunk.split()),
                                'char_count': len(word_chunk),
                                'chunk_type': 'word_based'
                            })
                        word_chunk = word + " "
                current_chunk = word_chunk
                i += 1
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append({
            'content': current_chunk.strip(),
            'word_count': len(current_chunk.split()),
            'char_count': len(current_chunk),
            'chunk_type': 'sentence_based'
        })
    
    return chunks

def process_scrape_data_for_vector_db():
    """Main function to process the scraped data and create chunks."""
    
    # Initialize Firecrawl (using the same setup as main.py)
    app = FirecrawlApp(api_key="fc-XXXX")
    
    # Scrape the website
    print("Scraping website...")
    scrape_status = app.scrape_url( 
        'https://community.ricksteves.com/travel-forum/italy/damage-to-rental-car-after-dropping-off-at-rome-from-sixt', 
        formats=['markdown', 'html']
    )
    
    # Extract markdown content
    try:
        markdown_content = extract_markdown_from_scrape(scrape_status)
        print(f"Extracted markdown content: {len(markdown_content)} characters")
        
        # Create chunks using both methods
        print("\nCreating header-based chunks...")
        header_chunks = chunk_markdown_by_headers(markdown_content, max_chunk_size=800)
        
        print("\nCreating sentence-based chunks...")
        sentence_chunks = chunk_markdown_by_sentences(markdown_content, max_chunk_size=800, overlap=50)

        return {
            'markdown_content': markdown_content,
            'header_chunks': header_chunks,
            'sentence_chunks': sentence_chunks
        }
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Scrape result attributes:", [attr for attr in dir(scrape_status) if not attr.startswith('_')])
        if hasattr(scrape_status, 'metadata'):
            print("Metadata:", scrape_status.metadata)
        return None

if __name__ == "__main__":
    result = process_scrape_data_for_vector_db()

    chunks = [chunk['content'] for chunk in result['sentence_chunks']]        

    # Best practice: store your credentials in environment variables
    weaviate_url = "XXX" # os.environ["WEAVIATE_URL"]
    weaviate_api_key = "XXXX" # os.environ["WEAVIATE_API_KEY"]
    openai_key="sk-proj-XXXX"
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(weaviate_api_key),
        headers = {
            "X-OpenAI-Api-Key": openai_key,
        }
    )

    print(client.is_ready())  # Should print: `True`


    # Ask user if they want to delete car rental collection
    if input("Do you want to delete and recreate the CarRentalChunks collection? (y/n): ") == 'y':
        client.collections.delete("CarRentalChunks")
        print("Deleted CarRentalChunks collection")

        questions = client.collections.create(
            name="CarRentalChunks",
            
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_weaviate(model="Snowflake/snowflake-arctic-embed-l-v2.0"),
            generative_config=wvc.config.Configure.Generative.openai(model="gpt-4o-mini"),
            properties=[
                wc.Property(name="source_url", data_type=wc.DataType.TEXT),
                wc.Property(name="content", data_type=wc.DataType.TEXT),
            ],
        )

        print("Created CarRentalChunks collection")
    
    with questions.batch.fixed_size(batch_size=200) as batch:
        for chunk in chunks:
            batch.add_object(
                {
                    "content": chunk,
                    "source_url": "https://community.ricksteves.com/travel-forum/italy/damage-to-rental-car-after-dropping-off-at-rome-from-sixt"
                }
            )
            if batch.number_errors > 10:
                print("Batch import stopped due to excessive errors.")
                break

    failed_objects = questions.batch.failed_objects
    if failed_objects:
        print(f"Number of failed imports: {len(failed_objects)}")
        print(f"First failed object: {failed_objects[0]}")

    client.close()  # Free up resources



import weaviate
from weaviate.classes.init import Auth

# Best practice: store your credentials in environment variables
weaviate_url = "XXX"# os.environ["WEAVIATE_URL"]
weaviate_api_key = "XXX" # os.environ["WEAVIATE_API_KEY"]
openai_key="sk-proj-XXX"

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers = {
        "X-OpenAI-Api-Key": openai_key,
    }
)

def chat_with_car_rental_data():
    """Interactive chat interface for querying car rental data."""
    questions = client.collections.get("CarRentalChunks")
    
    print("🚗 Car Rental Data Chat Interface")
    print("Ask questions about car rental experiences, issues, or advice!")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    while True:
        try:
            # Get user input
            user_query = input("\n❓ Your question: ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for chatting! Goodbye!")
                break
            
            if not user_query:
                print("Please enter a question.")
                continue
            
            print("\n🔍 Searching relevant information...")
            
            # Search for relevant chunks
            search_response = questions.query.near_text(
                query=user_query,
                limit=3,
                return_metadata=['score']
            )

            # print("Search response:")
            # print(search_response.objects)
            # print("----")

            if not search_response.objects:
                print("❌ No relevant information found. Try rephrasing your question.")
                continue
            
            # Generate response based on found chunks
            response = questions.generate.near_text(
                query=user_query,
                limit=3,
                grouped_task=f"Share similar stories back to the user based on the experience as defined by: --------- BEGIN USER QUERY --------- {user_query}. -------- END USER QUERY --------. Generate a response and include links if there are any relevant links."
            )
            
            print("\n🤖 Answer:")
            print(response.generated)
            
            # Show source information
            print("\n📚 Sources used:")
            for i, obj in enumerate(search_response.objects[:3], 1):
                content_preview = obj.properties['content'][:100] + "..." if len(obj.properties['content']) > 100 else obj.properties['content']
                score = obj.metadata.score if hasattr(obj.metadata, 'score') else 'N/A'
                print(f"  {i}. Score: {score:.3f} - {content_preview}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different question.")
    
    client.close()  # Free up resources

def demo_queries():
    """Run some demo queries to show the system capabilities."""
    questions = client.collections.get("CarRentalChunks")
    
    demo_questions = [
        "What are common issues with SIXT car rentals?",
        "How can I avoid damage charges when returning a rental car?",
        "What should I do if I find damage on my rental car?",
        "Are there any tips for dealing with car rental companies?"
    ]
    
    print("🚗 Car Rental Data - Demo Queries\n")
    
    for i, query in enumerate(demo_questions, 1):
        print(f"\n{i}. Question: {query}")
        print("   Answer: ", end="")
        
        try:
            response = questions.generate.near_text(
                query=query,
                limit=3,
                grouped_task=f"Based on the car rental experiences provided, answer: {query}"
            )
            print(response.generated)
        except Exception as e:
            print(f"Error generating response: {e}")
    
    client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_queries()
    else:
        chat_with_car_rental_data()


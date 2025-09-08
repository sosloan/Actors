#!/usr/bin/env python3
"""
ACTORS Embedding Demo
Demonstrate the embedding search capabilities
"""

import json
import time
from embedding_search import EmbeddingSearchEngine

def demo_embedding_search():
    """Demonstrate embedding search functionality"""
    print("🦞 ACTORS Embedding Search Demo")
    print("=" * 50)
    
    # Initialize search engine
    print("🔄 Initializing search engine...")
    engine = EmbeddingSearchEngine("md_embeddings.jsonl")
    engine.load_embeddings()
    
    # Show statistics
    print("\n📊 Embedding Statistics:")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Demo 1: Search by text
    print("\n🔍 Demo 1: Text Search")
    print("-" * 30)
    
    queries = [
        "financial trading algorithms",
        "distributed agents",
        "machine learning pipeline",
        "options trading",
        "risk management"
    ]
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        start_time = time.time()
        results = engine.search_by_text(query, 3)
        search_time = time.time() - start_time
        
        if results:
            print(f"  Found {len(results)} results in {search_time:.3f}s:")
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                similarity = result['similarity']
                filename = metadata['path'].split('/')[-1] if '/' in metadata['path'] else metadata['path']
                print(f"    {i}. {filename} (similarity: {similarity:.4f})")
        else:
            print("  No results found")
    
    # Demo 2: Find similar embeddings
    print("\n🔍 Demo 2: Similar Embeddings")
    print("-" * 30)
    
    # Get a random embedding ID
    if engine.embeddings_data:
        sample_id = engine.embeddings_data[0]['id']
        print(f"Finding embeddings similar to: {sample_id}")
        
        start_time = time.time()
        similar_results = engine.find_similar_to_id(sample_id, 5)
        search_time = time.time() - start_time
        
        if similar_results:
            print(f"  Found {len(similar_results)} similar embeddings in {search_time:.3f}s:")
            for i, result in enumerate(similar_results, 1):
                metadata = result['metadata']
                similarity = result['similarity']
                filename = metadata['path'].split('/')[-1] if '/' in metadata['path'] else metadata['path']
                print(f"    {i}. {filename} (similarity: {similarity:.4f})")
        else:
            print("  No similar embeddings found")
    
    # Demo 3: Clustering
    print("\n🎯 Demo 3: Embedding Clustering")
    print("-" * 30)
    
    print("Clustering embeddings into 5 groups...")
    start_time = time.time()
    clusters = engine.cluster_embeddings(5)
    cluster_time = time.time() - start_time
    
    if clusters:
        print(f"  Clustering completed in {cluster_time:.3f}s:")
        for cluster_id, items in clusters['clusters'].items():
            print(f"    Cluster {cluster_id}: {len(items)} embeddings")
            # Show sample files from each cluster
            sample_files = []
            for item in items[:3]:
                filename = item['metadata']['path'].split('/')[-1] if '/' in item['metadata']['path'] else item['metadata']['path']
                sample_files.append(filename)
            print(f"      Sample files: {', '.join(sample_files)}")
    
    # Demo 4: Content recommendations
    print("\n💡 Demo 4: Content Recommendations")
    print("-" * 30)
    
    recommendation_queries = [
        "derivatives trading",
        "portfolio optimization",
        "DeFi protocols"
    ]
    
    for query in recommendation_queries:
        print(f"\nRecommendations for: '{query}'")
        results = engine.search_by_text(query, 10)
        
        if results:
            # Group by file and get best match per file
            file_scores = {}
            for result in results:
                path = result['metadata']['path']
                filename = path.split('/')[-1] if '/' in path else path
                similarity = result['similarity']
                
                if filename not in file_scores or similarity > file_scores[filename]['similarity']:
                    file_scores[filename] = {
                        'path': path,
                        'similarity': similarity
                    }
            
            # Sort by similarity and take top 3
            recommendations = sorted(file_scores.values(), key=lambda x: x['similarity'], reverse=True)[:3]
            
            print(f"  Top {len(recommendations)} recommended files:")
            for i, rec in enumerate(recommendations, 1):
                filename = rec['path'].split('/')[-1] if '/' in rec['path'] else rec['path']
                print(f"    {i}. {filename} (relevance: {rec['similarity']:.4f})")
    
    print("\n🎉 Demo completed successfully!")
    print("\nThe ACTORS embedding system provides:")
    print("  • Semantic search across 13,570+ document chunks")
    print("  • Similarity-based content recommendations")
    print("  • Clustering for content organization")
    print("  • Fast vector similarity calculations")
    print("  • Integration with financial trading concepts")

if __name__ == "__main__":
    demo_embedding_search()


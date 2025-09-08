#!/usr/bin/env python3
"""
ACTORS Embedding Search System
Advanced semantic search using the generated embeddings
"""

import json
import numpy as np
from typing import List, Dict, Tuple, Optional
import argparse
from pathlib import Path
import time

class EmbeddingSearchEngine:
    def __init__(self, embeddings_file: str):
        """Initialize the embedding search engine"""
        self.embeddings_file = embeddings_file
        self.embeddings_data = []
        self.embeddings_matrix = None
        self.metadata = []
        
    def load_embeddings(self):
        """Load embeddings from JSONL file"""
        print(f"🔄 Loading embeddings from {self.embeddings_file}...")
        start_time = time.time()
        
        with open(self.embeddings_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        data = json.loads(line.strip())
                        self.embeddings_data.append(data)
                        self.metadata.append({
                            'id': data.get('id', f'line_{line_num}'),
                            'path': data.get('path', ''),
                            'chunk_index': data.get('chunk_index', 0),
                            'text_sha256': data.get('text_sha256', '')
                        })
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Skipping malformed line {line_num}: {e}")
                        continue
        
        # Convert to numpy matrix for efficient computation
        embeddings_list = [data['embedding'] for data in self.embeddings_data]
        self.embeddings_matrix = np.array(embeddings_list)
        
        load_time = time.time() - start_time
        print(f"✅ Loaded {len(self.embeddings_data)} embeddings in {load_time:.2f}s")
        print(f"📊 Embedding dimension: {self.embeddings_matrix.shape[1]}")
        
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def search(self, query_embedding: List[float], top_k: int = 10) -> List[Dict]:
        """Search for similar embeddings"""
        if self.embeddings_matrix is None:
            raise ValueError("Embeddings not loaded. Call load_embeddings() first.")
        
        query_vec = np.array(query_embedding)
        similarities = []
        
        # Calculate similarities
        for i, embedding in enumerate(self.embeddings_matrix):
            similarity = self.cosine_similarity(query_vec, embedding)
            similarities.append({
                'index': i,
                'similarity': similarity,
                'metadata': self.metadata[i],
                'embedding_data': self.embeddings_data[i]
            })
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def search_by_text(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """Search by text content (requires OpenAI API)"""
        try:
            from openai import OpenAI
            client = OpenAI()
            
            # Generate embedding for query text
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=query_text
            )
            query_embedding = response.data[0].embedding
            
            return self.search(query_embedding, top_k)
            
        except ImportError:
            print("❌ OpenAI library not available. Install with: pip install openai")
            return []
        except Exception as e:
            print(f"❌ Error generating query embedding: {e}")
            return []
    
    def get_embedding_by_id(self, embedding_id: str) -> Optional[Dict]:
        """Get embedding by ID"""
        for i, data in enumerate(self.embeddings_data):
            if data.get('id') == embedding_id:
                return {
                    'index': i,
                    'metadata': self.metadata[i],
                    'embedding_data': data
                }
        return None
    
    def find_similar_to_id(self, embedding_id: str, top_k: int = 10) -> List[Dict]:
        """Find embeddings similar to a specific embedding by ID"""
        target_embedding = self.get_embedding_by_id(embedding_id)
        if target_embedding is None:
            print(f"❌ Embedding with ID '{embedding_id}' not found")
            return []
        
        target_vec = np.array(target_embedding['embedding_data']['embedding'])
        return self.search(target_vec, top_k)
    
    def cluster_embeddings(self, n_clusters: int = 10) -> Dict:
        """Cluster embeddings using K-means"""
        try:
            from sklearn.cluster import KMeans
            from sklearn.decomposition import PCA
            
            print(f"🔄 Clustering {len(self.embeddings_data)} embeddings into {n_clusters} clusters...")
            
            # Reduce dimensionality for visualization
            pca = PCA(n_components=2)
            embeddings_2d = pca.fit_transform(self.embeddings_matrix)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(self.embeddings_matrix)
            
            # Organize results
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append({
                    'index': i,
                    'metadata': self.metadata[i],
                    'coordinates_2d': embeddings_2d[i].tolist()
                })
            
            return {
                'clusters': clusters,
                'cluster_centers': kmeans.cluster_centers_.tolist(),
                'pca_components': pca.components_.tolist(),
                'explained_variance_ratio': pca.explained_variance_ratio_.tolist()
            }
            
        except ImportError:
            print("❌ scikit-learn not available. Install with: pip install scikit-learn")
            return {}
        except Exception as e:
            print(f"❌ Error during clustering: {e}")
            return {}
    
    def get_statistics(self) -> Dict:
        """Get statistics about the embeddings"""
        if self.embeddings_matrix is None:
            return {}
        
        return {
            'total_embeddings': len(self.embeddings_data),
            'embedding_dimension': self.embeddings_matrix.shape[1],
            'unique_paths': len(set(meta['path'] for meta in self.metadata)),
            'mean_embedding_norm': float(np.mean(np.linalg.norm(self.embeddings_matrix, axis=1))),
            'std_embedding_norm': float(np.std(np.linalg.norm(self.embeddings_matrix, axis=1))),
            'min_embedding_value': float(np.min(self.embeddings_matrix)),
            'max_embedding_value': float(np.max(self.embeddings_matrix))
        }

def main():
    parser = argparse.ArgumentParser(description="ACTORS Embedding Search System")
    parser.add_argument("--embeddings", default="md_embeddings.jsonl", help="Path to embeddings file")
    parser.add_argument("--query", help="Text query to search for")
    parser.add_argument("--query-id", help="ID of embedding to find similar ones")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results to return")
    parser.add_argument("--cluster", type=int, help="Number of clusters for clustering analysis")
    parser.add_argument("--stats", action="store_true", help="Show embedding statistics")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    
    args = parser.parse_args()
    
    # Initialize search engine
    engine = EmbeddingSearchEngine(args.embeddings)
    engine.load_embeddings()
    
    if args.stats:
        stats = engine.get_statistics()
        print("\n📊 Embedding Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    if args.cluster:
        clusters = engine.cluster_embeddings(args.cluster)
        if clusters:
            print(f"\n🎯 Found {len(clusters['clusters'])} clusters:")
            for cluster_id, items in clusters['clusters'].items():
                print(f"  Cluster {cluster_id}: {len(items)} embeddings")
                # Show top 3 items in each cluster
                for item in items[:3]:
                    path = item['metadata']['path']
                    print(f"    - {Path(path).name}")
    
    if args.query:
        print(f"\n🔍 Searching for: '{args.query}'")
        results = engine.search_by_text(args.query, args.top_k)
        
        if results:
            print(f"\n📋 Top {len(results)} results:")
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                similarity = result['similarity']
                path = Path(metadata['path']).name
                print(f"  {i}. {path} (similarity: {similarity:.4f})")
                print(f"     ID: {metadata['id']}")
                print(f"     Chunk: {metadata['chunk_index']}")
        else:
            print("❌ No results found")
    
    if args.query_id:
        print(f"\n🔍 Finding similar to ID: '{args.query_id}'")
        results = engine.find_similar_to_id(args.query_id, args.top_k)
        
        if results:
            print(f"\n📋 Top {len(results)} similar embeddings:")
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                similarity = result['similarity']
                path = Path(metadata['path']).name
                print(f"  {i}. {path} (similarity: {similarity:.4f})")
                print(f"     ID: {metadata['id']}")
        else:
            print("❌ No similar embeddings found")
    
    if args.interactive:
        print("\n🎮 Interactive Mode - Type 'help' for commands, 'quit' to exit")
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    print("Commands:")
                    print("  search <text> - Search for similar embeddings")
                    print("  similar <id> - Find similar to embedding ID")
                    print("  stats - Show statistics")
                    print("  cluster <n> - Cluster embeddings")
                    print("  quit - Exit")
                elif command.startswith('search '):
                    query = command[7:].strip()
                    results = engine.search_by_text(query, 5)
                    if results:
                        print(f"\n📋 Results for '{query}':")
                        for i, result in enumerate(results, 1):
                            metadata = result['metadata']
                            similarity = result['similarity']
                            path = Path(metadata['path']).name
                            print(f"  {i}. {path} (similarity: {similarity:.4f})")
                    else:
                        print("❌ No results found")
                elif command.startswith('similar '):
                    query_id = command[8:].strip()
                    results = engine.find_similar_to_id(query_id, 5)
                    if results:
                        print(f"\n📋 Similar to '{query_id}':")
                        for i, result in enumerate(results, 1):
                            metadata = result['metadata']
                            similarity = result['similarity']
                            path = Path(metadata['path']).name
                            print(f"  {i}. {path} (similarity: {similarity:.4f})")
                    else:
                        print("❌ No similar embeddings found")
                elif command.lower() == 'stats':
                    stats = engine.get_statistics()
                    print("\n📊 Statistics:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                elif command.startswith('cluster '):
                    try:
                        n_clusters = int(command[8:].strip())
                        clusters = engine.cluster_embeddings(n_clusters)
                        if clusters:
                            print(f"\n🎯 {n_clusters} clusters found:")
                            for cluster_id, items in clusters['clusters'].items():
                                print(f"  Cluster {cluster_id}: {len(items)} embeddings")
                    except ValueError:
                        print("❌ Invalid number of clusters")
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()

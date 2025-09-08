#!/usr/bin/env python3
"""
ACTORS Embedding API Server
RESTful API for semantic search and embedding operations with ML integration
"""

import json
import numpy as np
from typing import List, Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from pathlib import Path
import logging
import asyncio
from embedding_search import EmbeddingSearchEngine
from ml_pipeline_integration import MLPipelineManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global instances
search_engine = None
ml_pipeline = None

def initialize_systems():
    """Initialize the global systems"""
    global search_engine, ml_pipeline
    success_count = 0
    
    # Initialize search engine
    try:
        search_engine = EmbeddingSearchEngine("md_embeddings.jsonl")
        search_engine.load_embeddings()
        logger.info("✅ Embedding search engine initialized successfully")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to initialize search engine: {e}")
    
    # Initialize ML pipeline
    try:
        ml_pipeline = MLPipelineManager()
        asyncio.run(ml_pipeline.initialize())
        logger.info("✅ ML pipeline initialized successfully")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to initialize ML pipeline: {e}")
    
    return success_count == 2

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ACTORS Embedding API with ML Integration',
        'timestamp': time.time(),
        'embeddings_loaded': search_engine is not None,
        'ml_pipeline_active': ml_pipeline is not None
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get embedding statistics"""
    if search_engine is None:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    stats = search_engine.get_statistics()
    return jsonify(stats)

@app.route('/search', methods=['POST'])
def search_embeddings():
    """Search embeddings by text query"""
    if search_engine is None:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"🔍 Searching for: '{query}' (top_k={top_k})")
        start_time = time.time()
        
        results = search_engine.search_by_text(query, top_k)
        
        search_time = time.time() - start_time
        
        # Format results
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata['id'],
                'path': metadata['path'],
                'chunk_index': metadata['chunk_index'],
                'similarity': result['similarity'],
                'filename': Path(metadata['path']).name
            })
        
        return jsonify({
            'query': query,
            'results': formatted_results,
            'total_results': len(formatted_results),
            'search_time_ms': round(search_time * 1000, 2)
        })
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/similar/<embedding_id>', methods=['GET'])
def find_similar(embedding_id):
    """Find embeddings similar to a specific embedding ID"""
    if search_engine is None:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    try:
        top_k = request.args.get('top_k', 10, type=int)
        
        logger.info(f"🔍 Finding similar to ID: '{embedding_id}' (top_k={top_k})")
        start_time = time.time()
        
        results = search_engine.find_similar_to_id(embedding_id, top_k)
        
        search_time = time.time() - start_time
        
        # Format results
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata['id'],
                'path': metadata['path'],
                'chunk_index': metadata['chunk_index'],
                'similarity': result['similarity'],
                'filename': Path(metadata['path']).name
            })
        
        return jsonify({
            'target_id': embedding_id,
            'results': formatted_results,
            'total_results': len(formatted_results),
            'search_time_ms': round(search_time * 1000, 2)
        })
        
    except Exception as e:
        logger.error(f"❌ Similar search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/embedding/<embedding_id>', methods=['GET'])
def get_embedding(embedding_id):
    """Get embedding by ID"""
    if search_engine is None:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    try:
        embedding_data = search_engine.get_embedding_by_id(embedding_id)
        
        if embedding_data is None:
            return jsonify({'error': f'Embedding with ID "{embedding_id}" not found'}), 404
        
        return jsonify({
            'id': embedding_data['metadata']['id'],
            'path': embedding_data['metadata']['path'],
            'chunk_index': embedding_data['metadata']['chunk_index'],
            'text_sha256': embedding_data['metadata']['text_sha256'],
            'embedding_dimension': len(embedding_data['embedding_data']['embedding'])
        })
        
    except Exception as e:
        logger.error(f"❌ Get embedding error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/cluster', methods=['POST'])
def cluster_embeddings():
    """Cluster embeddings"""
    if search_engine is None:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    try:
        data = request.get_json()
        n_clusters = data.get('n_clusters', 10)
        
        logger.info(f"🎯 Clustering embeddings into {n_clusters} clusters")
        start_time = time.time()
        
        clusters = search_engine.cluster_embeddings(n_clusters)
        
        cluster_time = time.time() - start_time
        
        if not clusters:
            return jsonify({'error': 'Clustering failed'}), 500
        
        # Format cluster results
        formatted_clusters = {}
        for cluster_id, items in clusters['clusters'].items():
            formatted_clusters[str(cluster_id)] = {
                'size': len(items),
                'sample_files': [Path(item['metadata']['path']).name for item in items[:5]]
            }
        
        return jsonify({
            'n_clusters': n_clusters,
            'clusters': formatted_clusters,
            'cluster_time_ms': round(cluster_time * 1000, 2),
            'explained_variance_ratio': clusters.get('explained_variance_ratio', [])
        })
        
    except Exception as e:
        logger.error(f"❌ Clustering error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Get content recommendations based on query"""
    if search_engine is None:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"💡 Getting recommendations for: '{query}'")
        
        # Get search results
        results = search_engine.search_by_text(query, top_k * 2)  # Get more for filtering
        
        # Group by file and get best match per file
        file_scores = {}
        for result in results:
            path = result['metadata']['path']
            filename = Path(path).name
            similarity = result['similarity']
            
            if filename not in file_scores or similarity > file_scores[filename]['similarity']:
                file_scores[filename] = {
                    'path': path,
                    'similarity': similarity,
                    'id': result['metadata']['id']
                }
        
        # Sort by similarity and take top_k
        recommendations = sorted(file_scores.values(), key=lambda x: x['similarity'], reverse=True)[:top_k]
        
        return jsonify({
            'query': query,
            'recommendations': recommendations,
            'total_recommendations': len(recommendations)
        })
        
    except Exception as e:
        logger.error(f"❌ Recommendations error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/explore', methods=['GET'])
def explore_embeddings():
    """Explore embeddings with random samples"""
    if search_engine is None:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Get random sample of embeddings
        import random
        sample_indices = random.sample(range(len(search_engine.embeddings_data)), min(limit, len(search_engine.embeddings_data)))
        
        samples = []
        for idx in sample_indices:
            metadata = search_engine.metadata[idx]
            samples.append({
                'id': metadata['id'],
                'path': metadata['path'],
                'chunk_index': metadata['chunk_index'],
                'filename': Path(metadata['path']).name
            })
        
        return jsonify({
            'samples': samples,
            'total_embeddings': len(search_engine.embeddings_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Explore error: {e}")
        return jsonify({'error': str(e)}), 500

async def ml_enhanced_search():
    """ML-enhanced semantic search with intelligent ranking"""
    if search_engine is None:
        return jsonify({'error': 'Search engine not initialized'}), 500
    if ml_pipeline is None:
        return jsonify({'error': 'ML pipeline not initialized'}), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 10)
        ml_enhancement = data.get('ml_enhancement', True)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"🤖 ML-enhanced search for: '{query}' (top_k={top_k})")
        start_time = time.time()
        
        # Get base search results
        results = search_engine.search_by_text(query, top_k * 2)  # Get more for ML filtering
        
        if ml_enhancement and ml_pipeline:
            # Apply ML enhancement to results
            enhanced_results = await _enhance_search_results_with_ml(query, results, top_k)
        else:
            enhanced_results = results[:top_k]
        
        search_time = time.time() - start_time
        
        # Format results
        formatted_results = []
        for result in enhanced_results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata['id'],
                'path': metadata['path'],
                'chunk_index': metadata['chunk_index'],
                'similarity': result['similarity'],
                'filename': Path(metadata['path']).name,
                'ml_enhanced': ml_enhancement
            })
        
        return jsonify({
            'query': query,
            'results': formatted_results,
            'total_results': len(formatted_results),
            'search_time_ms': round(search_time * 1000, 2),
            'ml_enhanced': ml_enhancement
        })
        
    except Exception as e:
        logger.error(f"❌ ML-enhanced search error: {e}")
        return jsonify({'error': str(e)}), 500

async def _enhance_search_results_with_ml(query: str, results: List[Dict], top_k: int) -> List[Dict]:
    """Enhance search results using ML pipeline"""
    try:
        # Create mock transcription for ML processing
        from speech_to_trading_connector import AudioTranscription, SentimentAnalysis, AudioSource
        from datetime import datetime
        
        # Create transcription object
        transcription = AudioTranscription(
            text=query,
            confidence=0.95,
            duration=1.0,
            source=AudioSource.FINANCIAL_NEWS,
            timestamp=datetime.now(),
            entities=[],
            sentiment=SentimentAnalysis(
                overall_sentiment=0.0,
                confidence=0.8,
                key_phrases=[],
                market_impact=0.1
            )
        )
        
        # Get ML predictions
        ml_predictions = await ml_pipeline._generate_ml_predictions(None, transcription)
        
        # Enhance results based on ML insights
        enhanced_results = []
        for result in results:
            # Apply ML-based scoring
            ml_score = _calculate_ml_relevance_score(result, ml_predictions)
            result['ml_score'] = ml_score
            result['enhanced_similarity'] = result['similarity'] * (1 + ml_score * 0.2)
            enhanced_results.append(result)
        
        # Sort by enhanced similarity and return top_k
        enhanced_results.sort(key=lambda x: x['enhanced_similarity'], reverse=True)
        return enhanced_results[:top_k]
        
    except Exception as e:
        logger.error(f"❌ ML enhancement error: {e}")
        return results[:top_k]

def _calculate_ml_relevance_score(result: Dict, ml_predictions: List) -> float:
    """Calculate ML-based relevance score for search result"""
    try:
        # Simple ML scoring based on content analysis
        metadata = result['metadata']
        path = metadata['path'].lower()
        
        # Score based on file type and content
        score = 0.0
        
        # Financial content gets higher score
        if any(keyword in path for keyword in ['financial', 'trading', 'investment', 'portfolio']):
            score += 0.3
        
        # Technical content gets medium score
        if any(keyword in path for keyword in ['technical', 'analysis', 'strategy']):
            score += 0.2
        
        # Documentation gets lower score
        if any(keyword in path for keyword in ['readme', 'doc', 'guide']):
            score += 0.1
        
        return min(score, 1.0)
        
    except Exception as e:
        logger.error(f"❌ ML scoring error: {e}")
        return 0.0

async def get_ml_status():
    """Get ML pipeline status"""
    if ml_pipeline is None:
        return jsonify({'error': 'ML pipeline not initialized'}), 500
    
    try:
        health = await ml_pipeline.get_pipeline_health()
        return jsonify(health)
    except Exception as e:
        logger.error(f"❌ ML status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Async route handler wrapper
def async_route(f):
    """Wrapper for async routes"""
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    wrapper.__name__ = f.__name__  # Preserve function name
    return wrapper

# Apply async wrapper to async routes
app.route('/ml/search', methods=['POST'])(async_route(ml_enhanced_search))
app.route('/ml/status', methods=['GET'])(async_route(get_ml_status))

if __name__ == '__main__':
    print("🚀 Starting ACTORS Embedding API Server with ML Integration...")
    
    # Initialize systems
    if not initialize_systems():
        print("❌ Failed to initialize all systems. Some features may not be available.")
    
    print("✅ Systems initialized successfully")
    print("📊 Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /stats - Embedding statistics")
    print("  POST /search - Search by text query")
    print("  GET  /similar/<id> - Find similar embeddings")
    print("  GET  /embedding/<id> - Get embedding by ID")
    print("  POST /cluster - Cluster embeddings")
    print("  POST /recommendations - Get content recommendations")
    print("  GET  /explore - Explore random embeddings")
    print("")
    print("  🤖 ML-Enhanced Endpoints:")
    print("  POST /ml/search - ML-enhanced semantic search")
    print("  GET  /ml/status - ML pipeline status")
    
    # Start the server
    app.run(host='0.0.0.0', port=5001, debug=True)

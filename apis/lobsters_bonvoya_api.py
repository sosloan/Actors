#!/usr/bin/env python3
"""
🦞 Lobsters Bonvoyå API Server
RESTful API for travel optimization and financial integration
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Import our Lobsters Bonvoyå system
from lobsters_bonvoya import (
    LobstersBonvoyaSystem, 
    TravelPreferences, 
    TravelClass, 
    AccommodationType, 
    TravelPurpose
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global system instance
bonvoya_system = None

def initialize_bonvoya_system():
    """Initialize the global Lobsters Bonvoyå system"""
    global bonvoya_system
    try:
        bonvoya_system = LobstersBonvoyaSystem()
        logger.info("✅ Lobsters Bonvoyå system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize Bonvoyå system: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Lobsters Bonvoyå API',
        'timestamp': time.time(),
        'system_initialized': bonvoya_system is not None
    })

@app.route('/api/travel/plan', methods=['POST'])
async def create_travel_plan():
    """Create optimized travel plan"""
    if bonvoya_system is None:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        data = request.get_json()
        
        # Extract travel preferences
        preferences_data = data.get('preferences', {})
        preferences = TravelPreferences(
            budget_range=(
                preferences_data.get('budget_min', 2000),
                preferences_data.get('budget_max', 4000)
            ),
            travel_class=TravelClass(preferences_data.get('travel_class', 'economy')),
            accommodation_type=AccommodationType(preferences_data.get('accommodation_type', 'boutique_hotel')),
            purpose=TravelPurpose(preferences_data.get('purpose', 'fire_optimization')),
            duration_days=preferences_data.get('duration_days', 7),
            group_size=preferences_data.get('group_size', 2),
            dietary_restrictions=preferences_data.get('dietary_restrictions', []),
            accessibility_needs=preferences_data.get('accessibility_needs', []),
            interests=preferences_data.get('interests', []),
            risk_tolerance=preferences_data.get('risk_tolerance', 0.7),
            luxury_preference=preferences_data.get('luxury_preference', 0.3),
            adventure_preference=preferences_data.get('adventure_preference', 0.6),
            cultural_preference=preferences_data.get('cultural_preference', 0.8)
        )
        
        departure_location = data.get('departure_location', 'San Francisco')
        financial_profile = data.get('financial_profile', {})
        user_id = data.get('user_id', f'user_{int(time.time())}')
        
        logger.info(f"🦞 Creating travel plan for user {user_id}")
        logger.info(f"   Purpose: {preferences.purpose.value}")
        logger.info(f"   Budget: ${preferences.budget_range[0]:,.0f} - ${preferences.budget_range[1]:,.0f}")
        
        # Create travel plan
        result = await bonvoya_system.create_travel_plan(
            user_id=user_id,
            preferences=preferences,
            departure_location=departure_location,
            financial_profile=financial_profile
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Travel plan creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/travel/recommendations/<user_id>', methods=['GET'])
async def get_travel_recommendations(user_id):
    """Get personalized travel recommendations"""
    if bonvoya_system is None:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        recommendation_type = request.args.get('type', 'personalized')
        
        logger.info(f"💡 Getting recommendations for user {user_id}")
        
        recommendations = await bonvoya_system.get_travel_recommendations(
            user_id=user_id,
            recommendation_type=recommendation_type
        )
        
        return jsonify(recommendations)
        
    except Exception as e:
        logger.error(f"❌ Recommendations error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/travel/destinations', methods=['GET'])
def get_destinations():
    """Get available destinations"""
    if bonvoya_system is None:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        destinations = []
        for dest in bonvoya_system.travel_agent.destinations_db.values():
            destinations.append({
                'id': dest.id,
                'name': dest.name,
                'country': dest.country,
                'continent': dest.continent,
                'coordinates': dest.coordinates,
                'climate': dest.climate,
                'cost_index': dest.cost_index,
                'safety_score': dest.safety_score,
                'cultural_richness': dest.cultural_richness,
                'adventure_score': dest.adventure_score,
                'luxury_score': dest.luxury_score,
                'fire_friendly': dest.fire_friendly,
                'visa_requirements': dest.visa_requirements,
                'best_seasons': dest.best_seasons
            })
        
        return jsonify({
            'destinations': destinations,
            'total_count': len(destinations)
        })
        
    except Exception as e:
        logger.error(f"❌ Destinations error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial/optimize', methods=['POST'])
async def optimize_travel_finances():
    """Optimize travel finances"""
    if bonvoya_system is None:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        data = request.get_json()
        
        # This would typically require a full itinerary object
        # For demo purposes, we'll create a mock optimization
        travel_cost = data.get('travel_cost', 3000)
        financial_profile = data.get('financial_profile', {})
        
        logger.info(f"💰 Optimizing finances for travel cost: ${travel_cost:,.0f}")
        
        # Simulate financial optimization
        optimization_result = {
            'budget_allocation': {
                'allocation_method': 'investment_portfolio',
                'amount': travel_cost,
                'savings': travel_cost * 0.05,
                'recommendation': 'Use investment portfolio for optimal financial impact'
            },
            'points_optimization': {
                'flight_savings': travel_cost * 0.1,
                'accommodation_savings': travel_cost * 0.05,
                'total_savings': travel_cost * 0.15,
                'points_used': 20000,
                'miles_used': 25000,
                'recommendation': f'Save ${travel_cost * 0.15:.0f} using points and miles'
            },
            'tax_optimization': {
                'deductible_amount': travel_cost * 0.8 if financial_profile.get('is_business_travel') else 0,
                'tax_savings': travel_cost * 0.8 * financial_profile.get('tax_bracket', 0.25) if financial_profile.get('is_business_travel') else 0,
                'strategy': 'business_deduction' if financial_profile.get('is_business_travel') else 'personal_travel',
                'recommendation': 'Consider business travel for tax benefits' if not financial_profile.get('is_business_travel') else f'Save ${travel_cost * 0.8 * financial_profile.get("tax_bracket", 0.25):.0f} through business travel deductions'
            },
            'total_savings': travel_cost * 0.2
        }
        
        return jsonify(optimization_result)
        
    except Exception as e:
        logger.error(f"❌ Financial optimization error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    if bonvoya_system is None:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        stats = bonvoya_system.get_system_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"❌ Stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/travel/purposes', methods=['GET'])
def get_travel_purposes():
    """Get available travel purposes"""
    return jsonify({
        'purposes': [
            {'value': 'fire_optimization', 'label': 'FIRE Optimization', 'description': 'Travel smart for financial independence', 'emoji': '🔥'},
            {'value': 'luxury', 'label': 'Luxury Experience', 'description': 'Premium travel with maximum comfort', 'emoji': '💎'},
            {'value': 'adventure', 'label': 'Adventure', 'description': 'Thrilling experiences in nature', 'emoji': '🏔️'},
            {'value': 'cultural', 'label': 'Cultural', 'description': 'Rich cultural experiences', 'emoji': '🏛️'},
            {'value': 'business', 'label': 'Business', 'description': 'Professional travel with tax benefits', 'emoji': '💼'},
            {'value': 'wellness', 'label': 'Wellness', 'description': 'Health and relaxation focused', 'emoji': '🧘'},
            {'value': 'budget', 'label': 'Budget', 'description': 'Maximum value for minimum cost', 'emoji': '💰'}
        ]
    })

@app.route('/api/travel/classes', methods=['GET'])
def get_travel_classes():
    """Get available travel classes"""
    return jsonify({
        'classes': [
            {'value': 'economy', 'label': 'Economy', 'description': 'Standard seating', 'price_multiplier': 1.0},
            {'value': 'premium_economy', 'label': 'Premium Economy', 'description': 'Enhanced comfort', 'price_multiplier': 1.5},
            {'value': 'business', 'label': 'Business', 'description': 'Premium service', 'price_multiplier': 3.0},
            {'value': 'first', 'label': 'First Class', 'description': 'Luxury experience', 'price_multiplier': 5.0},
            {'value': 'private', 'label': 'Private Jet', 'description': 'Ultimate luxury', 'price_multiplier': 20.0}
        ]
    })

@app.route('/api/accommodation/types', methods=['GET'])
def get_accommodation_types():
    """Get available accommodation types"""
    return jsonify({
        'types': [
            {'value': 'hostel', 'label': 'Hostel', 'description': 'Budget-friendly shared accommodation', 'price_multiplier': 0.3},
            {'value': 'budget_hotel', 'label': 'Budget Hotel', 'description': 'Affordable private rooms', 'price_multiplier': 0.6},
            {'value': 'boutique_hotel', 'label': 'Boutique Hotel', 'description': 'Unique, personalized experience', 'price_multiplier': 1.2},
            {'value': 'luxury_hotel', 'label': 'Luxury Hotel', 'description': 'Premium amenities and service', 'price_multiplier': 2.0},
            {'value': 'resort', 'label': 'Resort', 'description': 'All-inclusive luxury experience', 'price_multiplier': 2.5},
            {'value': 'villa', 'label': 'Villa', 'description': 'Private luxury accommodation', 'price_multiplier': 3.0},
            {'value': 'private_island', 'label': 'Private Island', 'description': 'Ultimate exclusivity', 'price_multiplier': 10.0}
        ]
    })

@app.route('/api/demo/fire-travel', methods=['GET'])
async def demo_fire_travel():
    """Demo FIRE optimization travel"""
    if bonvoya_system is None:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        # Create FIRE travel preferences
        preferences = TravelPreferences(
            budget_range=(2000, 4000),
            travel_class=TravelClass.ECONOMY,
            accommodation_type=AccommodationType.BOUTIQUE_HOTEL,
            purpose=TravelPurpose.FIRE_OPTIMIZATION,
            duration_days=7,
            group_size=2,
            dietary_restrictions=[],
            accessibility_needs=[],
            interests=['culture', 'nature', 'food'],
            risk_tolerance=0.7,
            luxury_preference=0.3,
            adventure_preference=0.6,
            cultural_preference=0.8
        )
        
        financial_profile = {
            'liquid_cash': 15000,
            'investment_portfolio': 200000,
            'monthly_income': 10000,
            'credit_card_points': 75000,
            'airline_miles': 40000,
            'is_business_travel': False,
            'tax_bracket': 0.28
        }
        
        result = await bonvoya_system.create_travel_plan(
            user_id='demo_fire_user',
            preferences=preferences,
            departure_location='San Francisco',
            financial_profile=financial_profile
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ FIRE demo error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo/luxury-travel', methods=['GET'])
async def demo_luxury_travel():
    """Demo luxury travel"""
    if bonvoya_system is None:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        # Create luxury travel preferences
        preferences = TravelPreferences(
            budget_range=(8000, 15000),
            travel_class=TravelClass.FIRST,
            accommodation_type=AccommodationType.LUXURY_HOTEL,
            purpose=TravelPurpose.LUXURY,
            duration_days=10,
            group_size=2,
            dietary_restrictions=[],
            accessibility_needs=[],
            interests=['luxury', 'fine_dining', 'spa'],
            risk_tolerance=0.9,
            luxury_preference=0.95,
            adventure_preference=0.2,
            cultural_preference=0.7
        )
        
        financial_profile = {
            'liquid_cash': 50000,
            'investment_portfolio': 500000,
            'monthly_income': 20000,
            'credit_card_points': 150000,
            'airline_miles': 80000,
            'is_business_travel': False,
            'tax_bracket': 0.35
        }
        
        result = await bonvoya_system.create_travel_plan(
            user_id='demo_luxury_user',
            preferences=preferences,
            departure_location='New York',
            financial_profile=financial_profile
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Luxury demo error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo/adventure-travel', methods=['GET'])
async def demo_adventure_travel():
    """Demo adventure travel"""
    if bonvoya_system is None:
        return jsonify({'error': 'System not initialized'}), 500
    
    try:
        # Create adventure travel preferences
        preferences = TravelPreferences(
            budget_range=(3000, 6000),
            travel_class=TravelClass.PREMIUM_ECONOMY,
            accommodation_type=AccommodationType.BOUTIQUE_HOTEL,
            purpose=TravelPurpose.ADVENTURE,
            duration_days=14,
            group_size=4,
            dietary_restrictions=[],
            accessibility_needs=[],
            interests=['hiking', 'nature', 'adventure'],
            risk_tolerance=0.8,
            luxury_preference=0.3,
            adventure_preference=0.95,
            cultural_preference=0.5
        )
        
        financial_profile = {
            'liquid_cash': 20000,
            'investment_portfolio': 300000,
            'monthly_income': 12000,
            'credit_card_points': 100000,
            'airline_miles': 60000,
            'is_business_travel': False,
            'tax_bracket': 0.28
        }
        
        result = await bonvoya_system.create_travel_plan(
            user_id='demo_adventure_user',
            preferences=preferences,
            departure_location='Los Angeles',
            financial_profile=financial_profile
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Adventure demo error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Async route handler wrapper
def async_route(f):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

# Apply async wrapper to async routes
app.route('/api/travel/plan', methods=['POST'])(async_route(create_travel_plan))
app.route('/api/travel/recommendations/<user_id>', methods=['GET'])(async_route(get_travel_recommendations))
app.route('/api/demo/fire-travel', methods=['GET'])(async_route(demo_fire_travel))
app.route('/api/demo/luxury-travel', methods=['GET'])(async_route(demo_luxury_travel))
app.route('/api/demo/adventure-travel', methods=['GET'])(async_route(demo_adventure_travel))

if __name__ == '__main__':
    print("🦞 Starting Lobsters Bonvoyå API Server...")
    
    # Initialize system
    if not initialize_bonvoya_system():
        print("❌ Failed to initialize system. Exiting.")
        exit(1)
    
    print("✅ Lobsters Bonvoyå system initialized successfully")
    print("📊 Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /api/travel/plan - Create travel plan")
    print("  GET  /api/travel/recommendations/<user_id> - Get recommendations")
    print("  GET  /api/travel/destinations - Get destinations")
    print("  POST /api/financial/optimize - Optimize travel finances")
    print("  GET  /api/stats - System statistics")
    print("  GET  /api/travel/purposes - Get travel purposes")
    print("  GET  /api/travel/classes - Get travel classes")
    print("  GET  /api/accommodation/types - Get accommodation types")
    print("  GET  /api/demo/fire-travel - Demo FIRE travel")
    print("  GET  /api/demo/luxury-travel - Demo luxury travel")
    print("  GET  /api/demo/adventure-travel - Demo adventure travel")
    
    # Start the server
    app.run(host='0.0.0.0', port=5002, debug=True)

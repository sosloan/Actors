#!/usr/bin/env python3
"""
🦞 Lobsters Bonvoyå - Premium Travel & Hospitality Intelligence System
Distributed Autonomous Agents for Travel Optimization & Financial Freedom

"Where every journey becomes a pathway to prosperity and adventure"
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from pathlib import Path

class TravelClass(Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"
    PRIVATE = "private"

class AccommodationType(Enum):
    HOSTEL = "hostel"
    BUDGET_HOTEL = "budget_hotel"
    BOUTIQUE_HOTEL = "boutique_hotel"
    LUXURY_HOTEL = "luxury_hotel"
    RESORT = "resort"
    VILLA = "villa"
    PRIVATE_ISLAND = "private_island"

class TravelPurpose(Enum):
    LEISURE = "leisure"
    BUSINESS = "business"
    ADVENTURE = "adventure"
    CULTURAL = "cultural"
    WELLNESS = "wellness"
    LUXURY = "luxury"
    BUDGET = "budget"
    FIRE_OPTIMIZATION = "fire_optimization"  # Financial Independence travel

@dataclass
class Destination:
    id: str
    name: str
    country: str
    continent: str
    coordinates: Tuple[float, float]
    climate: str
    cost_index: float  # Relative cost compared to global average
    safety_score: float  # 0-1 scale
    cultural_richness: float  # 0-1 scale
    adventure_score: float  # 0-1 scale
    luxury_score: float  # 0-1 scale
    fire_friendly: bool  # Good for FIRE lifestyle
    visa_requirements: List[str]
    best_seasons: List[str]

@dataclass
class TravelPreferences:
    budget_range: Tuple[float, float]
    travel_class: TravelClass
    accommodation_type: AccommodationType
    purpose: TravelPurpose
    duration_days: int
    group_size: int
    dietary_restrictions: List[str]
    accessibility_needs: List[str]
    interests: List[str]
    risk_tolerance: float  # 0-1 scale
    luxury_preference: float  # 0-1 scale
    adventure_preference: float  # 0-1 scale
    cultural_preference: float  # 0-1 scale

@dataclass
class FlightOption:
    id: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    duration_hours: float
    price: float
    class_type: TravelClass
    stops: int
    carbon_footprint: float
    comfort_score: float
    reliability_score: float

@dataclass
class AccommodationOption:
    id: str
    name: str
    type: AccommodationType
    location: str
    coordinates: Tuple[float, float]
    price_per_night: float
    rating: float
    amenities: List[str]
    availability: bool
    cancellation_policy: str
    sustainability_score: float
    local_experience_score: float

@dataclass
class TravelItinerary:
    id: str
    destination: Destination
    flights: List[FlightOption]
    accommodations: List[AccommodationOption]
    activities: List[Dict[str, Any]]
    total_cost: float
    total_duration_days: int
    carbon_footprint: float
    satisfaction_score: float
    fire_optimization_score: float
    adventure_score: float
    cultural_score: float
    luxury_score: float
    created_at: datetime

class TravelOptimizationAgent:
    """AI agent for optimizing travel experiences and costs"""
    
    def __init__(self):
        self.destinations_db = self._load_destinations()
        self.flight_cache = {}
        self.accommodation_cache = {}
        self.optimization_history = []
        
    def _load_destinations(self) -> Dict[str, Destination]:
        """Load comprehensive destination database"""
        destinations = {
            "tokyo": Destination(
                id="tokyo",
                name="Tokyo",
                country="Japan",
                continent="Asia",
                coordinates=(35.6762, 139.6503),
                climate="temperate",
                cost_index=1.2,
                safety_score=0.95,
                cultural_richness=0.98,
                adventure_score=0.7,
                luxury_score=0.9,
                fire_friendly=True,
                visa_requirements=["passport"],
                best_seasons=["spring", "autumn"]
            ),
            "paris": Destination(
                id="paris",
                name="Paris",
                country="France",
                continent="Europe",
                coordinates=(48.8566, 2.3522),
                climate="temperate",
                cost_index=1.1,
                safety_score=0.85,
                cultural_richness=0.99,
                adventure_score=0.4,
                luxury_score=0.95,
                fire_friendly=True,
                visa_requirements=["passport", "schengen"],
                best_seasons=["spring", "summer", "autumn"]
            ),
            "bali": Destination(
                id="bali",
                name="Bali",
                country="Indonesia",
                continent="Asia",
                coordinates=(-8.3405, 115.0920),
                climate="tropical",
                cost_index=0.3,
                safety_score=0.8,
                cultural_richness=0.9,
                adventure_score=0.8,
                luxury_score=0.7,
                fire_friendly=True,
                visa_requirements=["passport"],
                best_seasons=["dry_season"]
            ),
            "iceland": Destination(
                id="iceland",
                name="Iceland",
                country="Iceland",
                continent="Europe",
                coordinates=(64.9631, -19.0208),
                climate="subarctic",
                cost_index=1.5,
                safety_score=0.98,
                cultural_richness=0.8,
                adventure_score=0.95,
                luxury_score=0.6,
                fire_friendly=False,
                visa_requirements=["passport"],
                best_seasons=["summer"]
            ),
            "costa_rica": Destination(
                id="costa_rica",
                name="Costa Rica",
                country="Costa Rica",
                continent="North America",
                coordinates=(9.7489, -83.7534),
                climate="tropical",
                cost_index=0.6,
                safety_score=0.85,
                cultural_richness=0.7,
                adventure_score=0.9,
                luxury_score=0.5,
                fire_friendly=True,
                visa_requirements=["passport"],
                best_seasons=["dry_season"]
            ),
            "dubai": Destination(
                id="dubai",
                name="Dubai",
                country="UAE",
                continent="Asia",
                coordinates=(25.2048, 55.2708),
                climate="desert",
                cost_index=1.3,
                safety_score=0.9,
                cultural_richness=0.6,
                adventure_score=0.5,
                luxury_score=0.98,
                fire_friendly=False,
                visa_requirements=["passport"],
                best_seasons=["winter"]
            )
        }
        return destinations
    
    async def optimize_travel_plan(
        self, 
        preferences: TravelPreferences,
        departure_location: str,
        max_results: int = 5
    ) -> List[TravelItinerary]:
        """Optimize travel plan based on preferences and financial goals"""
        
        print(f"🦞 Lobsters Bonvoyå: Optimizing travel for {preferences.purpose.value} experience")
        print(f"💰 Budget: ${preferences.budget_range[0]:,.0f} - ${preferences.budget_range[1]:,.0f}")
        
        # Filter destinations based on preferences
        suitable_destinations = self._filter_destinations(preferences)
        
        # Generate itineraries for each suitable destination
        itineraries = []
        for destination in suitable_destinations:
            itinerary = await self._create_itinerary(
                destination, preferences, departure_location
            )
            if itinerary:
                itineraries.append(itinerary)
        
        # Sort by optimization score
        itineraries.sort(key=lambda x: self._calculate_optimization_score(x, preferences), reverse=True)
        
        return itineraries[:max_results]
    
    def _filter_destinations(self, preferences: TravelPreferences) -> List[Destination]:
        """Filter destinations based on travel preferences"""
        suitable = []
        
        for dest in self.destinations_db.values():
            # Budget filter
            if preferences.budget_range[1] < dest.cost_index * 1000:  # Rough budget check
                continue
                
            # Purpose-based filtering
            if preferences.purpose == TravelPurpose.FIRE_OPTIMIZATION and not dest.fire_friendly:
                continue
            elif preferences.purpose == TravelPurpose.LUXURY and dest.luxury_score < 0.7:
                continue
            elif preferences.purpose == TravelPurpose.ADVENTURE and dest.adventure_score < 0.6:
                continue
            elif preferences.purpose == TravelPurpose.CULTURAL and dest.cultural_richness < 0.7:
                continue
                
            # Risk tolerance filter
            if preferences.risk_tolerance < 0.5 and dest.safety_score < 0.8:
                continue
                
            suitable.append(dest)
        
        return suitable
    
    async def _create_itinerary(
        self, 
        destination: Destination, 
        preferences: TravelPreferences,
        departure_location: str
    ) -> Optional[TravelItinerary]:
        """Create a detailed itinerary for a destination"""
        
        # Simulate flight search
        flights = await self._search_flights(departure_location, destination, preferences)
        if not flights:
            return None
            
        # Simulate accommodation search
        accommodations = await self._search_accommodations(destination, preferences)
        if not accommodations:
            return None
            
        # Calculate costs and scores
        total_cost = sum(f.price for f in flights) + sum(a.price_per_night * preferences.duration_days for a in accommodations)
        
        # Generate activities based on preferences
        activities = self._generate_activities(destination, preferences)
        
        itinerary = TravelItinerary(
            id=f"itinerary_{destination.id}_{int(time.time())}",
            destination=destination,
            flights=flights,
            accommodations=accommodations,
            activities=activities,
            total_cost=total_cost,
            total_duration_days=preferences.duration_days,
            carbon_footprint=sum(f.carbon_footprint for f in flights),
            satisfaction_score=self._calculate_satisfaction_score(destination, preferences),
            fire_optimization_score=self._calculate_fire_score(destination, total_cost),
            adventure_score=destination.adventure_score,
            cultural_score=destination.cultural_richness,
            luxury_score=destination.luxury_score,
            created_at=datetime.now()
        )
        
        return itinerary
    
    async def _search_flights(
        self, 
        departure: str, 
        destination: Destination, 
        preferences: TravelPreferences
    ) -> List[FlightOption]:
        """Search for flight options (simulated)"""
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        flights = []
        base_price = 800 + (destination.cost_index * 200)
        
        # Generate multiple flight options
        for i in range(3):
            price_multiplier = {
                TravelClass.ECONOMY: 1.0,
                TravelClass.PREMIUM_ECONOMY: 1.5,
                TravelClass.BUSINESS: 3.0,
                TravelClass.FIRST: 5.0,
                TravelClass.PRIVATE: 20.0
            }.get(preferences.travel_class, 1.0)
            
            flight = FlightOption(
                id=f"flight_{destination.id}_{i}",
                airline=f"Airline {i+1}",
                departure_airport=departure,
                arrival_airport=f"{destination.name} Airport",
                departure_time=datetime.now() + timedelta(days=30),
                arrival_time=datetime.now() + timedelta(days=30, hours=8),
                duration_hours=8 + i,
                price=base_price * price_multiplier * (1 + i * 0.1),
                class_type=preferences.travel_class,
                stops=i,
                carbon_footprint=2.5 + i * 0.5,
                comfort_score=0.7 + i * 0.1,
                reliability_score=0.9 - i * 0.05
            )
            flights.append(flight)
        
        return flights
    
    async def _search_accommodations(
        self, 
        destination: Destination, 
        preferences: TravelPreferences
    ) -> List[AccommodationOption]:
        """Search for accommodation options (simulated)"""
        
        await asyncio.sleep(0.1)
        
        accommodations = []
        base_price = 100 * destination.cost_index
        
        for i in range(2):
            price_multiplier = {
                AccommodationType.HOSTEL: 0.3,
                AccommodationType.BUDGET_HOTEL: 0.6,
                AccommodationType.BOUTIQUE_HOTEL: 1.2,
                AccommodationType.LUXURY_HOTEL: 2.0,
                AccommodationType.RESORT: 2.5,
                AccommodationType.VILLA: 3.0,
                AccommodationType.PRIVATE_ISLAND: 10.0
            }.get(preferences.accommodation_type, 1.0)
            
            accommodation = AccommodationOption(
                id=f"accommodation_{destination.id}_{i}",
                name=f"{destination.name} {preferences.accommodation_type.value.title()} {i+1}",
                type=preferences.accommodation_type,
                location=destination.name,
                coordinates=destination.coordinates,
                price_per_night=base_price * price_multiplier * (1 + i * 0.2),
                rating=4.0 + i * 0.5,
                amenities=["WiFi", "Pool", "Spa", "Restaurant"],
                availability=True,
                cancellation_policy="Free cancellation",
                sustainability_score=0.7 + i * 0.1,
                local_experience_score=0.8 + i * 0.1
            )
            accommodations.append(accommodation)
        
        return accommodations
    
    def _generate_activities(self, destination: Destination, preferences: TravelPreferences) -> List[Dict[str, Any]]:
        """Generate activities based on destination and preferences"""
        
        activities = []
        
        # Base activities for all destinations
        base_activities = [
            {"name": "City Walking Tour", "cost": 50, "duration_hours": 3, "type": "cultural"},
            {"name": "Local Market Visit", "cost": 30, "duration_hours": 2, "type": "cultural"},
            {"name": "Traditional Restaurant", "cost": 80, "duration_hours": 2, "type": "culinary"}
        ]
        
        # Add activities based on destination characteristics
        if destination.adventure_score > 0.7:
            activities.extend([
                {"name": "Adventure Excursion", "cost": 150, "duration_hours": 6, "type": "adventure"},
                {"name": "Nature Hiking", "cost": 60, "duration_hours": 4, "type": "adventure"}
            ])
        
        if destination.luxury_score > 0.8:
            activities.extend([
                {"name": "Luxury Spa Experience", "cost": 200, "duration_hours": 3, "type": "wellness"},
                {"name": "Fine Dining Experience", "cost": 300, "duration_hours": 3, "type": "luxury"}
            ])
        
        if destination.cultural_richness > 0.8:
            activities.extend([
                {"name": "Museum & Gallery Tour", "cost": 40, "duration_hours": 4, "type": "cultural"},
                {"name": "Historical Site Visit", "cost": 25, "duration_hours": 3, "type": "cultural"}
            ])
        
        return base_activities + activities
    
    def _calculate_satisfaction_score(self, destination: Destination, preferences: TravelPreferences) -> float:
        """Calculate predicted satisfaction score"""
        
        score = 0.0
        
        # Purpose alignment
        if preferences.purpose == TravelPurpose.LUXURY:
            score += destination.luxury_score * 0.4
        elif preferences.purpose == TravelPurpose.ADVENTURE:
            score += destination.adventure_score * 0.4
        elif preferences.purpose == TravelPurpose.CULTURAL:
            score += destination.cultural_richness * 0.4
        elif preferences.purpose == TravelPurpose.FIRE_OPTIMIZATION:
            score += (1.0 - destination.cost_index / 2.0) * 0.4  # Lower cost = higher score
        
        # Safety and comfort
        score += destination.safety_score * 0.3
        
        # Cultural richness (always valuable)
        score += destination.cultural_richness * 0.2
        
        # Adventure preference alignment
        score += destination.adventure_score * preferences.adventure_preference * 0.1
        
        return min(score, 1.0)
    
    def _calculate_fire_score(self, destination: Destination, total_cost: float) -> float:
        """Calculate FIRE optimization score (lower cost, higher value)"""
        
        if not destination.fire_friendly:
            return 0.0
        
        # Value per dollar spent
        value_score = (destination.cultural_richness + destination.adventure_score + destination.safety_score) / 3.0
        
        # Cost efficiency (lower cost = higher score)
        cost_efficiency = max(0, 1.0 - (total_cost / 10000))  # Normalize around $10k
        
        return (value_score + cost_efficiency) / 2.0
    
    def _calculate_optimization_score(self, itinerary: TravelItinerary, preferences: TravelPreferences) -> float:
        """Calculate overall optimization score"""
        
        score = 0.0
        
        # Budget alignment (lower cost = higher score if within budget)
        if preferences.budget_range[0] <= itinerary.total_cost <= preferences.budget_range[1]:
            budget_score = 1.0 - (itinerary.total_cost - preferences.budget_range[0]) / (preferences.budget_range[1] - preferences.budget_range[0])
        else:
            budget_score = 0.0
        
        score += budget_score * 0.3
        
        # Satisfaction score
        score += itinerary.satisfaction_score * 0.25
        
        # FIRE optimization (if applicable)
        if preferences.purpose == TravelPurpose.FIRE_OPTIMIZATION:
            score += itinerary.fire_optimization_score * 0.25
        else:
            score += itinerary.satisfaction_score * 0.25
        
        # Carbon footprint (lower = better)
        carbon_score = max(0, 1.0 - itinerary.carbon_footprint / 10.0)
        score += carbon_score * 0.1
        
        # Adventure/Cultural/Luxury alignment
        if preferences.adventure_preference > 0.5:
            score += itinerary.adventure_score * 0.1
        if preferences.cultural_preference > 0.5:
            score += itinerary.cultural_score * 0.1
        if preferences.luxury_preference > 0.5:
            score += itinerary.luxury_score * 0.1
        
        return min(score, 1.0)

class FinancialIntegrationAgent:
    """Integrates travel optimization with ACTORS financial system"""
    
    def __init__(self):
        self.travel_budget_allocator = TravelBudgetAllocator()
        self.points_optimizer = PointsOptimizer()
        self.tax_optimizer = TravelTaxOptimizer()
    
    async def optimize_travel_finances(
        self, 
        itinerary: TravelItinerary, 
        user_financial_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize travel finances using ACTORS financial intelligence"""
        
        print(f"💰 Optimizing travel finances for {itinerary.destination.name}")
        
        # Allocate budget from investment portfolio
        budget_allocation = await self.travel_budget_allocator.allocate_budget(
            itinerary.total_cost, user_financial_profile
        )
        
        # Optimize points and miles usage
        points_optimization = await self.points_optimizer.optimize_points_usage(
            itinerary, user_financial_profile
        )
        
        # Optimize tax implications
        tax_optimization = await self.tax_optimizer.optimize_tax_strategy(
            itinerary, user_financial_profile
        )
        
        return {
            "budget_allocation": budget_allocation,
            "points_optimization": points_optimization,
            "tax_optimization": tax_optimization,
            "total_savings": (
                budget_allocation.get("savings", 0) + 
                points_optimization.get("savings", 0) + 
                tax_optimization.get("savings", 0)
            )
        }

class TravelBudgetAllocator:
    """Allocates travel budget from investment portfolio"""
    
    async def allocate_budget(self, travel_cost: float, financial_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate travel budget optimally"""
        
        # Simulate portfolio analysis
        await asyncio.sleep(0.1)
        
        liquid_cash = financial_profile.get("liquid_cash", 10000)
        investment_portfolio = financial_profile.get("investment_portfolio", 100000)
        monthly_income = financial_profile.get("monthly_income", 8000)
        
        # Calculate optimal allocation
        if travel_cost <= liquid_cash * 0.1:  # Use cash if < 10% of liquid cash
            allocation_method = "liquid_cash"
            savings = 0
        elif travel_cost <= investment_portfolio * 0.02:  # Use investments if < 2% of portfolio
            allocation_method = "investment_portfolio"
            savings = travel_cost * 0.05  # 5% savings from tax optimization
        else:
            allocation_method = "monthly_income"
            savings = travel_cost * 0.03  # 3% savings from timing optimization
        
        return {
            "allocation_method": allocation_method,
            "amount": travel_cost,
            "savings": savings,
            "recommendation": f"Use {allocation_method} for optimal financial impact"
        }

class PointsOptimizer:
    """Optimizes credit card points and airline miles usage"""
    
    async def optimize_points_usage(self, itinerary: TravelItinerary, financial_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize points and miles for maximum value"""
        
        await asyncio.sleep(0.1)
        
        available_points = financial_profile.get("credit_card_points", 50000)
        available_miles = financial_profile.get("airline_miles", 25000)
        
        # Calculate points value
        flight_cost = sum(f.price for f in itinerary.flights)
        accommodation_cost = sum(a.price_per_night * itinerary.total_duration_days for a in itinerary.accommodations)
        
        # Optimize flight redemption
        flight_savings = 0
        if available_miles >= 25000 and flight_cost > 500:
            flight_savings = flight_cost * 0.3  # 30% savings with miles
            available_miles -= 25000
        
        # Optimize accommodation redemption
        accommodation_savings = 0
        if available_points >= 20000 and accommodation_cost > 300:
            accommodation_savings = accommodation_cost * 0.2  # 20% savings with points
            available_points -= 20000
        
        total_savings = flight_savings + accommodation_savings
        
        return {
            "flight_savings": flight_savings,
            "accommodation_savings": accommodation_savings,
            "total_savings": total_savings,
            "points_used": 20000 - available_points,
            "miles_used": 25000 - available_miles,
            "recommendation": f"Save ${total_savings:.0f} using points and miles"
        }

class TravelTaxOptimizer:
    """Optimizes tax implications of business travel"""
    
    async def optimize_tax_strategy(self, itinerary: TravelItinerary, financial_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize tax strategy for travel expenses"""
        
        await asyncio.sleep(0.1)
        
        is_business_travel = financial_profile.get("is_business_travel", False)
        tax_bracket = financial_profile.get("tax_bracket", 0.25)
        
        if is_business_travel:
            # Business travel deductions
            deductible_amount = itinerary.total_cost * 0.8  # 80% typically deductible
            tax_savings = deductible_amount * tax_bracket
            
            return {
                "deductible_amount": deductible_amount,
                "tax_savings": tax_savings,
                "strategy": "business_deduction",
                "recommendation": f"Save ${tax_savings:.0f} through business travel deductions"
            }
        else:
            # Personal travel - optimize timing for tax year
            return {
                "deductible_amount": 0,
                "tax_savings": 0,
                "strategy": "personal_travel",
                "recommendation": "Consider business travel for tax benefits"
            }

class LobstersBonvoyaSystem:
    """Main system orchestrating all travel optimization components"""
    
    def __init__(self):
        self.travel_agent = TravelOptimizationAgent()
        self.financial_agent = FinancialIntegrationAgent()
        self.user_profiles = {}
        self.booking_history = []
    
    async def create_travel_plan(
        self,
        user_id: str,
        preferences: TravelPreferences,
        departure_location: str,
        financial_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create optimized travel plan with financial integration"""
        
        print(f"\n🦞 Lobsters Bonvoyå: Creating travel plan for user {user_id}")
        print(f"🎯 Purpose: {preferences.purpose.value}")
        print(f"💰 Budget: ${preferences.budget_range[0]:,.0f} - ${preferences.budget_range[1]:,.0f}")
        print(f"✈️  Departure: {departure_location}")
        
        # Generate travel itineraries
        itineraries = await self.travel_agent.optimize_travel_plan(
            preferences, departure_location, max_results=3
        )
        
        if not itineraries:
            return {"error": "No suitable travel options found"}
        
        # Optimize finances for the best itinerary
        best_itinerary = itineraries[0]
        financial_optimization = {}
        
        if financial_profile:
            financial_optimization = await self.financial_agent.optimize_travel_finances(
                best_itinerary, financial_profile
            )
        
        # Store user profile and booking
        self.user_profiles[user_id] = {
            "preferences": preferences,
            "financial_profile": financial_profile,
            "last_updated": datetime.now()
        }
        
        self.booking_history.append({
            "user_id": user_id,
            "itinerary": best_itinerary,
            "financial_optimization": financial_optimization,
            "created_at": datetime.now()
        })
        
        return {
            "user_id": user_id,
            "recommended_itinerary": asdict(best_itinerary),
            "alternative_itineraries": [asdict(it) for it in itineraries[1:]],
            "financial_optimization": financial_optimization,
            "total_savings": financial_optimization.get("total_savings", 0),
            "optimization_score": self.travel_agent._calculate_optimization_score(best_itinerary, preferences),
            "created_at": datetime.now().isoformat()
        }
    
    async def get_travel_recommendations(
        self, 
        user_id: str, 
        recommendation_type: str = "personalized"
    ) -> Dict[str, Any]:
        """Get personalized travel recommendations"""
        
        if user_id not in self.user_profiles:
            return {"error": "User profile not found"}
        
        user_profile = self.user_profiles[user_id]
        preferences = user_profile["preferences"]
        
        # Generate recommendations based on user history and preferences
        recommendations = []
        
        # FIRE-friendly destinations
        if preferences.purpose == TravelPurpose.FIRE_OPTIMIZATION:
            fire_destinations = [
                dest for dest in self.travel_agent.destinations_db.values() 
                if dest.fire_friendly and dest.cost_index < 0.8
            ]
            recommendations.extend(fire_destinations[:3])
        
        # Adventure destinations
        if preferences.adventure_preference > 0.7:
            adventure_destinations = [
                dest for dest in self.travel_agent.destinations_db.values() 
                if dest.adventure_score > 0.8
            ]
            recommendations.extend(adventure_destinations[:2])
        
        # Cultural destinations
        if preferences.cultural_preference > 0.7:
            cultural_destinations = [
                dest for dest in self.travel_agent.destinations_db.values() 
                if dest.cultural_richness > 0.9
            ]
            recommendations.extend(cultural_destinations[:2])
        
        return {
            "user_id": user_id,
            "recommendation_type": recommendation_type,
            "recommendations": [asdict(dest) for dest in recommendations],
            "generated_at": datetime.now().isoformat()
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics and performance metrics"""
        
        total_users = len(self.user_profiles)
        total_bookings = len(self.booking_history)
        
        # Calculate average savings
        total_savings = sum(
            booking.get("financial_optimization", {}).get("total_savings", 0)
            for booking in self.booking_history
        )
        avg_savings = total_savings / total_bookings if total_bookings > 0 else 0
        
        # Calculate popular destinations
        destination_counts = {}
        for booking in self.booking_history:
            dest_name = booking["itinerary"].destination.name
            destination_counts[dest_name] = destination_counts.get(dest_name, 0) + 1
        
        popular_destinations = sorted(
            destination_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "total_users": total_users,
            "total_bookings": total_bookings,
            "average_savings_per_booking": avg_savings,
            "popular_destinations": popular_destinations,
            "system_uptime": "Active",
            "last_updated": datetime.now().isoformat()
        }

async def demo_lobsters_bonvoya():
    """Demonstrate the Lobsters Bonvoyå system"""
    
    print("🦞 Welcome to Lobsters Bonvoyå - Premium Travel Intelligence")
    print("=" * 60)
    
    # Initialize system
    system = LobstersBonvoyaSystem()
    
    # Demo 1: FIRE Optimization Travel
    print("\n🔥 Demo 1: FIRE Optimization Travel")
    print("-" * 40)
    
    fire_preferences = TravelPreferences(
        budget_range=(2000, 4000),
        travel_class=TravelClass.ECONOMY,
        accommodation_type=AccommodationType.BOUTIQUE_HOTEL,
        purpose=TravelPurpose.FIRE_OPTIMIZATION,
        duration_days=7,
        group_size=2,
        dietary_restrictions=[],
        accessibility_needs=[],
        interests=["culture", "nature", "food"],
        risk_tolerance=0.7,
        luxury_preference=0.3,
        adventure_preference=0.6,
        cultural_preference=0.8
    )
    
    fire_financial_profile = {
        "liquid_cash": 15000,
        "investment_portfolio": 200000,
        "monthly_income": 10000,
        "credit_card_points": 75000,
        "airline_miles": 40000,
        "is_business_travel": False,
        "tax_bracket": 0.28
    }
    
    fire_plan = await system.create_travel_plan(
        "fire_traveler_001",
        fire_preferences,
        "San Francisco",
        fire_financial_profile
    )
    
    print(f"✅ FIRE Travel Plan Created!")
    print(f"   Destination: {fire_plan['recommended_itinerary']['destination']['name']}")
    print(f"   Total Cost: ${fire_plan['recommended_itinerary']['total_cost']:,.0f}")
    print(f"   Total Savings: ${fire_plan['total_savings']:,.0f}")
    print(f"   Optimization Score: {fire_plan['optimization_score']:.2f}")
    
    # Demo 2: Luxury Travel
    print("\n💎 Demo 2: Luxury Travel Experience")
    print("-" * 40)
    
    luxury_preferences = TravelPreferences(
        budget_range=(8000, 15000),
        travel_class=TravelClass.FIRST,
        accommodation_type=AccommodationType.LUXURY_HOTEL,
        purpose=TravelPurpose.LUXURY,
        duration_days=10,
        group_size=2,
        dietary_restrictions=[],
        accessibility_needs=[],
        interests=["luxury", "fine_dining", "spa"],
        risk_tolerance=0.9,
        luxury_preference=0.95,
        adventure_preference=0.2,
        cultural_preference=0.7
    )
    
    luxury_plan = await system.create_travel_plan(
        "luxury_traveler_001",
        luxury_preferences,
        "New York",
        fire_financial_profile  # Same financial profile for demo
    )
    
    print(f"✅ Luxury Travel Plan Created!")
    print(f"   Destination: {luxury_plan['recommended_itinerary']['destination']['name']}")
    print(f"   Total Cost: ${luxury_plan['recommended_itinerary']['total_cost']:,.0f}")
    print(f"   Total Savings: ${luxury_plan['total_savings']:,.0f}")
    print(f"   Optimization Score: {luxury_plan['optimization_score']:.2f}")
    
    # Demo 3: Adventure Travel
    print("\n🏔️ Demo 3: Adventure Travel")
    print("-" * 40)
    
    adventure_preferences = TravelPreferences(
        budget_range=(3000, 6000),
        travel_class=TravelClass.PREMIUM_ECONOMY,
        accommodation_type=AccommodationType.BOUTIQUE_HOTEL,
        purpose=TravelPurpose.ADVENTURE,
        duration_days=14,
        group_size=4,
        dietary_restrictions=[],
        accessibility_needs=[],
        interests=["hiking", "nature", "adventure"],
        risk_tolerance=0.8,
        luxury_preference=0.3,
        adventure_preference=0.95,
        cultural_preference=0.5
    )
    
    adventure_plan = await system.create_travel_plan(
        "adventure_traveler_001",
        adventure_preferences,
        "Los Angeles",
        fire_financial_profile
    )
    
    print(f"✅ Adventure Travel Plan Created!")
    print(f"   Destination: {adventure_plan['recommended_itinerary']['destination']['name']}")
    print(f"   Total Cost: ${adventure_plan['recommended_itinerary']['total_cost']:,.0f}")
    print(f"   Total Savings: ${adventure_plan['total_savings']:,.0f}")
    print(f"   Optimization Score: {adventure_plan['optimization_score']:.2f}")
    
    # Demo 4: Get Recommendations
    print("\n💡 Demo 4: Personalized Recommendations")
    print("-" * 40)
    
    recommendations = await system.get_travel_recommendations("fire_traveler_001")
    print(f"✅ Generated {len(recommendations['recommendations'])} recommendations")
    for i, rec in enumerate(recommendations['recommendations'][:3], 1):
        print(f"   {i}. {rec['name']}, {rec['country']} (Cost Index: {rec['cost_index']})")
    
    # Demo 5: System Statistics
    print("\n📊 Demo 5: System Statistics")
    print("-" * 40)
    
    stats = system.get_system_stats()
    print(f"✅ System Performance:")
    print(f"   Total Users: {stats['total_users']}")
    print(f"   Total Bookings: {stats['total_bookings']}")
    print(f"   Average Savings: ${stats['average_savings_per_booking']:,.0f}")
    print(f"   Popular Destinations: {[dest[0] for dest in stats['popular_destinations']]}")
    
    print("\n🎉 Lobsters Bonvoyå Demo Complete!")
    print("=" * 60)
    print("The system successfully demonstrates:")
    print("• AI-powered travel optimization")
    print("• Financial integration with ACTORS")
    print("• Personalized recommendations")
    print("• Cost optimization and savings")
    print("• Multi-purpose travel planning")
    print("\n🦞 Bon voyage with Lobsters Bonvoyå! ✈️🌍")

if __name__ == "__main__":
    asyncio.run(demo_lobsters_bonvoya())

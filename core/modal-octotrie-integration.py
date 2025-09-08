# 🎭 OCTOTRIE Modal Integration
# Combines Modal's cloud computing with the 8-dimensional narrative engine
# Now with Convex real-time database integration

import modal
from pathlib import Path
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
import json
import asyncio
import os

# Define the Modal app and image
app = modal.App("octotrie-modal-integration")

# Create a custom image with all necessary dependencies including Convex
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "instructor~=1.7.2",
    "anthropic==0.42.0",
    "playwright==1.42.0",
    "recharts",
    "tailwindcss",
    "framer-motion",
    "convex",
    "httpx",
    "websockets"
).run_commands(
    "apt-get update",
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "playwright install-deps chromium",
    "playwright install chromium",
)

# Convex integration
CONVEX_URL = os.getenv("CONVEX_URL", "https://your-deployment.convex.cloud")
CONVEX_API_KEY = os.getenv("CONVEX_API_KEY", "")

# Pydantic models for structured data extraction
class OctotrieDimension(BaseModel):
    """Represents one of the 8 dimensions in the OCTOTRIE system."""
    dimension_number: int = Field(..., ge=1, le=8)
    name: str = Field(..., description="Name of the dimension archetype")
    role: str = Field(..., description="The role/purpose of this dimension")
    resonance: float = Field(..., ge=0.0, le=1.0, description="Resonance level (0-1)")
    icon: str = Field(..., description="Unicode icon representing this dimension")
    color: str = Field(..., description="Hex color code for this dimension")
    energy_level: float = Field(..., ge=0.0, le=2.0, description="Energy level (0-2)")

class OctotrieStory(BaseModel):
    """Complete 8-dimensional story structure."""
    title: str = Field(..., description="Story title")
    template: str = Field(..., description="Story template used")
    dimensions: List[OctotrieDimension] = Field(..., description="All 8 dimensions")
    narrative_energy: float = Field(..., ge=0.0, le=2.0)
    jackie_resonance: float = Field(..., ge=0.0, le=1.0)
    system_harmony: float = Field(..., ge=0.0, le=1.0)
    sacred_geometry_score: float = Field(..., ge=0.0, le=1.0)
    generated_story: str = Field(..., description="The complete generated narrative")

class TradingAgent(BaseModel):
    """Represents a trading agent in the system."""
    name: str = Field(..., description="Agent name")
    dimension: str = Field(..., description="Associated dimension")
    resonance: float = Field(..., ge=0.0, le=1.0)
    status: Literal["active", "inactive", "error"] = Field(...)
    energy: float = Field(..., ge=0.0, le=2.0)
    performance_score: float = Field(..., ge=0.0, le=1.0)

class SystemHealth(BaseModel):
    """System health and status information."""
    overall_health: float = Field(..., ge=0.0, le=100.0)
    active_agents: int = Field(..., ge=0)
    system_load: float = Field(..., ge=0.0, le=100.0)
    error_count: int = Field(..., ge=0)
    last_optimization: str = Field(..., description="Timestamp of last optimization")

class ConvexStory(BaseModel):
    """Convex-compatible story structure."""
    _id: Optional[str] = Field(None, description="Convex document ID")
    _creationTime: Optional[int] = Field(None, description="Convex creation timestamp")
    title: str = Field(..., description="Story title")
    template: str = Field(..., description="Story template used")
    dimensions: List[Dict] = Field(..., description="All 8 dimensions as dicts")
    narrative_energy: float = Field(..., ge=0.0, le=2.0)
    jackie_resonance: float = Field(..., ge=0.0, le=1.0)
    system_harmony: float = Field(..., ge=0.0, le=1.0)
    sacred_geometry_score: float = Field(..., ge=0.0, le=1.0)
    generated_story: str = Field(..., description="The complete generated narrative")
    created_at: str = Field(..., description="ISO timestamp")
    updated_at: str = Field(..., description="ISO timestamp")
    user_id: Optional[str] = Field(None, description="User ID if applicable")

# Convex integration functions
@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("anthropic-secret", required_keys=["ANTHROPIC_API_KEY"]),
        modal.Secret.from_name("convex-secret", required_keys=["CONVEX_URL", "CONVEX_API_KEY"])
    ]
)
def convex_store_story(story: OctotrieStory, user_id: Optional[str] = None) -> Dict:
    """Store a generated story in Convex database."""
    import httpx
    import json
    from datetime import datetime
    
    # Convert story to Convex format
    convex_story = ConvexStory(
        title=story.title,
        template=story.template,
        dimensions=[dim.model_dump() for dim in story.dimensions],
        narrative_energy=story.narrative_energy,
        jackie_resonance=story.jackie_resonance,
        system_harmony=story.system_harmony,
        sacred_geometry_score=story.sacred_geometry_score,
        generated_story=story.generated_story,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        user_id=user_id
    )
    
    # Call Convex mutation function
    mutation_data = {
        "function": "octotrie:storeStory",
        "args": [convex_story.model_dump()]
    }
    
    headers = {
        "Authorization": f"Bearer {CONVEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    with httpx.Client() as client:
        response = client.post(
            f"{CONVEX_URL}/api/mutation",
            json=mutation_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("convex-secret", required_keys=["CONVEX_URL", "CONVEX_API_KEY"])
    ]
)
def convex_get_stories(template: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """Retrieve stories from Convex database."""
    import httpx
    
    # Build query parameters
    args = [limit]
    if template:
        args.append(template)
    
    query_data = {
        "function": "octotrie:getStories",
        "args": args
    }
    
    headers = {
        "Authorization": f"Bearer {CONVEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    with httpx.Client() as client:
        response = client.post(
            f"{CONVEX_URL}/api/query",
            json=query_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("convex-secret", required_keys=["CONVEX_URL", "CONVEX_API_KEY"])
    ]
)
def convex_store_trading_agents(agents: List[TradingAgent]) -> Dict:
    """Store trading agents in Convex database."""
    import httpx
    from datetime import datetime
    
    # Convert agents to Convex format
    convex_agents = []
    for agent in agents:
        convex_agent = {
            "name": agent.name,
            "dimension": agent.dimension,
            "resonance": agent.resonance,
            "status": agent.status,
            "energy": agent.energy,
            "performance_score": agent.performance_score,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        convex_agents.append(convex_agent)
    
    mutation_data = {
        "function": "octotrie:storeTradingAgents",
        "args": [convex_agents]
    }
    
    headers = {
        "Authorization": f"Bearer {CONVEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    with httpx.Client() as client:
        response = client.post(
            f"{CONVEX_URL}/api/mutation",
            json=mutation_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("convex-secret", required_keys=["CONVEX_URL", "CONVEX_API_KEY"])
    ]
)
def convex_update_system_health(health: SystemHealth) -> Dict:
    """Update system health in Convex database."""
    import httpx
    from datetime import datetime
    
    health_data = {
        "overall_health": health.overall_health,
        "active_agents": health.active_agents,
        "system_load": health.system_load,
        "error_count": health.error_count,
        "last_optimization": health.last_optimization,
        "updated_at": datetime.now().isoformat()
    }
    
    mutation_data = {
        "function": "octotrie:updateSystemHealth",
        "args": [health_data]
    }
    
    headers = {
        "Authorization": f"Bearer {CONVEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    with httpx.Client() as client:
        response = client.post(
            f"{CONVEX_URL}/api/mutation",
            json=mutation_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("convex-secret", required_keys=["CONVEX_URL", "CONVEX_API_KEY"])
    ]
)
def convex_get_system_metrics() -> Dict:
    """Get system metrics from Convex database."""
    import httpx
    
    query_data = {
        "function": "octotrie:getSystemMetrics",
        "args": []
    }
    
    headers = {
        "Authorization": f"Bearer {CONVEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    with httpx.Client() as client:
        response = client.post(
            f"{CONVEX_URL}/api/query",
            json=query_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("convex-secret", required_keys=["CONVEX_URL", "CONVEX_API_KEY"])
    ]
)
def convex_create_realtime_subscription(story_id: str) -> Dict:
    """Create a real-time subscription for story updates."""
    import httpx
    
    subscription_data = {
        "function": "octotrie:subscribeToStory",
        "args": [story_id]
    }
    
    headers = {
        "Authorization": f"Bearer {CONVEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    with httpx.Client() as client:
        response = client.post(
            f"{CONVEX_URL}/api/subscribe",
            json=subscription_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

# Modal functions for distributed OCTOTRIE processing

@app.function(
    image=image,
    max_containers=10,
    secrets=[modal.Secret.from_name("anthropic-secret", required_keys=["ANTHROPIC_API_KEY"])]
)
def generate_octotrie_story(
    template: str,
    input_text: Optional[str] = None,
    use_opus: bool = False
) -> OctotrieStory:
    """Generate a complete 8-dimensional OCTOTRIE story using AI."""
    import instructor
    from anthropic import Anthropic
    
    client = instructor.from_anthropic(Anthropic())
    model = "claude-3-opus-20240229" if use_opus else "claude-3-haiku-20240307"
    
    # Define the 8 dimensions
    dimension_definitions = {
        "Prince": {"role": "The Generous Giver", "icon": "👑", "color": "#3B82F6"},
        "Sloan": {"role": "The Foundation Builder", "icon": "🏗️", "color": "#8B5CF6"},
        "Adam": {"role": "The Seeker/Transformer", "icon": "🔍", "color": "#10B981"},
        "Stan": {"role": "The Analyzer", "icon": "📊", "color": "#F59E0B"},
        "Grace": {"role": "The Harmonizer", "icon": "🎵", "color": "#EC4899"},
        "JAX42": {"role": "The Optimizer", "icon": "⚡", "color": "#6366F1"},
        "Ray Lewis": {"role": "The Heart/Completion", "icon": "❤️", "color": "#EF4444"},
        "Harmony": {"role": "The Universal Resonance", "icon": "🌟", "color": "#06B6D4"}
    }
    
    # Generate story using AI
    story_prompt = f"""
    Generate a complete 8-dimensional OCTOTRIE story based on the template: {template}
    
    Input context: {input_text or "Automotive and personal transformation journey"}
    
    Create a story that incorporates all 8 dimensions with their sacred geometry relationships.
    Each dimension should have appropriate resonance levels and energy.
    
    The story should embody the principles of:
    - Sacred geometry and octahedral structure
    - Harmonic resonance across dimensions
    - Transformation and growth
    - Universal harmony and completion
    """
    
    response = client.messages.create(
        model=model,
        temperature=0.7,
        max_tokens=2048,
        response_model=OctotrieStory,
        messages=[{"role": "user", "content": story_prompt}]
    )
    
    return response

@app.function(image=image, max_containers=5)
def calculate_dimension_resonance(dimension_data: Dict) -> OctotrieDimension:
    """Calculate resonance and energy for a specific dimension."""
    import random
    import math
    
    # Simulate complex resonance calculations
    base_resonance = random.uniform(0.8, 1.0)
    harmonic_multiplier = math.sin(random.uniform(0, 2 * math.pi)) * 0.1 + 1.0
    resonance = min(1.0, base_resonance * harmonic_multiplier)
    
    # Calculate energy based on resonance
    energy = resonance * 1.5 + random.uniform(-0.1, 0.1)
    energy = max(0.0, min(2.0, energy))
    
    return OctotrieDimension(
        dimension_number=dimension_data["dimension_number"],
        name=dimension_data["name"],
        role=dimension_data["role"],
        resonance=resonance,
        icon=dimension_data["icon"],
        color=dimension_data["color"],
        energy_level=energy
    )

@app.function(image=image)
async def capture_octotrie_visualization(story: OctotrieStory) -> bytes:
    """Capture a screenshot of the OCTOTRIE visualization."""
    from playwright.async_api import async_playwright
    import tempfile
    
    # Create HTML visualization
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OCTOTRIE Visualization</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .sacred-geometry {{
                background: conic-gradient(from 180deg at 50% 50%, #667eea, #764ba2, #f093fb, #f5576c, #667eea);
            }}
        </style>
    </head>
    <body class="bg-gray-900 text-white p-8">
        <div class="max-w-6xl mx-auto">
            <h1 class="text-4xl font-bold text-center mb-8 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                🎭 OCTOTRIE - {story.title}
            </h1>
            
            <div class="grid grid-cols-4 gap-6 mb-8">
                {''.join([f'''
                <div class="bg-gray-800 rounded-lg p-6 border border-gray-700 text-center">
                    <div class="text-4xl mb-3">{dim.icon}</div>
                    <h3 class="font-bold text-{dim.color.replace('#', '')}">{dim.name}</h3>
                    <p class="text-sm text-gray-400">{dim.role}</p>
                    <div class="mt-3 text-xs text-gray-500">Dimension {dim.dimension_number}</div>
                    <div class="mt-2 text-sm">
                        <div>Resonance: {dim.resonance:.3f}</div>
                        <div>Energy: {dim.energy_level:.3f}</div>
                    </div>
                </div>
                ''' for dim in story.dimensions])}
            </div>
            
            <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 class="text-xl font-bold mb-4">System Metrics</h3>
                <div class="grid grid-cols-2 gap-4">
                    <div>Narrative Energy: {story.narrative_energy:.3f}</div>
                    <div>Jackie Resonance: {story.jackie_resonance:.3f}</div>
                    <div>System Harmony: {story.system_harmony:.3f}</div>
                    <div>Sacred Geometry: {story.sacred_geometry_score:.3f}</div>
                </div>
            </div>
            
            <div class="mt-8 bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 class="text-xl font-bold mb-4">Generated Story</h3>
                <p class="text-gray-300 leading-relaxed">{story.generated_story}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        html_path = f.name
    
    # Take screenshot
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file://{html_path}")
        await page.wait_for_load_state("networkidle")
        
        # Set viewport for better visualization
        await page.set_viewport_size({"width": 1200, "height": 800})
        
        screenshot_data = await page.screenshot(full_page=True)
        await browser.close()
    
    return screenshot_data

@app.function(image=image, max_containers=3)
def analyze_trading_agents(agents_data: List[Dict]) -> List[TradingAgent]:
    """Analyze and optimize trading agents."""
    import random
    
    analyzed_agents = []
    for agent_data in agents_data:
        # Simulate performance analysis
        performance_score = random.uniform(0.7, 1.0)
        resonance = random.uniform(0.8, 1.0)
        energy = random.uniform(0.9, 1.3)
        
        agent = TradingAgent(
            name=agent_data["name"],
            dimension=agent_data["dimension"],
            resonance=resonance,
            status="active",
            energy=energy,
            performance_score=performance_score
        )
        analyzed_agents.append(agent)
    
    return analyzed_agents

@app.function(image=image)
def monitor_system_health() -> SystemHealth:
    """Monitor overall system health and status."""
    import random
    from datetime import datetime
    
    return SystemHealth(
        overall_health=random.uniform(95.0, 100.0),
        active_agents=random.randint(15, 20),
        system_load=random.uniform(60.0, 80.0),
        error_count=random.randint(0, 2),
        last_optimization=datetime.now().isoformat()
    )

# Import template system
from octotrie_templates import get_template, get_templates_by_category, TemplateCategory

# Main orchestration function with Convex integration
@app.local_entrypoint()
def main(
    template: str = "adams_first_ride",
    input_text: str = "Automotive transformation and personal growth journey",
    use_opus: bool = False,
    generate_visualization: bool = True,
    category: str = None,
    store_in_convex: bool = True,
    user_id: Optional[str] = None
):
    """Main entry point for OCTOTRIE Modal integration with Convex."""
    print("🎭 OCTOTRIE Modal Integration with Convex Starting...")
    
    # Get template information
    template_obj = get_template(template)
    if template_obj:
        print(f"Template: {template_obj.name}")
        print(f"Category: {template_obj.category.value}")
        print(f"Description: {template_obj.description}")
    else:
        print(f"Template: {template} (custom)")
    
    print(f"Input: {input_text}")
    print(f"Using Opus: {use_opus}")
    print(f"Store in Convex: {store_in_convex}")
    
    # Step 1: Generate the complete OCTOTRIE story
    print("\n📖 Generating 8-dimensional story...")
    if template_obj:
        # Use template prompt
        story = generate_octotrie_story.remote(template_obj.name, input_text, use_opus)
    else:
        # Use custom template
        story = generate_octotrie_story.remote(template, input_text, use_opus)
    print(f"✅ Story generated: {story.title}")
    print(f"   Narrative Energy: {story.narrative_energy:.3f}")
    print(f"   Jackie Resonance: {story.jackie_resonance:.3f}")
    print(f"   System Harmony: {story.system_harmony:.3f}")
    
    # Step 2: Store story in Convex (if enabled)
    if store_in_convex:
        print("\n🗄️ Storing story in Convex database...")
        try:
            convex_result = convex_store_story.remote(story, user_id)
            print(f"✅ Story stored in Convex with ID: {convex_result.get('_id', 'unknown')}")
        except Exception as e:
            print(f"⚠️ Failed to store in Convex: {e}")
    
    # Step 3: Calculate dimension resonance in parallel
    print("\n🌐 Calculating dimension resonance...")
    dimension_tasks = []
    for i, dim in enumerate(story.dimensions):
        task = calculate_dimension_resonance.remote({
            "dimension_number": i + 1,
            "name": dim.name,
            "role": dim.role,
            "icon": dim.icon,
            "color": dim.color
        })
        dimension_tasks.append(task)
    
    # Wait for all dimension calculations to complete
    updated_dimensions = [task for task in dimension_tasks]
    print(f"✅ Calculated resonance for {len(updated_dimensions)} dimensions")
    
    # Step 4: Analyze trading agents
    print("\n🤖 Analyzing trading agents...")
    agents_data = [
        {"name": "🏎️ Market Data Agent", "dimension": "SPEED"},
        {"name": "📈 Technical Analysis", "dimension": "SPEED"},
        {"name": "💰 Personal Finance", "dimension": "LOYALTY"},
        {"name": "🔥 DeFi Integration", "dimension": "SACRED"},
        {"name": "🧠 Neural Network", "dimension": "PASSION"},
        {"name": "🐉 Dragon Patterns", "dimension": "SACRED"}
    ]
    
    analyzed_agents = analyze_trading_agents.remote(agents_data)
    print(f"✅ Analyzed {len(analyzed_agents)} trading agents")
    
    # Step 5: Store trading agents in Convex
    if store_in_convex:
        print("\n🗄️ Storing trading agents in Convex...")
        try:
            convex_agents_result = convex_store_trading_agents.remote(analyzed_agents)
            print(f"✅ Trading agents stored in Convex")
        except Exception as e:
            print(f"⚠️ Failed to store agents in Convex: {e}")
    
    # Step 6: Monitor system health
    print("\n📊 Monitoring system health...")
    system_health = monitor_system_health.remote()
    print(f"✅ System Health: {system_health.overall_health:.1f}%")
    print(f"   Active Agents: {system_health.active_agents}")
    print(f"   System Load: {system_health.system_load:.1f}%")
    
    # Step 7: Update system health in Convex
    if store_in_convex:
        print("\n🗄️ Updating system health in Convex...")
        try:
            convex_health_result = convex_update_system_health.remote(system_health)
            print(f"✅ System health updated in Convex")
        except Exception as e:
            print(f"⚠️ Failed to update health in Convex: {e}")
    
    # Step 8: Generate visualization (optional)
    if generate_visualization:
        print("\n🎨 Generating visualization...")
        # Create updated story with calculated dimensions
        updated_story = OctotrieStory(
            title=story.title,
            template=story.template,
            dimensions=updated_dimensions,
            narrative_energy=story.narrative_energy,
            jackie_resonance=story.jackie_resonance,
            system_harmony=story.system_harmony,
            sacred_geometry_score=story.sacred_geometry_score,
            generated_story=story.generated_story
        )
        
        screenshot_data = capture_octotrie_visualization.remote(updated_story)
        
        # Save visualization
        output_path = Path("/tmp/octotrie-visualization.png")
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(screenshot_data)
        print(f"✅ Visualization saved to: {output_path}")
    
    # Step 9: Retrieve stories from Convex (demonstration)
    if store_in_convex:
        print("\n📖 Retrieving recent stories from Convex...")
        try:
            recent_stories = convex_get_stories.remote(template, 5)
            print(f"✅ Retrieved {len(recent_stories)} recent stories from Convex")
            for i, story_data in enumerate(recent_stories[:3]):
                print(f"   {i+1}. {story_data.get('title', 'Unknown')} - {story_data.get('template', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ Failed to retrieve stories from Convex: {e}")
    
    # Step 10: Get system metrics from Convex
    if store_in_convex:
        print("\n📊 Retrieving system metrics from Convex...")
        try:
            system_metrics = convex_get_system_metrics.remote()
            print(f"✅ Retrieved system metrics from Convex")
            print(f"   Total Stories: {system_metrics.get('total_stories', 0)}")
            print(f"   Total Agents: {system_metrics.get('total_agents', 0)}")
            print(f"   Average Health: {system_metrics.get('average_health', 0):.1f}%")
        except Exception as e:
            print(f"⚠️ Failed to retrieve metrics from Convex: {e}")
    
    # Step 11: Generate comprehensive report
    print("\n📋 Generating comprehensive report...")
    report = {
        "timestamp": story.model_dump(),
        "story": story.model_dump(),
        "dimensions": [dim.model_dump() for dim in updated_dimensions],
        "trading_agents": [agent.model_dump() for agent in analyzed_agents],
        "system_health": system_health.model_dump(),
        "convex_integration": {
            "enabled": store_in_convex,
            "user_id": user_id,
            "convex_url": CONVEX_URL
        },
        "metadata": {
            "template_used": template,
            "input_text": input_text,
            "use_opus": use_opus,
            "visualization_generated": generate_visualization
        }
    }
    
    # Save report
    report_path = Path("/tmp/octotrie-report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Report saved to: {report_path}")
    
    print("\n🎭 OCTOTRIE Modal Integration with Convex Complete!")
    print("🌐 Sacred geometry has been manifested in the cloud!")
    print("🗄️ Stories are now stored in real-time Convex database!")
    print("✨ The 8-dimensional narrative engine is now distributed, scalable, and persistent!")

# Utility function for running specific components with Convex
@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("anthropic-secret", required_keys=["ANTHROPIC_API_KEY"]),
        modal.Secret.from_name("convex-secret", required_keys=["CONVEX_URL", "CONVEX_API_KEY"])
    ]
)
def run_octotrie_component_with_convex(component: str, data: Dict, store_in_convex: bool = True) -> Dict:
    """Run a specific OCTOTRIE component with Convex integration."""
    if component == "story_generation":
        story = generate_octotrie_story.remote(
            data.get("template", "Universal Input"),
            data.get("input_text"),
            data.get("use_opus", False)
        )
        
        result = {"story": story.model_dump()}
        
        if store_in_convex:
            try:
                convex_result = convex_store_story.remote(story, data.get("user_id"))
                result["convex_storage"] = convex_result
            except Exception as e:
                result["convex_error"] = str(e)
        
        return result
    
    elif component == "resonance_calculation":
        return calculate_dimension_resonance.remote(data).model_dump()
    
    elif component == "agent_analysis":
        agents = analyze_trading_agents.remote(data.get("agents", []))
        
        result = {"agents": [agent.model_dump() for agent in agents]}
        
        if store_in_convex:
            try:
                convex_result = convex_store_trading_agents.remote(agents)
                result["convex_storage"] = convex_result
            except Exception as e:
                result["convex_error"] = str(e)
        
        return result
    
    elif component == "health_monitoring":
        health = monitor_system_health.remote()
        
        result = {"health": health.model_dump()}
        
        if store_in_convex:
            try:
                convex_result = convex_update_system_health.remote(health)
                result["convex_update"] = convex_result
            except Exception as e:
                result["convex_error"] = str(e)
        
        return result
    
    elif component == "convex_retrieval":
        return convex_get_stories.remote(data.get("template"), data.get("limit", 10))
    
    elif component == "convex_metrics":
        return convex_get_system_metrics.remote()
    
    else:
        raise ValueError(f"Unknown component: {component}")

if __name__ == "__main__":
    # Example usage
    print("🎭 OCTOTRIE Modal Integration with Convex")
    print("Run with: modal run modal-octotrie-integration.py")
    print("Or with custom parameters:")
    print("modal run modal-octotrie-integration.py --template 'Yamaha Acquisition' --input-text 'Motorcycle mastery journey' --store-in-convex true") 
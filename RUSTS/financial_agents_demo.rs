use lobster::financial_agents::*;
use lobster::financial_agents::base::*;
use lobster::financial_agents::market_data::*;
use lobster::financial_agents::sentiment::*;
use lobster::financial_agents::technical::*;
use lobster::financial_agents::portfolio::*;
use lobster::financial_agents::execution::*;
use lobster::financial_agents::risk::*;
use lobster::financial_agents::defi::*;
use lobster::financial_agents::performance::*;
use std::collections::HashMap;
use tokio;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize logging
    env_logger::init();
    
    println!("🦞 Lobster Financial Agent System Demo");
    println!("======================================");
    
    // Create agent coordinator
    let mut coordinator = AgentCoordinator::new();
    
    // Demo 1: Create and start market data agent
    println!("\n📊 Creating Market Data Agent...");
    let mut market_agent = MarketDataAgent::new(vec!["equities".to_string(), "crypto".to_string()]);
    
    // Add some instruments
    market_agent.add_instrument(Instrument {
        id: "AAPL".to_string(),
        symbol: "AAPL".to_string(),
        asset_class: "equity".to_string(),
        exchange: "NASDAQ".to_string(),
        currency: "USD".to_string(),
    });
    
    market_agent.add_instrument(Instrument {
        id: "BTC".to_string(),
        symbol: "BTC".to_string(),
        asset_class: "crypto".to_string(),
        exchange: "Coinbase".to_string(),
        currency: "USD".to_string(),
    });
    
    // Set movement thresholds
    market_agent.set_movement_threshold("AAPL".to_string(), 2.0); // 2% threshold
    market_agent.set_movement_threshold("BTC".to_string(), 5.0);  // 5% threshold
    
    // Process some mock tick data
    let tick_data = TickData {
        instrument_id: "AAPL".to_string(),
        price: 150.0,
        volume: 1000.0,
        timestamp: Timestamp::now(),
        order_book: Some(OrderBook {
            bids: vec![PriceLevel { price: 149.95, size: 500.0 }],
            asks: vec![PriceLevel { price: 150.05, size: 500.0 }],
            timestamp: Timestamp::now(),
        }),
    };
    
    market_agent.process_tick_data(tick_data)?;
    println!("✅ Market data agent processed tick data successfully");
    
    // Demo 2: Technical Analysis Agent
    println!("\n📈 Creating Technical Analysis Agent...");
    let mut tech_agent = TechnicalAnalysisAgent::new(
        vec!["AAPL".to_string(), "BTC".to_string()],
        vec![TimeFrame::H1, TimeFrame::D1],
    );
    
    tech_agent.set_signal_threshold("golden_cross".to_string(), 0.8);
    println!("✅ Technical analysis agent configured");
    
    // Demo 3: Personal Finance Agent (FIRE Planning)
    println!("\n💰 Creating Personal Finance Agent for FIRE Planning...");
    
    let risk_profile = RiskProfile {
        risk_tolerance: 0.7,     // Moderately aggressive
        time_horizon: 20,        // 20 years
        liquidity_needs: 0.1,    // 10% needs to be liquid
        income_stability: 0.8,   // Stable income
    };
    
    let cash_flow_model = CashFlowModel {
        monthly_income: 8000.0,
        monthly_expenses: 4000.0,
        projected_income_growth: 0.03,  // 3% annual growth
        projected_expense_growth: 0.02, // 2% annual growth
        discretionary_income: 2000.0,   // $2k available for investing
    };
    
    let mut finance_agent = PersonalFinanceAgent::new(
        "user123".to_string(),
        risk_profile,
        cash_flow_model,
    );
    
    // Add a financial goal
    finance_agent.add_goal(FinancialGoal {
        id: "fire_goal".to_string(),
        goal_type: GoalType::FinancialIndependence,
        target_amount: 1_000_000.0, // $1M target
        target_date: Timestamp(Timestamp::now().0 + (20 * 365 * 24 * 60 * 60)), // 20 years
        current_progress: 0.05,  // 5% complete
        priority: GoalPriority::High,
    });
    
    // Add a portfolio
    let mut positions = HashMap::new();
    positions.insert("VTI".to_string(), Position {
        instrument_id: "VTI".to_string(),
        quantity: 100.0,
        average_price: 200.0,
        current_price: 220.0,
        market_value: 22000.0,
        unrealized_pnl: 2000.0,
        realized_pnl: 0.0,
        last_updated: Timestamp::now(),
    });
    
    let portfolio = Portfolio {
        id: "main_portfolio".to_string(),
        owner_id: "user123".to_string(),
        positions,
        cash_balance: 10000.0,
        total_value: 32000.0,
        created_at: Timestamp::now(),
        last_updated: Timestamp::now(),
    };
    
    finance_agent.add_portfolio(portfolio);
    
    // Generate FIRE plan
    match finance_agent.optimize_for_financial_freedom() {
        Ok(fire_plan) => {
            println!("\n🔥 FIRE Plan Generated Successfully!");
            println!("   FI Number: ${:.0}", fire_plan.fi_number);
            println!("   Current Net Worth: ${:.0}", fire_plan.current_net_worth);
            println!("   Monthly Investment Target: ${:.0}", fire_plan.monthly_investment_target);
            println!("   Time to FI: {} months ({:.1} years)", fire_plan.time_to_fi, fire_plan.time_to_fi as f64 / 12.0);
            
            println!("\n📍 Milestones:");
            for milestone in &fire_plan.milestones {
                println!("   • {}", milestone.description);
            }
            
            println!("\n💡 Optimization Opportunities:");
            for opportunity in &fire_plan.optimization_opportunities {
                println!("   • {}: ${:.0}/month potential impact", 
                        opportunity.description, opportunity.potential_impact);
            }
        }
        Err(e) => {
            println!("❌ Failed to generate FIRE plan: {:?}", e);
        }
    }
    
    // Demo 4: Sentiment Analysis Agent
    println!("\n📰 Creating Sentiment Analysis Agent...");
    let sentiment_agent = SentimentAnalysisAgent::new(
        Box::new(BasicNLPProcessor),
        Box::new(BasicEntityRecognizer),
    );
    
    println!("✅ Sentiment analysis agent created");
    
    // Demo 5: Execution Agent
    println!("\n⚡ Creating Execution Agent...");
    let mut execution_agent = ExecutionAgent::new();
    
    // Add some trading venues
    execution_agent.add_venue(TradingVenue {
        id: "nasdaq".to_string(),
        name: "NASDAQ".to_string(),
        venue_type: VenueType::Exchange,
        supported_instruments: vec!["AAPL".to_string(), "MSFT".to_string()],
        fees: VenueFees {
            maker_fee: 0.0005, // 5 bps
            taker_fee: 0.001,  // 10 bps
            withdrawal_fee: None,
        },
        liquidity_score: 0.95,
    });
    
    // Create a sample order
    let order = Order {
        id: "order_001".to_string(),
        instrument_id: "AAPL".to_string(),
        side: OrderSide::Buy,
        order_type: OrderType::Limit,
        quantity: 100.0,
        price: Some(149.50),
        time_in_force: TimeInForce::GTC,
        created_at: Timestamp::now(),
        status: OrderStatus::Pending,
    };
    
    // Execute the order
    match execution_agent.execute_order(order).await {
        Ok(result) => {
            println!("✅ Order executed successfully!");
            println!("   Order ID: {}", result.order_id);
            println!("   Status: {}", result.status);
            println!("   Total Quantity: {}", result.total_quantity);
            println!("   Average Price: ${:.2}", result.average_price);
            println!("   Total Fees: ${:.2}", result.total_fees);
        }
        Err(e) => {
            println!("❌ Order execution failed: {:?}", e);
        }
    }
    
    // Demo 6: Risk Management
    println!("\n🛡️ Creating Risk Management System...");
    let risk_limits = RiskLimits {
        max_position_size: 50000.0,    // $50k max position
        max_portfolio_volatility: 0.20, // 20% max volatility
        max_drawdown: 0.15,            // 15% max drawdown
        max_concentration: 0.25,       // 25% max in single asset
        max_leverage: 2.0,             // 2x max leverage
    };
    
    let mut risk_monitor = SystemRiskMonitor::new(risk_limits);
    
    // Add portfolio for risk monitoring
    let risk_portfolio = Portfolio {
        id: "risk_portfolio".to_string(),
        owner_id: "user123".to_string(),
        positions: {
            let mut pos = HashMap::new();
            pos.insert("AAPL".to_string(), Position {
                instrument_id: "AAPL".to_string(),
                quantity: 200.0,
                average_price: 150.0,
                current_price: 155.0,
                market_value: 31000.0,
                unrealized_pnl: 1000.0,
                realized_pnl: 0.0,
                last_updated: Timestamp::now(),
            });
            pos
        },
        cash_balance: 19000.0,
        total_value: 50000.0,
        created_at: Timestamp::now(),
        last_updated: Timestamp::now(),
    };
    
    risk_monitor.add_portfolio(risk_portfolio);
    
    match risk_monitor.perform_system_check() {
        Ok(assessment) => {
            println!("✅ Risk assessment completed!");
            println!("   Overall Risk Level: {:.2}", assessment.overall_risk_level);
            println!("   Total Exposure: ${:.0}", assessment.total_exposure.total_value);
            println!("   Limit Breaches: {}", assessment.limit_breaches.len());
            println!("   Stress Test Scenarios: {}", assessment.stress_test_results.len());
        }
        Err(e) => {
            println!("❌ Risk assessment failed: {:?}", e);
        }
    }
    
    // Demo 7: DeFi Integration
    println!("\n🌐 Creating DeFi Integration Agent...");
    let mut defi_agent = DeFiIntegrationAgent::new();
    
    // Add mock protocol connectors
    defi_agent.add_protocol_connector("Aave".to_string(), Box::new(MockProtocolConnector::new("Aave".to_string())));
    defi_agent.add_protocol_connector("Compound".to_string(), Box::new(MockProtocolConnector::new("Compound".to_string())));
    
    let yield_params = YieldParameters {
        risk_tolerance: 0.5,
        min_yield: 0.03,  // 3% minimum yield
        time_period: 365, // 1 year
        max_lock_period: Some(365),
    };
    
    match defi_agent.optimize_yield(10000.0, "USDC".to_string(), yield_params) {
        Ok(strategy) => {
            println!("✅ DeFi yield strategy optimized!");
            println!("   Asset: {}", strategy.asset);
            println!("   Amount: ${:.0}", strategy.amount);
            println!("   Expected Yield: {:.2}%", strategy.expected_yield * 100.0);
            println!("   Risk Score: {:.2}", strategy.risk_score);
            println!("   Allocations: {}", strategy.allocations.len());
        }
        Err(e) => {
            println!("❌ DeFi optimization failed: {:?}", e);
        }
    }
    
    // Demo 8: Performance Evaluation
    println!("\n📊 Creating Performance Evaluation Agent...");
    let performance_agent = PerformanceEvaluationAgent::new();
    
    println!("✅ Performance evaluation agent created");
    
    // Summary
    println!("\n🎉 Demo Completed Successfully!");
    println!("=====================================");
    println!("The Lobster Financial Agent System demonstrates:");
    println!("• Real-time market data processing");
    println!("• Technical analysis with multiple indicators");
    println!("• Comprehensive FIRE planning and optimization");
    println!("• Multi-venue order execution");
    println!("• Advanced risk management and stress testing");
    println!("• DeFi yield optimization across protocols");
    println!("• Performance evaluation and improvement recommendations");
    println!("\nThis system can help achieve financial freedom through:");
    println!("🎯 Automated investment strategies");
    println!("💰 Passive income optimization");
    println!("📈 Risk-adjusted portfolio management");
    println!("🌍 Diversification across traditional and DeFi markets");
    
    Ok(())
} 
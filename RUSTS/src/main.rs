//! ACTORS Rust Components Demo
//! 
//! Demonstrates the usage of ACTORS Rust performance components.

use actors_rust_components::*;
use std::collections::HashMap;
use chrono::Utc;

fn main() {
    println!("🚀 ACTORS Rust Components Demo");
    
    // Initialize financial engine
    let engine = FinancialEngine::new(0.02); // 2% risk-free rate
    
    // Create sample positions
    let positions = vec![
        Position {
            id: uuid::Uuid::new_v4(),
            account_id: "demo-account".to_string(),
            symbol: "AAPL".to_string(),
            instrument_type: InstrumentType::Stock,
            quantity: 100.0,
            average_price: 150.0,
            current_price: 155.0,
            market_value: 15500.0,
            unrealized_pnl: 500.0,
            last_updated: Utc::now(),
        },
        Position {
            id: uuid::Uuid::new_v4(),
            account_id: "demo-account".to_string(),
            symbol: "GOOGL".to_string(),
            instrument_type: InstrumentType::Stock,
            quantity: 50.0,
            average_price: 200.0,
            current_price: 210.0,
            market_value: 10500.0,
            unrealized_pnl: 500.0,
            last_updated: Utc::now(),
        },
    ];
    
    // Calculate portfolio metrics
    let total_value = engine.calculate_portfolio_value(&positions);
    let total_pnl = engine.calculate_portfolio_pnl(&positions);
    
    println!("📊 Portfolio Analysis:");
    println!("  Total Value: ${:.2}", total_value);
    println!("  Total P&L: ${:.2}", total_pnl);
    
    for position in &positions {
        let weight = engine.calculate_position_weight(position, total_value);
        println!("  {}: ${:.2} ({:.1}%)", position.symbol, position.market_value, weight * 100.0);
    }
    
    // Test ML Pipeline
    let features = vec!["price".to_string(), "volume".to_string(), "volatility".to_string()];
    let pipeline = MLPipeline::new("v1.0".to_string(), features);
    
    let mut training_data = Vec::new();
    for i in 0..5 {
        let mut record = HashMap::new();
        record.insert("price".to_string(), 100.0 + i as f64 * 10.0);
        record.insert("volume".to_string(), 1000.0 + i as f64 * 100.0);
        record.insert("volatility".to_string(), 0.2 + i as f64 * 0.01);
        training_data.push(record);
    }
    
    match pipeline.process_training_data(&training_data) {
        Ok(processed) => {
            println!("\n🤖 ML Pipeline Results:");
            println!("  Processed {} records with {} features", processed.len(), processed[0].len());
            
            for (i, record) in processed.iter().enumerate() {
                match pipeline.predict(record) {
                    Ok(prediction) => println!("  Record {}: Prediction = {:.4}", i, prediction),
                    Err(e) => println!("  Record {}: Error = {}", i, e),
                }
            }
            
            let importance = pipeline.get_feature_importance();
            println!("  Feature Importance:");
            for (feature, importance) in importance {
                println!("    {}: {:.4}", feature, importance);
            }
        }
        Err(e) => println!("ML Pipeline Error: {}", e),
    }
    
    // Test System Monitor
    let mut monitor = SystemMonitor::new(5);
    
    for i in 0..3 {
        let metrics = PerformanceMetrics {
            processing_time_ms: 100 + i * 10,
            memory_usage_mb: 50.0 + i as f64 * 5.0,
            cpu_usage_percent: 25.0 + i as f64 * 2.0,
            throughput_ops_per_sec: 1000.0 - i as f64 * 50.0,
            error_rate: 0.01 + i as f64 * 0.005,
            timestamp: Utc::now(),
        };
        
        monitor.record_metrics(metrics);
    }
    
    if let Some(avg_metrics) = monitor.get_average_metrics() {
        println!("\n📈 System Performance:");
        println!("  Avg Processing Time: {}ms", avg_metrics.processing_time_ms);
        println!("  Avg Memory Usage: {:.1}MB", avg_metrics.memory_usage_mb);
        println!("  Avg CPU Usage: {:.1}%", avg_metrics.cpu_usage_percent);
        println!("  Avg Throughput: {:.0} ops/sec", avg_metrics.throughput_ops_per_sec);
        println!("  Avg Error Rate: {:.3}%", avg_metrics.error_rate * 100.0);
    }
    
    println!("\n✅ Demo completed successfully!");
}

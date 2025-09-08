use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

use crate::types::*;
use crate::errors::{QuizError, QuizResult};

/// Manages machine learning pipelines and predictions
pub struct MLPipelineManager {
    models: Arc<RwLock<HashMap<String, Box<dyn MLModel + Send + Sync>>>>,
    is_active: Arc<RwLock<bool>>,
    predictor_cache: Arc<RwLock<HashMap<String, MLPredictions>>>,
}

impl MLPipelineManager {
    /// Create a new ML pipeline manager
    pub fn new() -> Self {
        Self {
            models: Arc::new(RwLock::new(HashMap::new())),
            is_active: Arc::new(RwLock::new(false)),
            predictor_cache: Arc::new(RwLock::new(HashMap::new())),
        }
    }
    
    /// Initialize the ML pipeline
    pub async fn initialize(&self) -> QuizResult<()> {
        // Load ML models
        self.load_models().await?;
        
        // Mark as active
        let mut is_active = self.is_active.write().await;
        *is_active = true;
        
        tracing::info!("ML Pipeline Manager initialized");
        Ok(())
    }
    
    /// Activate the ML pipeline
    pub async fn activate(&self) -> QuizResult<()> {
        let mut is_active = self.is_active.write().await;
        *is_active = true;
        Ok(())
    }
    
    /// Generate predictions based on responses and personality profile
    pub async fn generate_predictions(
        &self,
        responses: &[String],
        personality_profile: &PersonalityProfile,
    ) -> QuizResult<MLPredictions> {
        let is_active = *self.is_active.read().await;
        if !is_active {
            return Ok(MLPredictions::default());
        }
        
        // Check cache first
        let cache_key = self.create_cache_key(responses, personality_profile);
        {
            let cache = self.predictor_cache.read().await;
            if let Some(cached_predictions) = cache.get(&cache_key) {
                return Ok(cached_predictions.clone());
            }
        }
        
        // Generate predictions in parallel
        let (behavior_predictions, career_predictions, relationship_predictions, learning_predictions) = tokio::join!(
            self.predict_behaviors(responses, personality_profile),
            self.predict_career_paths(responses, personality_profile),
            self.predict_relationship_dynamics(responses, personality_profile),
            self.predict_learning_styles(responses, personality_profile)
        );
        
        let predictions = MLPredictions {
            predicted_behaviors: behavior_predictions?,
            career_paths: career_predictions?,
            relationship_dynamics: relationship_predictions?,
            learning_styles: learning_predictions?,
            confidence_scores: self.calculate_prediction_confidence(responses, personality_profile).await?,
        };
        
        // Cache the predictions
        {
            let mut cache = self.predictor_cache.write().await;
            cache.insert(cache_key, predictions.clone());
        }
        
        Ok(predictions)
    }
    
    /// Get health score for the ML pipeline
    pub async fn get_health_score(&self) -> f64 {
        let is_active = *self.is_active.read().await;
        if is_active { 1.0 } else { 0.0 }
    }
    
    // MARK: - Private Methods
    
    /// Load ML models
    async fn load_models(&self) -> QuizResult<()> {
        let mut models = self.models.write().await;
        
        // Load behavior prediction model
        models.insert("behavior".to_string(), Box::new(BehaviorPredictionModel::new()));
        
        // Load career prediction model
        models.insert("career".to_string(), Box::new(CareerPredictionModel::new()));
        
        // Load relationship prediction model
        models.insert("relationship".to_string(), Box::new(RelationshipPredictionModel::new()));
        
        // Load learning style prediction model
        models.insert("learning".to_string(), Box::new(LearningStylePredictionModel::new()));
        
        Ok(())
    }
    
    /// Create cache key for predictions
    fn create_cache_key(&self, responses: &[String], profile: &PersonalityProfile) -> String {
        use sha2::{Sha256, Digest};
        
        let mut hasher = Sha256::new();
        hasher.update(responses.join("|"));
        hasher.update(serde_json::to_string(profile).unwrap_or_default());
        format!("{:x}", hasher.finalize())
    }
    
    /// Predict behaviors
    async fn predict_behaviors(
        &self,
        responses: &[String],
        profile: &PersonalityProfile,
    ) -> QuizResult<Vec<String>> {
        // Analyze personality traits to predict behaviors
        let mut behaviors = Vec::new();
        
        // Based on Big Five traits
        if let Some(&openness) = profile.big_five_traits.get(&PersonalityTrait::Openness) {
            if openness > 0.6 {
                behaviors.push("Creative".to_string());
                behaviors.push("Innovative".to_string());
            }
        }
        
        if let Some(&conscientiousness) = profile.big_five_traits.get(&PersonalityTrait::Conscientiousness) {
            if conscientiousness > 0.7 {
                behaviors.push("Organized".to_string());
                behaviors.push("Reliable".to_string());
            } else {
                behaviors.push("Flexible".to_string());
                behaviors.push("Spontaneous".to_string());
            }
        }
        
        if let Some(&extraversion) = profile.big_five_traits.get(&PersonalityTrait::Extraversion) {
            if extraversion > 0.6 {
                behaviors.push("Social".to_string());
                behaviors.push("Outgoing".to_string());
            } else {
                behaviors.push("Independent".to_string());
                behaviors.push("Thoughtful".to_string());
            }
        }
        
        // Default behaviors if none detected
        if behaviors.is_empty() {
            behaviors.extend_from_slice(&["Adaptive".to_string(), "Analytical".to_string()]);
        }
        
        Ok(behaviors)
    }
    
    /// Predict career paths
    async fn predict_career_paths(
        &self,
        responses: &[String],
        profile: &PersonalityProfile,
    ) -> QuizResult<Vec<String>> {
        let mut career_paths = Vec::new();
        
        // Analyze traits for career alignment
        let openness = profile.big_five_traits.get(&PersonalityTrait::Openness).unwrap_or(&0.5);
        let conscientiousness = profile.big_five_traits.get(&PersonalityTrait::Conscientiousness).unwrap_or(&0.5);
        let extraversion = profile.big_five_traits.get(&PersonalityTrait::Extraversion).unwrap_or(&0.5);
        
        // High openness suggests creative fields
        if *openness > 0.7 {
            career_paths.push("Creative Arts".to_string());
            career_paths.push("Design".to_string());
            career_paths.push("Innovation".to_string());
        }
        
        // High conscientiousness suggests structured fields
        if *conscientiousness > 0.7 {
            career_paths.push("Management".to_string());
            career_paths.push("Finance".to_string());
            career_paths.push("Operations".to_string());
        }
        
        // High extraversion suggests people-focused fields
        if *extraversion > 0.7 {
            career_paths.push("Sales".to_string());
            career_paths.push("Marketing".to_string());
            career_paths.push("Leadership".to_string());
        }
        
        // Technical orientation for analytical types
        if profile.neural_insights.get("analytical_thinking").unwrap_or(&0.5) > &0.6 {
            career_paths.push("Technology".to_string());
            career_paths.push("Research".to_string());
            career_paths.push("Engineering".to_string());
        }
        
        // Default if no specific alignment
        if career_paths.is_empty() {
            career_paths.extend_from_slice(&["General Business".to_string(), "Consulting".to_string()]);
        }
        
        Ok(career_paths)
    }
    
    /// Predict relationship dynamics
    async fn predict_relationship_dynamics(
        &self,
        responses: &[String],
        profile: &PersonalityProfile,
    ) -> QuizResult<Vec<String>> {
        let mut dynamics = Vec::new();
        
        let agreeableness = profile.big_five_traits.get(&PersonalityTrait::Agreeableness).unwrap_or(&0.5);
        let extraversion = profile.big_five_traits.get(&PersonalityTrait::Extraversion).unwrap_or(&0.5);
        let emotional_intelligence = profile.emotional_intelligence;
        
        // High agreeableness suggests cooperative dynamics
        if *agreeableness > 0.6 {
            dynamics.push("Cooperative".to_string());
            dynamics.push("Supportive".to_string());
        } else {
            dynamics.push("Independent".to_string());
            dynamics.push("Direct".to_string());
        }
        
        // High EI suggests empathetic relationships
        if emotional_intelligence > 0.7 {
            dynamics.push("Empathetic".to_string());
            dynamics.push("Understanding".to_string());
        }
        
        // Extraversion affects social dynamics
        if *extraversion > 0.6 {
            dynamics.push("Social".to_string());
            dynamics.push("Engaging".to_string());
        } else {
            dynamics.push("Intimate".to_string());
            dynamics.push("Deep".to_string());
        }
        
        Ok(dynamics)
    }
    
    /// Predict learning styles
    async fn predict_learning_styles(
        &self,
        responses: &[String],
        profile: &PersonalityProfile,
    ) -> QuizResult<Vec<String>> {
        let mut styles = Vec::new();
        
        let openness = profile.big_five_traits.get(&PersonalityTrait::Openness).unwrap_or(&0.5);
        let conscientiousness = profile.big_five_traits.get(&PersonalityTrait::Conscientiousness).unwrap_or(&0.5);
        
        // High openness suggests experiential learning
        if *openness > 0.6 {
            styles.push("Experiential".to_string());
            styles.push("Creative".to_string());
        }
        
        // High conscientiousness suggests structured learning
        if *conscientiousness > 0.6 {
            styles.push("Structured".to_string());
            styles.push("Sequential".to_string());
        } else {
            styles.push("Flexible".to_string());
            styles.push("Adaptive".to_string());
        }
        
        // Analyze Jungian preferences for learning modalities
        if let Some(&sensing) = profile.jungian_types.get(&JungianType::Sensing) {
            if sensing > 0.6 {
                styles.push("Hands-on".to_string());
                styles.push("Practical".to_string());
            }
        }
        
        if let Some(&intuitive) = profile.jungian_types.get(&JungianType::Intuitive) {
            if intuitive > 0.6 {
                styles.push("Conceptual".to_string());
                styles.push("Theoretical".to_string());
            }
        }
        
        // Default learning styles
        if styles.is_empty() {
            styles.extend_from_slice(&["Visual".to_string(), "Auditory".to_string()]);
        }
        
        Ok(styles)
    }
    
    /// Calculate confidence scores for predictions
    async fn calculate_prediction_confidence(
        &self,
        responses: &[String],
        profile: &PersonalityProfile,
    ) -> QuizResult<HashMap<String, f64>> {
        let mut confidence_scores = HashMap::new();
        
        // Base confidence on response count and profile completeness
        let response_quality = (responses.len() as f64 / 20.0).min(1.0);
        let profile_completeness = if profile.big_five_traits.len() == 5 { 1.0 } else { 0.7 };
        
        let base_confidence = (response_quality + profile_completeness) / 2.0;
        
        confidence_scores.insert("behaviors".to_string(), base_confidence * 0.85);
        confidence_scores.insert("career".to_string(), base_confidence * 0.78);
        confidence_scores.insert("relationships".to_string(), base_confidence * 0.82);
        confidence_scores.insert("learning".to_string(), base_confidence * 0.79);
        
        Ok(confidence_scores)
    }
}

// MARK: - ML Model Trait and Implementations

/// Trait for ML models
trait MLModel {
    fn model_type(&self) -> &str;
    fn predict(&self, input: &[f32]) -> Vec<f32>;
}

/// Behavior prediction model
struct BehaviorPredictionModel;

impl BehaviorPredictionModel {
    fn new() -> Self {
        Self
    }
}

impl MLModel for BehaviorPredictionModel {
    fn model_type(&self) -> &str {
        "behavior_prediction"
    }
    
    fn predict(&self, input: &[f32]) -> Vec<f32> {
        // Placeholder implementation
        vec![0.8, 0.6, 0.7] // Example prediction scores
    }
}

/// Career prediction model
struct CareerPredictionModel;

impl CareerPredictionModel {
    fn new() -> Self {
        Self
    }
}

impl MLModel for CareerPredictionModel {
    fn model_type(&self) -> &str {
        "career_prediction"
    }
    
    fn predict(&self, input: &[f32]) -> Vec<f32> {
        // Placeholder implementation
        vec![0.75, 0.82, 0.68]
    }
}

/// Relationship prediction model
struct RelationshipPredictionModel;

impl RelationshipPredictionModel {
    fn new() -> Self {
        Self
    }
}

impl MLModel for RelationshipPredictionModel {
    fn model_type(&self) -> &str {
        "relationship_prediction"
    }
    
    fn predict(&self, input: &[f32]) -> Vec<f32> {
        // Placeholder implementation
        vec![0.73, 0.77, 0.85]
    }
}

/// Learning style prediction model
struct LearningStylePredictionModel;

impl LearningStylePredictionModel {
    fn new() -> Self {
        Self
    }
}

impl MLModel for LearningStylePredictionModel {
    fn model_type(&self) -> &str {
        "learning_style_prediction"
    }
    
    fn predict(&self, input: &[f32]) -> Vec<f32> {
        // Placeholder implementation
        vec![0.71, 0.79, 0.66]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_ml_pipeline_creation() {
        let pipeline = MLPipelineManager::new();
        assert!(!*pipeline.is_active.read().await);
    }
    
    #[tokio::test]
    async fn test_ml_pipeline_initialization() {
        let pipeline = MLPipelineManager::new();
        let result = pipeline.initialize().await;
        assert!(result.is_ok());
        assert!(*pipeline.is_active.read().await);
    }
    
    #[tokio::test]
    async fn test_behavior_prediction() {
        let pipeline = MLPipelineManager::new();
        pipeline.initialize().await.unwrap();
        
        let responses = vec!["I am creative".to_string(), "I like to organize".to_string()];
        let profile = PersonalityProfile::default();
        
        let behaviors = pipeline.predict_behaviors(&responses, &profile).await.unwrap();
        assert!(!behaviors.is_empty());
    }
    
    #[tokio::test]
    async fn test_career_prediction() {
        let pipeline = MLPipelineManager::new();
        pipeline.initialize().await.unwrap();
        
        let responses = vec!["I enjoy analytical work".to_string()];
        let profile = PersonalityProfile::default();
        
        let careers = pipeline.predict_career_paths(&responses, &profile).await.unwrap();
        assert!(!careers.is_empty());
    }
    
    #[tokio::test]
    async fn test_full_predictions() {
        let pipeline = MLPipelineManager::new();
        pipeline.initialize().await.unwrap();
        
        let responses = vec!["I am creative and analytical".to_string()];
        let profile = PersonalityProfile::default();
        
        let predictions = pipeline.generate_predictions(&responses, &profile).await.unwrap();
        
        assert!(!predictions.predicted_behaviors.is_empty());
        assert!(!predictions.career_paths.is_empty());
        assert!(!predictions.relationship_dynamics.is_empty());
        assert!(!predictions.learning_styles.is_empty());
        assert!(!predictions.confidence_scores.is_empty());
    }
} 
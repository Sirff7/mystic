use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize)]
pub struct SignupRequest {
    pub email: String,
    pub password: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SignupResponse {
    user_id: i32,
}

#[derive(Debug, Clone, Serialize)]
pub struct LoginRequest {
    pub email: String,
    pub password: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct UpdateProfileRequest {
    pub profile_id: i32,
    pub display_name: String,
    pub bio: String,
    pub zodiac: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct DiscoveryRequest {
    pub profile_id: i32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DiscoveryResponse {
    pub profile_id: i32,
    pub display_name: String,
    pub bio: String,
    pub zodiac: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct LikeRequest {
    pub liker_id: i32,
    pub liked_id: i32,
    pub status: i32,
}

#[derive(Debug, Clone, Serialize)]
pub struct CouplesRequest {
    pub profile_id: i32,
    pub index: i32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct MatchResponse {
    pub display_name: String,
    pub zodiac: String,
    pub bio: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ProfileResponse {
    pub profile_id: i32,
    pub display_name: String,
    pub bio: String,
    pub zodiac: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct ProfileRequest {
    pub profile_id: i32,
}

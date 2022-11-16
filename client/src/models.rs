use serde::{
    Deserialize,
    Serialize,
};

/// Struct for tasks received from the server
#[derive(Serialize, Deserialize, Debug)]
pub struct Task {
    pub data: String,
    pub max_delay: u32,
    pub min_delay: u32,
    pub name: String,
}

/// Struct for authorization credentials received from the server
#[derive(Serialize, Deserialize, Debug)]
pub struct Auth {
    #[serde(rename(serialize = "Authorization", deserialize = "Authorization"))]
    pub authorization: String,
}
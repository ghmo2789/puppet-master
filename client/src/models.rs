use serde::{
    Deserialize,
    Serialize,
};

#[derive(Serialize, Deserialize, Debug)]
pub struct SystemInformation {
    pub os_name: String,
    pub os_version: String,
    pub hostname: String,
    pub host_user: String,
    pub privileges: String,
}

/// Struct for tasks received from the server
#[derive(Serialize, Deserialize, Debug)]
pub struct Task {
    pub id: String,
    pub data: String,
    pub max_delay: u32,
    pub min_delay: u32,
    pub name: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TaskResult {
    pub id: String,
    pub status: i32,
    pub result: String,
}

/// Struct for authorization credentials received from the server
#[derive(Serialize, Deserialize, Debug)]
pub struct Auth {
    #[serde(rename(serialize = "Authorization", deserialize = "Authorization"))]
    pub authorization: String,
}

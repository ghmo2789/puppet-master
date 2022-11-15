use std::{
    time::Duration
};
use reqwest::Client;
use reqwest::header::CONTENT_TYPE;
use serde::{
    Deserialize,
    Serialize,
};

// Note that URL is set by environment variable during compilation
const URL: &'static str = env!("URL");
const TIMEOUT: Duration = Duration::from_secs(5);

#[derive(Serialize, Deserialize, Debug)]
struct Auth {
    #[serde(rename(serialize = "Authorization", deserialize = "Authorization"))]
    authorization: String,
}

/// Sends the clients identifying characteristics to the control server.
///
/// Returns the authorization token received from the control server.
///
/// # Errors
/// This function fails if there are issues sending the request, or if 200 is not returned from
/// the server
pub async fn send_identity(id_json: String) -> Result<String, anyhow::Error> {
    let client = Client::builder().timeout(TIMEOUT).build()?;
    let res = client.post(format!("{}/control/client/init", URL))
        .header(CONTENT_TYPE, "application/json")
        .body(id_json)
        .send()
        .await?;
    let code = res.status();
    if code != 200 {
        return Err(anyhow::Error::msg(code));
    }
    let response: Auth = serde_json::from_str(&*(res.text().await?)).unwrap();
    Ok(response.authorization)
}

use std::{
    time::Duration
};
use reqwest::Client;
use reqwest::header::CONTENT_TYPE;
use serde::{
    Deserialize,
    Serialize,
};


const TIMEOUT: Duration = Duration::from_secs(2);
const INIT_ENDPOINT: &'static str = "/control/client/init";

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
pub async fn send_identity(id_json: String, url: &str) -> Result<String, anyhow::Error> {
    let client = Client::builder().timeout(TIMEOUT).build()?;
    let res = client.post(format!("{}{}", url, INIT_ENDPOINT))
        .header(CONTENT_TYPE, "application/json")
        .body(id_json)
        .send()
        .await?;
    let code = res.status();
    if code != 200 {
        return Err(anyhow::Error::msg(code));
    }
    let response: Auth = serde_json::from_str(&*(res.text().await?))
        .unwrap_or_else(|_error| {
            Auth { authorization: String::from("") }
        });
    Ok(response.authorization)
}


#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[actix_rt::test]
    async fn test_send_identity() {
        let url: &'static str = env!("CONTROL_SERVER_URL");
        let id = json!({
        "os_name": "test",
        "os_version": "test",
        "hostname": "test",
        "host_user": "test",
        "privileges": "test" });
        match send_identity(id.to_string(), url).await {
            Ok(val) => {
                assert_eq!(val, String::from("12345"));
            },
            Err(_) => assert!(false)
        };
    }

    #[actix_rt::test]
    async fn test_send_identity_invalid_url() {
        let url = "https://1.2.3.4";
        let id = "test";
        match send_identity(id.to_string(), url).await {
            Ok(_val) => assert!(false),
            Err(_) => assert!(true)
        };
    }
}
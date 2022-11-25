use std::time::Duration;
use reqwest::Client;
use reqwest::header::CONTENT_TYPE;
use crate::models::{Task, Auth, TaskResult, SystemInformation};

const TIMEOUT: Duration = Duration::from_secs(2);

const CONTENT_HEADER_VALUE: &'static str = "application/json";
const AUTHORIZATION_HEADER: &'static str = "Authorization";

/// Sends a post request to the control server with a JSON String as body
///
/// # Returns
/// The response from the request as a String
///
/// # Errors
/// This function fails if there are issues sending the request, if 200 is not returned from
/// the server or if parsing of the request response text fails
pub async fn post_request(body: String,
                          url: &str,
                          endpoint: &str,
                          auth_token: &String) -> Result<String, anyhow::Error> {
    let client = Client::builder()
        .timeout(TIMEOUT)
        .build()?;
    let res = client.post(format!("{}{}", url, endpoint))
        .header(CONTENT_TYPE, CONTENT_HEADER_VALUE)
        .header(AUTHORIZATION_HEADER, auth_token)
        .body(body)
        .send()
        .await?;
    let code = res.status();
    if code != 200 {
        #[cfg(debug_assertions)]
        println!("Failed POST: {}", code);

        return Err(anyhow::Error::msg(code));
    }
    Ok(res.text().await?)
}

/// Send a GET request
///
/// # Returns
/// Result from GET request as a String
///
/// # Errors
/// Fails if there are issues sending the requests, if the return code is not 200 or if parsing
/// of the request response text fails
pub async fn get_request(url: &str,
                         endpoint: &str,
                         auth_token: &String) -> Result<String, anyhow::Error> {
    let client = Client::builder()
        .timeout(TIMEOUT)
        .build()?;
    let res = client.get(&format!("{}{}", url, endpoint))
        .header(CONTENT_TYPE, CONTENT_HEADER_VALUE)
        .header(AUTHORIZATION_HEADER, auth_token)
        .send()
        .await?;
    let code = res.status();
    if res.status() != 200 {
        #[cfg(debug_assertions)]
        println!("Failed GET: {}", code);

        return Err(anyhow::Error::msg(code));
    }
    Ok(res.text().await?)
}

/// Tests for the communication module
#[cfg(test)]
mod tests {
    use super::*;


    #[actix_rt::test]
    async fn test_post_request_invalid_url() {
        let url = "https://1.2.3.4";

        match post_request(String::from("hej"),
                           url,
                           "/",
                           &String::from("")).await {
            Ok(_val) => assert!(false),
            Err(_) => assert!(true)
        };
    }


    #[actix_rt::test]
    async fn test_get_request_invalid_url() {
        let url = "http://1.2.3.4";
        let auth = &String::from("12345");
        match get_request(url, "/", auth).await {
            Ok(_) => assert!(false),
            Err(_) => assert!(true)
        }
    }
}
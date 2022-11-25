/// Struct for UDP messages
struct UDPMessage {
    message_header: UDPMessageHeader,
    url: String,
    body: String,
    request_header: String,
}

/// Implementation of UDPMessage methods
impl UDPMessage {
    const MAX_LENGTH: u16 = 508;

    /// Static function used to create a UDPMessage from a URL, HTTP request header, message body
    /// and status code
    ///
    /// # Returns
    /// UDPMessage struct
    fn new(url: String, request_header: String, body: String, status_code: u8) -> UDPMessage {
        let url_length = url.len() as u16;
        let request_header_length = request_header.len() as u16;
        let true_body_len = body.len() as u16;

        let max_body_size = UDPMessage::MAX_LENGTH -
            UDPMessageHeader::HEADER_LENGTH -
            url_length -
            request_header_length;
        let body_length = if true_body_len <= max_body_size {
            true_body_len
        } else {
            max_body_size
        };
        let message_length = UDPMessageHeader::HEADER_LENGTH +
            url_length +
            request_header_length +
            body_length;

        let message_header = UDPMessageHeader {
            message_length,
            status_code,
            request_header_length,
            url_length,
            body_length,
        };

        UDPMessage {
            message_header,
            url,
            body: body[0..body_length as usize].to_string(),
            request_header,
        }
    }

    /// UDP message length getter
    fn get_length(&self) -> u16 {
        self.message_header.message_length
    }

    /// Concatenate a bytearray into a vector of bytes
    fn push_buf(buf: &mut Vec<u8>, buf2: &[u8]) {
        for b in buf2 {
            buf.push(b.clone());
        }
    }

    /// Getter for the UDPMessage as a vector of bytes.
    ///
    /// # Returns
    /// The UDPMessage as a vector of bytes
    fn as_bytes(&mut self) -> Vec<u8> {
        let mut buf: Vec<u8> = vec![];
        UDPMessage::push_buf(&mut buf, &self.message_header.as_bytes());
        UDPMessage::push_buf(&mut buf, self.url.as_bytes());
        UDPMessage::push_buf(&mut buf, self.body.as_bytes());
        UDPMessage::push_buf(&mut buf, self.request_header.as_bytes());

        buf
    }

    /// Static function to create a UDPMessage from a vector of bytes
    ///
    /// # Returns
    /// A UDPMessage generated from bytes
    fn from_bytes(buf: &Vec<u8>) -> UDPMessage {
        let message_header =
            UDPMessageHeader::from_bytes(&buf[0..UDPMessageHeader::HEADER_LENGTH as usize]);

        let mut cur_index = UDPMessageHeader::HEADER_LENGTH as usize;

        let url =
            buf[cur_index..(cur_index + message_header.url_length as usize)].to_vec();
        cur_index += message_header.url_length as usize;

        let body =
            buf[cur_index..(cur_index + message_header.body_length as usize)].to_vec();
        cur_index += message_header.body_length as usize;

        let request_header =
            buf[cur_index..(cur_index + message_header.request_header_length as usize)].to_vec();

        UDPMessage {
            message_header,
            url: String::from_utf8(url).unwrap(),
            body: String::from_utf8(body).unwrap(),
            request_header: String::from_utf8(request_header).unwrap(),
        }
    }

    /// Checks whether a UDPMessages is equal
    ///
    /// # Returns
    /// True if equal, otherwise false
    fn equal(&mut self, msg: &UDPMessage) -> bool {
        self.message_header.equal(&msg.message_header) &&
            self.url == msg.url &&
            self.body == msg.body &&
            self.request_header == msg.request_header
    }
}


struct UDPMessageHeader {
    message_length: u16,
    status_code: u8,
    url_length: u16,
    body_length: u16,
    request_header_length: u16,
}

impl UDPMessageHeader {
    const HEADER_LENGTH: u16 = 9;

    fn as_bytes(&mut self) -> [u8; 9] {
        let mut buf = [0; 9];
        buf[0] = (self.message_length >> 8) as u8;
        buf[1] = (self.message_length) as u8;
        buf[2] = self.status_code;
        buf[3] = (self.url_length >> 8) as u8;
        buf[4] = self.url_length as u8;
        buf[5] = (self.body_length >> 8) as u8;
        buf[6] = self.body_length as u8;
        buf[7] = (self.request_header_length >> 8) as u8;
        buf[8] = self.request_header_length as u8;

        buf
    }

    fn from_bytes(buf: &[u8]) -> UDPMessageHeader {
        UDPMessageHeader {
            message_length: (buf[0] as u16) << 8 | buf[1] as u16,
            status_code: buf[2],
            url_length: (buf[3] as u16) << 8 | buf[4] as u16,
            body_length: (buf[5] as u16) << 8 | buf[6] as u16,
            request_header_length: (buf[7] as u16) << 8 | buf[8] as u16,
        }
    }

    fn equal(&mut self, header: &UDPMessageHeader) -> bool {
        self.request_header_length == header.request_header_length &&
            self.body_length == header.body_length &&
            self.url_length == header.url_length &&
            self.status_code == header.status_code &&
            self.message_length == header.message_length
    }
}

mod tests {
    use super::*;

    const UDP_HEADERS: [&[u8; 9]; 2] = [
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        b"\x00\x01\x02\x00\x03\x00\x04\x00\x05"
    ];
    const TEST_HEADER1: UDPMessageHeader = UDPMessageHeader {
        message_length: 0,
        status_code: 0,
        url_length: 0,
        body_length: 0,
        request_header_length: 0,
    };
    const TEST_HEADER2: UDPMessageHeader = UDPMessageHeader {
        message_length: 1,
        status_code: 2,
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
            let mut udp_header = UDPMessageHeader::from_bytes(UDP_HEADERS[i]);
            let expected_header = TEST_HEADERS[i];
            assert!(udp_header.equal(expected_header));
        }
    }

    #[test]
    fn test_udp_new_message() {
        let url = "http://127.0.0.1:8080";
        let url_len = url.len() as u16;
        let request_header = "Authorization: \"12345\"";
        let request_header_len = request_header.len() as u16;
        let body = "Successful";
        let body_len = body.len() as u16;
        let status_code = 0;
        let udp_message = UDPMessage::new(url.to_string(),
                                          request_header.to_string(),
                                          body.to_string(),
                                          status_code);

        assert_eq!(url.to_string(), udp_message.url);
        assert_eq!(body.to_string(), udp_message.body);
        assert_eq!(request_header.to_string(), udp_message.request_header);

        assert_eq!(status_code, udp_message.message_header.status_code);
        assert_eq!(url_len, udp_message.message_header.url_length);
        assert_eq!(request_header_len, udp_message.message_header.request_header_length);
        assert_eq!(body_len, udp_message.message_header.body_length);
    }

    #[test]
    fn test_udp_new_message_long_body() {
        let url = "http://127.0.0.1:8080/control/client/init";
        let url_len = url.len() as u16;
        let request_header = "Authorization: \"12345\"";
        let request_header_len = request_header.len() as u16;
        let mut body = String::new();
        for _ in 0..550 {
            body.push('A');
        }
        let body_len = UDPMessage::MAX_LENGTH -
            url_len -
            request_header_len -
            UDPMessageHeader::HEADER_LENGTH;

        let status_code = 0;
        let udp_message = UDPMessage::new(url.to_string(),
                                          request_header.to_string(),
                                          body.to_string(),
                                          status_code);

        assert_eq!(url.to_string(), udp_message.url);
        assert_eq!(body[0..body_len as usize].to_string(), udp_message.body);
        assert_eq!(request_header.to_string(), udp_message.request_header);

        assert_eq!(status_code, udp_message.message_header.status_code);
        assert_eq!(url_len, udp_message.message_header.url_length);
        assert_eq!(request_header_len, udp_message.message_header.request_header_length);
        assert_eq!(body_len, udp_message.message_header.body_length);
        assert_eq!(UDPMessage::MAX_LENGTH, udp_message.message_header.message_length);
    }

    const UDP_MESSAGES: [&[u8; 12]; 2] = [
        b"\x00\x0C\x02\x00\x01\x00\x01\x00\x01ABC",
        b"\x00\x0C\x00\x00\x01\x00\x01\x00\x01AAA"
    ];

    #[test]
    fn test_udp_message_as_bytes() {
        let udp_message1 = UDPMessage::new(
            "A".to_string(),
            "C".to_string(),
            "B".to_string(),
            2);
        let udp_message2 = UDPMessage::new(
            "A".to_string(),
            "A".to_string(),
            "A".to_string(),
            0,
        );
        let mut udp_messages = [
            udp_message1,
            udp_message2
        ];

        for i in 0..UDP_MESSAGES.len() {
            let buf = udp_messages[i].as_bytes();
            for j in 0..UDP_MESSAGES[i].len() {
                assert_eq!(buf[j], UDP_MESSAGES[i][j]);
            }
        }
    }

    #[test]
    fn test_udp_message_from_bytes() {
        let udp_message1 = UDPMessage::new(
            "A".to_string(),
            "C".to_string(),
            "B".to_string(),
            2);
        let udp_message2 = UDPMessage::new(
            "A".to_string(),
            "A".to_string(),
            "A".to_string(),
            0,
        );
        let udp_messages = [
            &udp_message1,
            &udp_message2
        ];

        for i in 0..UDP_MESSAGES.len() {
            let mut udp_message = UDPMessage::from_bytes(&UDP_MESSAGES[i].to_vec());
            assert!(udp_message.equal(udp_messages[i]));
        }
    }
}
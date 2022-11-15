use whoami;
use serde_json::json;

/// Returns the current clients identifying characteristics
pub fn get_host_identify() -> String {
    let os_distro = whoami::distro();
    let vec = os_distro.split_whitespace().collect::<Vec<&str>>();
    let json = json!({
        "os_name": vec[0 as usize],
        "os_version": vec[1 as usize],
        "hostname": whoami::hostname(),
        "host_user": whoami::username(),
        "privileges": "null" // Currently not implemented!
    });
    json.to_string()
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_host_identity() {
        let keys = ["os_name", "os_version", "hostname", "host_user", "privileges"];
        let id = get_host_identify();
        for key in keys {
            if !id.contains(key) {
                assert!(false);
            }
        }
        assert!(true);
    }
}
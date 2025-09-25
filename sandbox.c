#define _GNU_SOURCE
#define _POSIX_C_SOURCE 199309L

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <stdarg.h>
#include <signal.h>

/**
 * ZenCube Sandbox Runner - Phase 1
 * 
 * A minimal sandbox implementation that creates isolated process execution
 * using fork/exec/wait system calls with proper error handling and timing.
 * 
 * Author: Systems Programming Team
 * Date: September 2025
 */

/* Function prototypes */
void print_usage(const char *program_name);
void log_message(const char *format, ...);
void log_command(int argc, char *argv[], int start_index);
double timespec_diff(struct timespec *start, struct timespec *end);

/**
 * Print usage information for the sandbox program
 */
void print_usage(const char *program_name) {
    printf("Usage: %s <command> [arguments...]\n", program_name);
    printf("\nDescription:\n");
    printf("  Execute a command in a minimal sandbox environment.\n");
    printf("  The command will run as a child process with full monitoring.\n");
    printf("\nExamples:\n");
    printf("  %s /bin/ls -l /\n", program_name);
    printf("  %s /usr/bin/whoami\n", program_name);
    printf("  %s /bin/echo \"Hello from sandbox\"\n", program_name);
    printf("  %s /bin/sleep 3\n", program_name);
}

/**
 * Log a formatted message with timestamp and sandbox prefix
 */
void log_message(const char *format, ...) {
    va_list args;
    time_t raw_time;
    struct tm *time_info;
    char time_buffer[80];
    
    /* Get current time for logging */
    time(&raw_time);
    time_info = localtime(&raw_time);
    strftime(time_buffer, sizeof(time_buffer), "%H:%M:%S", time_info);
    
    printf("[Sandbox %s] ", time_buffer);
    
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
    
    printf("\n");
    fflush(stdout);
}

/**
 * Log the command being executed with all its arguments
 */
void log_command(int argc, char *argv[], int start_index) {
    printf("[Sandbox] Starting command:");
    for (int i = start_index; i < argc; i++) {
        printf(" %s", argv[i]);
    }
    printf("\n");
    fflush(stdout);
}

/**
 * Calculate the difference between two timespec structures in seconds
 */
double timespec_diff(struct timespec *start, struct timespec *end) {
    return (end->tv_sec - start->tv_sec) + (end->tv_nsec - start->tv_nsec) / 1000000000.0;
}

/**
 * Main sandbox runner function
 */
int main(int argc, char *argv[]) {
    pid_t child_pid;
    int status;
    struct timespec start_time, end_time;
    double execution_time;
    
    /* Check command line arguments */
    if (argc < 2) {
        fprintf(stderr, "Error: No command specified\n\n");
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }
    
    /* Log the command we're about to execute */
    log_command(argc, argv, 1);
    
    /* Record start time for timing measurement */
    if (clock_gettime(CLOCK_MONOTONIC, &start_time) == -1) {
        log_message("Warning: Failed to get start time: %s", strerror(errno));
    }
    
    /* Create child process using fork() */
    child_pid = fork();
    
    if (child_pid == -1) {
        /* Fork failed */
        fprintf(stderr, "[Sandbox] Error: Failed to create child process: %s\n", 
                strerror(errno));
        return EXIT_FAILURE;
    }
    
    if (child_pid == 0) {
        /* This is the child process */
        log_message("Child process created (PID: %d)", getpid());
        
        /* Replace process image with target command using execvp() */
        /* execvp() automatically searches PATH for the executable */
        if (execvp(argv[1], &argv[1]) == -1) {
            /* execvp() failed - this only executes if exec fails */
            fprintf(stderr, "[Sandbox] Child Error: Failed to execute '%s': %s\n", 
                    argv[1], strerror(errno));
            exit(EXIT_FAILURE);
        }
        
        /* This line should never be reached if execvp() succeeds */
        exit(EXIT_FAILURE);
    } else {
        /* This is the parent process */
        log_message("Child PID: %d", child_pid);
        
        /* Wait for child process to complete */
        pid_t wait_result = waitpid(child_pid, &status, 0);
        
        /* Record end time */
        if (clock_gettime(CLOCK_MONOTONIC, &end_time) == -1) {
            log_message("Warning: Failed to get end time: %s", strerror(errno));
            execution_time = -1.0;  /* Indicate timing failed */
        } else {
            execution_time = timespec_diff(&start_time, &end_time);
        }
        
        if (wait_result == -1) {
            fprintf(stderr, "[Sandbox] Error: waitpid() failed: %s\n", strerror(errno));
            return EXIT_FAILURE;
        }
        
        /* Analyze and log child process exit status */
        if (WIFEXITED(status)) {
            /* Child exited normally */
            int exit_code = WEXITSTATUS(status);
            log_message("Process exited normally with status %d", exit_code);
            
            if (execution_time >= 0) {
                log_message("Execution time: %.3f seconds", execution_time);
            }
            
            /* Return the same exit code as the child process */
            return exit_code;
        } else if (WIFSIGNALED(status)) {
            /* Child was terminated by a signal */
            int signal_num = WTERMSIG(status);
            log_message("Process terminated by signal %d (%s)", 
                       signal_num, strsignal(signal_num));
            
            if (execution_time >= 0) {
                log_message("Execution time before termination: %.3f seconds", execution_time);
            }
            
            /* Check if core dump was created */
            if (WCOREDUMP(status)) {
                log_message("Core dump was created");
            }
            
            return EXIT_FAILURE;
        } else if (WIFSTOPPED(status)) {
            /* Child was stopped (shouldn't happen with our waitpid call) */
            int stop_signal = WSTOPSIG(status);
            log_message("Process stopped by signal %d", stop_signal);
            return EXIT_FAILURE;
        } else {
            /* Unknown status */
            log_message("Process ended with unknown status: %d", status);
            return EXIT_FAILURE;
        }
    }
    
    return EXIT_SUCCESS;
}
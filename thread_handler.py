
# Handles threads for the rail project
import threading

threads = {}  # Store all threads

def start_thread(thread_name, function, arguments):
    # Start a new thread
    if thread_name in threads:
        print("Error: Thread", thread_name, "already running!")
        return
    try:
        new_thread = threading.Thread(target=function, args=arguments)
        new_thread.daemon = True  # Stop thread when program exits
        new_thread.start()
        threads[thread_name] = new_thread
        print("Started thread:", thread_name)
    except Exception as e:
        print("Failed to start thread", thread_name, ":", e)

def stop_all_threads():
    # Clear all threads (daemon threads stop automatically)
    global threads
    for thread_name in threads:
        print("Stopping thread:", thread_name)
    threads = {}

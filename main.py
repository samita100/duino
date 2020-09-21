import multiprocessing, threading, socket, hashlib, os, urllib.request, statistics, random, sys, time


username = "rock6064" # Username
efficiency = 50 # Efficiency
try:
  thread_number = os.cpu_count() // 2
except:
  thread_number = 5
refresh_time = 1 # refresh time in seconds for the output (recommended: 1)
autorestart_time = 600 # autorestart time in seconds. 0 = disabled

# --------------------------------------------------------------- #


if not username:
    print("Please set your username first")
    time.sleep(5)
    os._exit(1)

last_hash_count = 0
khash_count = 0
hash_count = 0
hash_mean = []

def hashrateCalculator():
    global last_hash_count, hash_count, khash_count, hash_mean
  
    last_hash_count = hash_count
    khash_count = last_hash_count / 1000
    if khash_count == 0:
        khash_count = random.uniform(0, 1)
    
    hash_mean.append(khash_count)
    khash_count = statistics.mean(hash_mean)
    khash_count = round(khash_count, 2)
  
    hash_count = 0
  
    threading.Timer(1.0, hashrateCalculator).start()

    
def start_thread(arr, i, username, accepted_shares, bad_shares, thread_number, efficiency):
    global hash_count, khash_count
    soc = socket.socket()

    serverip = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"
    with urllib.request.urlopen(serverip) as content:
        content = content.read().decode().splitlines()
    pool_address = content[0]
    pool_port = content[1]

    soc.connect((str(pool_address), int(pool_port)))
    soc.recv(3).decode()

    hashrateCalculator()
    efficiency = 100 - float(efficiency) # Calulate efficiency
    efficiency = efficiency * 0.01
    while True:
        time.sleep(float(efficiency)) # Sleep to achieve lower efficiency
        try:
            soc.send(bytes("JOB,"+str(username), encoding="utf8"))
            job = soc.recv(1024).decode()
            job = job.split(",")
            try:
                difficulty = job[2]
            except:
                for p in multiprocessing.active_children():
                    p.terminate()
                time.sleep(1)
                sys.argv.append(str(thread_number))
                os.execl(sys.executable, sys.executable, *sys.argv)

            for result in range(100 * int(difficulty) + 1):
                hash_count = hash_count + 1
                ducos1 = hashlib.sha1(str(job[0] + str(result)).encode("utf-8")).hexdigest()
                if job[1] == ducos1:
                    soc.send(bytes(str(result), encoding="utf8"))
                    feedback = soc.recv(1024).decode()
                    arr[i] = khash_count
                    if feedback == "GOOD" or feedback == "BLOCK":
                        accepted_shares[i] += 1
                        break
                    elif feedback == "BAD":
                        bad_shares[i] += 1
                        break
                    elif feedback == "INVU":
                        print("Entered username is incorrect!")
        except (KeyboardInterrupt, SystemExit):
            print("Thread #{}: exiting...".format(i))
            os._exit(0)


def autorestarter():
    time.sleep(autorestart_time)
    
    for p in multiprocessing.active_children():
        p.terminate()
    time.sleep(1)
    sys.argv.append(str(thread_number))
    os.execl(sys.executable, sys.executable, *sys.argv)

def showOutput():
    clear()

    d = {}
    for thread in range(thread_number):
        d[f"#{thread + 1}"] = [f"{hashrate_array[thread]} kH/s", accepted_shares[thread], bad_shares[thread]]

    print("{:<9} {:<13} {:<10} {:<10}".format('Thread','Hashrate','Accepted','Rejected'))
    for k, v in d.items():
        hashrate, good, bad = v
        print("{:<9} {:<13} {:<10} {:<10}".format(k, hashrate, good, bad))
    
    print("{:<9} {:<13} {:<10} {:<10}".format("TOTAL", totalHashrate(sum(hashrate_array)), sum(accepted_shares), sum(bad_shares)))

    threading.Timer(float(refresh_time), showOutput).start()
        

def clear():
    os.system('cls' if os.name=='nt' else 'clear')


def totalHashrate(khash):
    if khash / 1000 >= 1:
        return str(round(khash / 1000, 2)) + " MH/s"
    else:
        return str(round(khash, 2)) + " kH/s"


if __name__ == '__main__':
    if os.name == 'nt':
        os.system("title " + "Duino-Coin multithreaded miner")
    else:
        print('\33]0;' + "Duino-Coin multithreaded miner"+'\a', end='')
    clear()
    
    if (autorestart_time) > 0:
        threading.Thread(target=autorestarter).start()

    with urllib.request.urlopen("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt") as content:
        content = content.read().decode().splitlines() # doing this here because can't access pool_address and pool_port in the threads
    pool_address = content[0]
    pool_port = content[1]
    


    hashrate_array = multiprocessing.Array("d", thread_number)
    accepted_shares = multiprocessing.Array("i", thread_number)
    bad_shares = multiprocessing.Array("i", thread_number)

    showOutput()

    for i in range(thread_number):
        p = multiprocessing.Process(target=start_thread, args=(hashrate_array, i, username, accepted_shares, bad_shares, thread_number, efficiency))
        p.start()
        time.sleep(0.5)
    time.sleep(1)
    

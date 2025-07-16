# =============================================================================
# Maintainer:     Luis Eduardo Pessoa
# Contact:        lpdemarinha@gmail.com
# Purpose:        Collect summarized info on HD usage for the list of servers identified in the servers dictionary
# =============================================================================

import subprocess

# Hardcoded dictionary of servers
servers = {
 

    "192.168.1.20": {"username": "user2", "password": "pass2", "environment":"SSO", "server_name":"APOLO 2 – Single Sign On"},
    # Add more IPs and credentials as needed
}

output_file = "server_storage_report2.txt"
separator = "#" * 100 + "\n"

# Command to get storage info
remote_command = "df -h -BM"
# remote_command = """df -kh && df -kh | awk 'NR==1; NR>1 {used+=$3; avail+=$4; total+=$2} END {printf \"%-20s %-10s %-10s %-10s %-10.2f%%\\n\", \"Total\", total, used, avail, used/total*100}'"""

def mainRunner():
    with open(output_file, "w") as f:
        for ip, creds in servers.items():
            print(f"Processing {ip}")
            username = creds["username"]
            password = creds["password"]
            environment = creds["environment"]
            server_name = creds["server_name"]

            try:
                ssh_command = [
                    "sshpass", "-p", password,
                    "ssh", "-o", "StrictHostKeyChecking=no", "-o", "HostKeyAlgorithms=+ssh-rsa",
                    f"{username}@{ip}", remote_command
                ]            
                # df -kh | awk 'NR==1; NR>1 {used+=$3; avail+=$4; total+=$2} END {printf "%-20s %-10s %-10s %-10s %-10s\n", "Total", total, used, avail, used/total*100 "%"}'

                result = subprocess.run(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                # print(" ".join(ssh_command))

                f.write(f"Storage info for {server_name} / {ip} of the {environment} environment:\n")
                final = result.stdout if result.stdout else result.stderr
                # f.write(final)
                f.write(summarize_df_output(final))
                f.write("\n" + separator)
            except Exception as e:
                f.write(f"Error connecting to {ip}: {e}\n{separator}")

    print(f"Storage report saved to {output_file}")


def summarize_df_output(df_output: str):
    total_size = 0
    total_used = 0

    for line in df_output.strip().splitlines():
        # Skip header line
        if line.startswith("Filesystem") or not line.strip():
            continue

        parts = line.split()
        if len(parts) < 6:
            continue

        size_str = parts[1]
        used_str = parts[2]

        try:
            # Remove 'M' and convert to int
            size = int(size_str.rstrip('M'))
            used = int(used_str.rstrip('M'))
            total_size += size
            total_used += used
        except ValueError:
            continue  # Skip lines with unexpected formats

    if total_size == 0:
        percent_used = 0
    else:
        percent_used = round((total_used / total_size) * 100, 2)

    summary_line = f"Total Size: {round(total_size/ 1024, 2)}GB, Used: {round(total_used/1024,2)}GB, %Used: {percent_used}%"
    return summary_line

if __name__ == "__main__":
    mainRunner()

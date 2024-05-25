import argparse
import json
import paramiko
import socket

DEFAULT_CREDENTIALS_FILE = 'default_credentials.json'

def load_credentials(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return [(cred['username'], cred['password']) for cred in data['credentials']], None
    except FileNotFoundError:
        return None, f"Credentials file not found: {file_path}"
    except json.JSONDecodeError as e:
        return None, f"Error parsing credentials file: {e}"
    except KeyError as e:
        return None, f"Missing key in credentials file: {e}"
    except Exception as e:
        return None, f"Error loading credentials file: {e}"

def is_port_open(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            result = sock.connect_ex((ip, port))
            return result == 0, None
    except socket.error as e:
        return False, f"Error checking port availability: {e}"

def test_ssh_login(ip, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password, timeout=5)
        ssh.close()
        return True, None
    except paramiko.AuthenticationException:
        return False, None
    except paramiko.SSHException as e:
        return False, f"SSH exception: {e}"
    except socket.error as e:
        return False, f"Socket error: {e}"
    except Exception as e:
        return False, f"Error during SSH login: {e}"

def main():
    parser = argparse.ArgumentParser(description='Test SSH login using default credentials.')
    parser.add_argument('ip', type=str, help='IP address of the SSH server')
    parser.add_argument('port', type=int, help='Port number of the SSH server')
    parser.add_argument('--credentials-file', type=str, default=DEFAULT_CREDENTIALS_FILE,
                        help='JSON file containing default credentials (default: default_credentials.json)')
    args = parser.parse_args()

    ip = args.ip
    port = args.port
    credentials_file = args.credentials_file

    port_open, error = is_port_open(ip, port)
    if not port_open:
        results = [{'error': error}] if error else [{'error': f"Port {port} is not open on {ip}"}]
        report = {
            'ip': ip,
            'port': port,
            'results': results
        }
        print(json.dumps(report, indent=2))
        return

    credentials, error = load_credentials(credentials_file)
    if error:
        results = [{'error': error}]
    elif credentials is None:
        results = [{'error': 'No credentials found'}]
    else:
        print(f"Scanning with {len(credentials)} username/password combinations.\n")

        results = []
        for i, (username, password) in enumerate(credentials, start=1):
            print(f"Checking {i}/{len(credentials)} - Username: {username}, Password: {password}")
            success, error = test_ssh_login(ip, port, username, password)
            result = {
                'username': username,
                'password': password,
                'success': success
            }
            if error:
                result['error'] = error
            results.append(result)
            status = "Success" if success else "Fail"
            print(f"Result: {status}\n")

    report = {
        'ip': ip,
        'port': port,
        'results': results
    }

    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
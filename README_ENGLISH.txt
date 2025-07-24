# VYNE - Vulnerability Yielding Network Enumerator v1.0
		   (A Network Scanner That Reveals Vulnerabilities)

**VYNE** is a versatile security scanning tool that performs subdomain and endpoint discovery on target systems. It includes wildcard detection, supports GET and POST requests, and offers flexible filtering and JSON output.

## Features

- Subdomain scanning (wordlist-supported)
- Wildcard subdomain detection
- Endpoint (URL path) discovery
- Supports GET and POST HTTP methods
- Wordlist-based POST payloads (key-value or data format)
- Filter results by HTTP status codes
- Output in JSON format
- Fast scanning with multi-threading

## Installation

```bash
git clone https://github.com/Sh4d0wHunt3r-XD/VYNE-v1.0.git
cd VYNE
pip3 install -r requirements.txt
```

Python 3.6 or higher is recommended.

## Usage Examples

Basic usage:
```bash
python3 vyne.py -u https://example.com -w wordlist.txt
```

Subdomain + endpoint scanning:
```bash
python3 vyne.py -u https://example.com -w endpoints.txt -s subdomains.txt
```

Subdomain-only scan:
```bash
python3 vyne.py -u https://example.com -s subdomains.txt --noendpoint
```

Brute-force with POST request:
```bash
python3 vyne.py -u https://example.com/login -X POST -K keys.txt -V values.txt
```

Save results to a JSON file:
```bash
python3 vyne.py -u https://example.com -w wordlist.txt -o /path/to/output/
```

Filter by specific HTTP status codes:
```bash
python3 vyne.py -u https://example.com -w wordlist.txt --status 200,403
```

## Parameters

| Parameter          | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| -u, --url          | Target URL (required)                                                       |
| -w, --wordlist     | Wordlist file for endpoint scanning                                         |
| -s, --subwordlist  | Wordlist file for subdomain scanning                                        |
| -X, --method       | HTTP method (GET or POST), default is GET                                   |
| -K, --keys         | Wordlist file for POST keys                                                 |
| -V, --values       | Wordlist file for POST values                                               |
| -D, --datas        | Wordlist file in `key=value&key2=value2` format for POST data               |
| -t, --thread       | Number of threads to use, default is 5                                      |
| --timeout          | Timeout for HTTP requests (in seconds), default is 15                       |
| -o, --output       | Directory to save the output                                                |
| --status           | Comma-separated list of HTTP status codes to filter                         |
| -fs, --firstsub    | Perform subdomain scanning first                                            |
| --noendpoint       | Skip endpoint scanning                                                      |
| -U, --user-agent   | Custom User-Agent for HTTP requests                                         |

## Output

Results are saved in JSON format to the specified directory. Example:

```json
[
  {
    "url": "https://admin.example.com",
    "status": 200
  },
  {
    "url": "https://example.com/login",
    "status": 302,
    "redirect": "https://example.com/dashboard"
  }
]
```

## Comparison Table

| Feature / Tool       | VYNE | ffuf | Amass | Dirsearch | Sublist3r |
|----------------------|:----:|:----:|:-----:|:---------:|:---------:|
| Subdomain Scanning   |  ✔   |  ✘   |  ✔    |     ✘     |     ✔     |
| Wildcard Detection   |  ✔   |  ✘   |  ⚠️    |     ✘     |     ✘     |
| Endpoint Scanning    |  ✔   |  ✔   |  ✘    |     ✔     |     ✘     |
| POST Support         |  ✔   |  ⚠️   |  ✘    |     ✘     |     ✘     |
| JSON Output          |  ✔   |  ✔   |  ✔    |     ✔     |     ✘     |

> ✔: Supported, ✘: Not supported, ⚠️: Limited/Indirect support

## License

Released under the MIT License.

---

## ⚠️ Disclaimer

This tool is intended **only for authorized and legal security testing**. The developer is not responsible for any misuse or illegal activities performed using this tool.

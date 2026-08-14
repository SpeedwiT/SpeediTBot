#!/usr/bin/env python3
"""
SpeediT - Telegram Bot Manager for VPN Panel Management
Advanced Terminal UI with full installation and management capabilities
"""

import os
import sys
import subprocess
import json
import time
import shutil
from pathlib import Path

# ============== ANSI Color Codes ==============

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    ORANGE = "\033[38;5;208m"
    PURPLE = "\033[38;5;141m"
    PINK = "\033[38;5;213m"

# ============== Configuration ==============

PROJECT_NAME = "SpeediT"
PROJECT_VERSION = "1.0.0"
PROJECT_DESC = "Telegram Bot for VPN Panel Management"
SUPPORT_TG = "@SpeedwIT"
CHANNEL_TG = "@Speedw_IT"
GITHUB_URL = "https://github.com/SpeedwiT/SpeediTBot"
INSTALL_DIR = "/opt/speedit"
ENV_FILE = f"{INSTALL_DIR}/.env"

# ============== UI Components ==============

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def gradient_text(text):
    colors = [Colors.CYAN, Colors.BLUE, Colors.PURPLE, Colors.MAGENTA, Colors.PINK]
    result = ""
    for i, char in enumerate(text):
        color_index = int((i / len(text)) * (len(colors) - 1))
        result += f"{colors[color_index]}{char}"
    return result + Colors.RESET

def status_dot(status):
    dots = {
        "ok": f"{Colors.GREEN}[OK]{Colors.RESET}",
        "error": f"{Colors.RED}[FAIL]{Colors.RESET}",
        "warning": f"{Colors.YELLOW}[WARN]{Colors.RESET}",
        "info": f"{Colors.BLUE}[INFO]{Colors.RESET}",
    }
    return dots.get(status, f"{Colors.WHITE}[?]{Colors.RESET}")

def progress_bar(percent, width=40):
    filled = int(width * percent / 100)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {percent:.0f}%"

def print_header():
    banner = f"""
{gradient_text("   ███████╗██████╗ ███████╗███████╗██████╗ ██╗████████╗")}
{gradient_text("   ██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██║╚══██╔══╝")}
{gradient_text("   ███████╗██████╔╝█████╗  █████╗  ██║  ██║██║   ██║")}
{gradient_text("   ╚════██║██╔═══╝ ██╔══╝  ██╔══╝  ██║  ██║██║   ██║")}
{gradient_text("   ███████║██║     ███████╗███████╗██████╔╝██║   ██║")}
{gradient_text("   ╚══════╝╚═╝     ╚══════╝╚══════╝╚═════╝ ╚═╝   ╚═╝")}
{Colors.DIM}{'═' * 55}{Colors.RESET}
{Colors.GREEN}{Colors.BOLD}   🚀 {PROJECT_NAME} v{PROJECT_VERSION}{Colors.RESET}
{Colors.DIM}   {PROJECT_DESC}{Colors.RESET}
{Colors.DIM}{'═' * 55}{Colors.RESET}
"""
    print(banner)

def show_links():
    print(f"\n{Colors.DIM}┌─ {Colors.WHITE}Links{'─' * 48}{Colors.DIM}┐{Colors.RESET}")
    print(f"{Colors.DIM}│{Colors.RESET} 📱 Support: {Colors.CYAN}{SUPPORT_TG}{Colors.RESET}  │  📢 Channel: {Colors.CYAN}{CHANNEL_TG}{Colors.RESET}  {Colors.DIM}│{Colors.RESET}")
    print(f"{Colors.DIM}│{Colors.RESET} 💻 GitHub:  {Colors.CYAN}{GITHUB_URL}{Colors.RESET}    {Colors.DIM}│{Colors.RESET}")
    print(f"{Colors.DIM}└{'─' * 55}┘{Colors.RESET}\n")

def show_menu(title, items):
    """Show interactive menu"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.WHITE}  {title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 55}{Colors.RESET}\n")
    
    for key, (desc, icon, color) in items.items():
        print(f"  {Colors.BOLD}{color}[{key}]{Colors.RESET} {icon} {desc}")
    
    print(f"\n{Colors.CYAN}{'─' * 55}{Colors.RESET}")
    
    while True:
        choice = input(f"\n{Colors.BOLD}{Colors.YELLOW}➤ Select option:{Colors.RESET} ").strip().lower()
        if choice in items:
            return choice
        print(f"{Colors.RED}✗ Invalid option. Please try again.{Colors.RESET}")

def input_with_validation(prompt, validator, error_msg):
    """Get validated input"""
    while True:
        value = input(prompt).strip()
        if validator(value):
            return value
        print(f"{Colors.RED}✗ {error_msg}{Colors.RESET}")

def confirm_action(message):
    """Confirm dangerous action"""
    print(f"\n{Colors.RED}{Colors.BOLD}⚠ {message}{Colors.RESET}")
    return input(f"{Colors.YELLOW}Type 'yes' to confirm:{Colors.RESET} ").strip().lower() == 'yes'

def run_cmd(cmd, desc=""):
    """Run shell command with status"""
    if desc:
        print(f"  {Colors.DIM}{desc}...{Colors.RESET}", end="", flush=True)
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        if desc:
            print(f"\r  {Colors.GREEN}✓ {desc}{Colors.RESET}")
        return True
    else:
        if desc:
            print(f"\r  {Colors.RED}✗ {desc}{Colors.RESET}")
        return False

# ============== Main Functions ==============

def check_root():
    if os.geteuid() != 0:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Error:{Colors.RESET} {Colors.RED}This script must be run as root!{Colors.RESET}")
        print(f"{Colors.YELLOW}  Please run: {Colors.WHITE}sudo python3 speedit.py{Colors.RESET}\n")
        return False
    return True

def check_requirements():
    print(f"\n{Colors.CYAN}{'─' * 55}{Colors.RESET}")
    print(f"{Colors.BOLD}System Requirements Check{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 55}{Colors.RESET}\n")
    
    reqs = [("Docker", "docker"), ("Docker Compose", "docker-compose"), ("Git", "git"), ("Curl", "curl")]
    all_ok = True
    
    for name, cmd in reqs:
        if shutil.which(cmd):
            print(f"  {status_dot('ok')} {Colors.GREEN}{name:<20}{Colors.RESET} Installed")
        else:
            print(f"  {status_dot('error')} {Colors.RED}{name:<20}{Colors.RESET} Not found")
            all_ok = False
    
    try:
        with open("/proc/meminfo") as f:
            mem_total = int(f.readline().split()[1]) / 1024 / 1024
            status = "ok" if mem_total >= 1.0 else "warning"
            print(f"  {status_dot(status)} {Colors.GREEN if status == 'ok' else Colors.YELLOW}{'RAM':<20}{Colors.RESET} {mem_total:.1f} GB")
    except:
        pass
    
    print(f"\n{Colors.CYAN}{'─' * 55}{Colors.RESET}")
    
    if all_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All requirements met!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Some requirements missing. Will install automatically.{Colors.RESET}")
    
    return all_ok

def install_requirements():
    print(f"\n{Colors.CYAN}Installing requirements...{Colors.RESET}\n")
    
    run_cmd("apt-get update", "Updating package list")
    run_cmd("apt-get install -y curl wget git software-properties-common apt-transport-https ca-certificates", "Installing basic tools")
    
    if not shutil.which("docker"):
        run_cmd("curl -fsSL https://get.docker.com | sh", "Installing Docker")
        run_cmd("systemctl enable docker && systemctl start docker", "Enabling Docker")
    
    if not shutil.which("docker-compose"):
        run_cmd('pip3 install docker-compose 2>/dev/null || (curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose)', "Installing Docker Compose")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All requirements installed!{Colors.RESET}")

def get_bot_config():
    print(f"\n{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.WHITE}  Bot Configuration{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}\n")
    
    token = input_with_validation(
        f"{Colors.BOLD}{Colors.YELLOW}🤖 Enter Bot Token:{Colors.RESET} ",
        lambda x: len(x) > 20 and ":" in x,
        "Invalid token format. Please try again."
    )
    print(f"  {Colors.GREEN}✓ Token format looks valid{Colors.RESET}")
    
    admin_id = input_with_validation(
        f"{Colors.BOLD}{Colors.YELLOW}👤 Enter Admin ID (numeric):{Colors.RESET} ",
        lambda x: x.isdigit() and len(x) > 5,
        "Invalid ID. Please enter a numeric Telegram user ID."
    )
    print(f"  {Colors.GREEN}✓ Admin ID: {admin_id}{Colors.RESET}")
    
    domain = input(f"{Colors.BOLD}{Colors.YELLOW}🌐 Enter Domain (optional, press Enter to skip):{Colors.RESET} ").strip()
    if domain:
        print(f"  {Colors.GREEN}✓ Domain: {domain}{Colors.RESET}")
    
    email = ""
    if domain:
        email = input(f"{Colors.BOLD}{Colors.YELLOW}📧 Enter Email (for SSL certificate):{Colors.RESET} ").strip()
        if "@" in email:
            print(f"  {Colors.GREEN}✓ Email: {email}{Colors.RESET}")
    
    return {"token": token, "admin_id": admin_id, "domain": domain, "email": email}

def generate_env(config):
    print(f"\n{Colors.CYAN}Generating configuration...{Colors.RESET}\n")
    
    import secrets
    db_password = secrets.token_urlsafe(24)
    redis_password = secrets.token_urlsafe(24)
    secret_key = secrets.token_urlsafe(48)
    
    webhook_line = f"WEBHOOK_URL=https://{config['domain']}/webhook" if config['domain'] else "# WEBHOOK_URL="
    domain_line = f"DOMAIN={config['domain']}" if config['domain'] else "# DOMAIN="
    
    env_content = f"""# SpeediT Configuration
# Generated on {time.strftime("%Y-%m-%d %H:%M:%S")}

# Telegram Bot
BOT_TOKEN={config['token']}
ADMIN_IDS={config['admin_id']}
USE_POLLING=true
{webhook_line}

# Database
DB_NAME=speedit
DB_USER=speedit
DB_PASSWORD={db_password}

# Redis
REDIS_PASSWORD={redis_password}

# Security
SECRET_KEY={secret_key}

# Domain
{domain_line}

# Logging
LOG_LEVEL=INFO
"""
    
    os.makedirs(INSTALL_DIR, exist_ok=True)
    with open(ENV_FILE, "w") as f:
        f.write(env_content)
    
    print(f"  {Colors.GREEN}✓ Configuration saved to {ENV_FILE}{Colors.RESET}")
    
    with open(f"{INSTALL_DIR}/.speedit_config.json", "w") as f:
        json.dump(config, f, indent=2)

def setup_ssl(config):
    if not config.get('domain') or not config.get('email'):
        print(f"\n{Colors.DIM}  Skipping SSL setup (no domain/email){Colors.RESET}")
        return
    
    print(f"\n{Colors.CYAN}Setting up SSL certificate...{Colors.RESET}\n")
    
    if not shutil.which("certbot"):
        run_cmd("apt-get install -y certbot python3-certbot-nginx", "Installing Certbot")
    
    # Create webroot directory
    run_cmd("mkdir -p /var/www/html", "Creating webroot directory")
    
    # Use webroot mode (works even if nginx is running)
    domain = config['domain']
    email = config['email']
    
    cmd = f'certbot certonly --webroot -w /var/www/html -d {domain} --email {email} --agree-tos --non-interactive'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"  {Colors.GREEN}✓ SSL certificate obtained{Colors.RESET}")
        
        ssl_dir = f"{INSTALL_DIR}/nginx/ssl"
        os.makedirs(ssl_dir, exist_ok=True)
        
        subdomain_dir = domain.split('.')[0] if '.' in domain else domain
        possible_paths = [
            f"/etc/letsencrypt/live/{domain}",
            f"/etc/letsencrypt/live/{subdomain_dir}.{'.'.join(domain.split('.')[1:])}" if '.' in domain else "",
        ]
        
        for cert_path in possible_paths:
            if os.path.exists(cert_path) and cert_path:
                run_cmd(f"cp {cert_path}/fullchain.pem {ssl_dir}/", "Copying SSL certificate")
                run_cmd(f"cp {cert_path}/privkey.pem {ssl_dir}/", "Copying SSL key")
                break
    else:
        print(f"  {Colors.YELLOW}⚠ SSL setup failed: {result.stderr[:100]}{Colors.RESET}")
        print(f"  {Colors.DIM}  Continuing without SSL{Colors.RESET}")

def deploy():
    print(f"\n{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.WHITE}  Deploying SpeediT{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}\n")
    
    steps = [
        ("Checking Docker", "docker --version"),
        ("Building images", f"cd {INSTALL_DIR} && docker-compose build --no-cache"),
        ("Starting services", f"cd {INSTALL_DIR} && docker-compose up -d"),
    ]
    
    for i, (desc, cmd) in enumerate(steps, 1):
        print(f"  {Colors.CYAN}[{i}/{len(steps)}]{Colors.RESET} {desc}...", end="", flush=True)
        result = subprocess.run(cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print(f"\r  {Colors.GREEN}✓ [{i}/{len(steps)}] {desc}{Colors.RESET}")
        else:
            print(f"\r  {Colors.RED}✗ [{i}/{len(steps)}] {desc}{Colors.RESET}")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Deployment complete!{Colors.RESET}")

def show_post_install(config):
    print(f"\n{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}  🎉 Installation Complete!{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}\n")
    
    print(f"  {Colors.BOLD}Useful Commands:{Colors.RESET}")
    print(f"  {Colors.DIM}─────────────────────────────────────────────{Colors.RESET}")
    print(f"  {Colors.CYAN}Manage:{Colors.RESET}    sudo python3 speedit.py manage")
    print(f"  {Colors.CYAN}Logs:{Colors.RESET}      cd {INSTALL_DIR} && docker-compose logs -f")
    print(f"  {Colors.CYAN}Restart:{Colors.RESET}   cd {INSTALL_DIR} && docker-compose restart")
    print(f"  {Colors.CYAN}Update:{Colors.RESET}    sudo python3 speedit.py update")
    print(f"  {Colors.CYAN}Uninstall:{Colors.RESET} sudo python3 speedit.py uninstall")
    
    if config.get('domain'):
        print(f"\n  {Colors.BOLD}Access URLs:{Colors.RESET}")
        print(f"  {Colors.DIM}─────────────────────────────────────────────{Colors.RESET}")
        print(f"  {Colors.CYAN}Mini App:{Colors.RESET} https://{config['domain']}/miniapp")
        print(f"  {Colors.CYAN}API:{Colors.RESET}      https://{config['domain']}/api")
    
    print(f"\n{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print(f"  {Colors.DIM}Need help? Contact: {Colors.CYAN}{SUPPORT_TG}{Colors.RESET}")
    print(f"  {Colors.DIM}Join our channel: {Colors.CYAN}{CHANNEL_TG}{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}\n")

def install():
    clear_screen()
    print_header()
    
    if not check_root():
        return
    
    check_requirements()
    install_requirements()
    
    config = get_bot_config()
    generate_env(config)
    download_project()
    setup_ssl(config)
    deploy()
    show_post_install(config)

def download_project():
    """Copy project files to install directory"""
    print(f"\n{Colors.CYAN}Copying project files...{Colors.RESET}\n")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    items_to_copy = [
        "bot", "api", "webapp", "database", "config", "scripts",
        "nginx", "docker-compose.yml", "Dockerfile.bot", "Dockerfile.api",
        "requirements-bot.txt", "requirements-api.txt"
    ]
    
    os.makedirs(INSTALL_DIR, exist_ok=True)
    
    for item in items_to_copy:
        src = os.path.join(script_dir, item)
        dst = os.path.join(INSTALL_DIR, item)
        if os.path.exists(src):
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            print(f"  {Colors.GREEN}✓{Colors.RESET} Copied {item}")
        else:
            print(f"  {Colors.YELLOW}⚠{Colors.RESET} Skipped {item} (not found)")
    
    os.makedirs(f"{INSTALL_DIR}/nginx/ssl", exist_ok=True)
    os.makedirs(f"{INSTALL_DIR}/backups", exist_ok=True)
    
    print(f"\n  {Colors.GREEN}✓ Project files ready{Colors.RESET}")

def check_status():
    print(f"\n{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.WHITE}  Bot Status{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}\n")
    
    result = subprocess.run(f"cd {INSTALL_DIR} && docker-compose ps", shell=True, capture_output=True, text=True)
    print(f"  {Colors.BOLD}Docker Containers:{Colors.RESET}")
    print(f"  {Colors.DIM}{'─' * 50}{Colors.RESET}")
    
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        for line in lines[2:] if len(lines) > 2 else lines:
            if line.strip():
                print(f"  {status_dot('ok' if 'running' in line.lower() else 'error')} {line}")
    
    print(f"\n  {Colors.BOLD}Disk Usage:{Colors.RESET}")
    stat = shutil.disk_usage(INSTALL_DIR)
    used_gb = stat.used / 1024 / 1024 / 1024
    total_gb = stat.total / 1024 / 1024 / 1024
    percent = (stat.used / stat.total) * 100
    print(f"  {progress_bar(percent, 30)}")
    print(f"  {Colors.DIM}  {used_gb:.1f} GB / {total_gb:.1f} GB{Colors.RESET}")
    
    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")

def view_logs():
    print(f"\n{Colors.CYAN}Opening logs (Ctrl+C to exit)...{Colors.RESET}\n")
    time.sleep(1)
    subprocess.run(f"cd {INSTALL_DIR} && docker-compose logs -f", shell=True)

def restart_bot():
    print(f"\n{Colors.CYAN}Restarting SpeediT...{Colors.RESET}")
    run_cmd(f"cd {INSTALL_DIR} && docker-compose restart", "Restarting services")
    time.sleep(2)

def stop_bot():
    print(f"\n{Colors.YELLOW}Stopping SpeediT...{Colors.RESET}")
    run_cmd(f"cd {INSTALL_DIR} && docker-compose stop", "Stopping services")
    time.sleep(2)

def start_bot():
    print(f"\n{Colors.CYAN}Starting SpeediT...{Colors.RESET}")
    run_cmd(f"cd {INSTALL_DIR} && docker-compose start", "Starting services")
    time.sleep(2)

def update_bot():
    print(f"\n{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.WHITE}  Update SpeediT{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}\n")
    
    run_cmd(f"cd {INSTALL_DIR} && git pull 2>/dev/null || echo 'Not a git repo'", "Pulling latest changes")
    run_cmd(f"cd {INSTALL_DIR} && docker-compose build --no-cache", "Rebuilding images")
    run_cmd(f"cd {INSTALL_DIR} && docker-compose up -d", "Restarting services")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Update complete!{Colors.RESET}")
    time.sleep(2)

def backup():
    print(f"\n{Colors.CYAN}Creating backup...{Colors.RESET}\n")
    backup_dir = f"{INSTALL_DIR}/backups"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/speedit_backup_{timestamp}.tar.gz"
    run_cmd(f"tar -czf {backup_file} -C {INSTALL_DIR} bot api webapp database config .env 2>/dev/null", "Creating backup")
    time.sleep(2)

def restore():
    backup_dir = f"{INSTALL_DIR}/backups"
    if not os.path.exists(backup_dir):
        print(f"\n{Colors.RED}No backups found{Colors.RESET}")
        time.sleep(2)
        return
    
    backups = sorted(Path(backup_dir).glob("*.tar.gz"), reverse=True)
    if not backups:
        print(f"\n{Colors.RED}No backups found{Colors.RESET}")
        time.sleep(2)
        return
    
    print(f"\n{Colors.CYAN}Available backups:{Colors.RESET}\n")
    for i, bp in enumerate(backups[:10], 1):
        size = bp.stat().st_size / 1024 / 1024
        print(f"  {Colors.BOLD}{i}.{Colors.RESET} {bp.name} ({size:.1f} MB)")
    
    print()
    choice = input(f"{Colors.YELLOW}Select backup to restore (or 'cancel'):{Colors.RESET} ").strip()
    
    if choice.lower() == 'cancel' or not choice.isdigit():
        return
    
    idx = int(choice) - 1
    if 0 <= idx < len(backups):
        if confirm_action("This will overwrite current data!"):
            run_cmd(f"cd {INSTALL_DIR} && docker-compose stop", "Stopping services")
            run_cmd(f"tar -xzf {backups[idx]} -C {INSTALL_DIR}", "Extracting backup")
            run_cmd(f"cd {INSTALL_DIR} && docker-compose up -d", "Starting services")
            print(f"\n{Colors.GREEN}✓ Restore complete{Colors.RESET}")
    time.sleep(2)

def uninstall():
    print(f"\n{Colors.RED}{Colors.BOLD}{'═' * 55}{Colors.RESET}")
    print(f"{Colors.RED}{Colors.BOLD}  ⚠ UNINSTALL SpeediT{Colors.RESET}")
    print(f"{Colors.RED}{Colors.BOLD}{'═' * 55}{Colors.RESET}\n")
    
    print(f"  {Colors.RED}This will permanently delete all data!{Colors.RESET}")
    
    if confirm_action("Are you sure you want to uninstall?"):
        print(f"\n{Colors.CYAN}Uninstalling...{Colors.RESET}\n")
        run_cmd(f"cd {INSTALL_DIR} && docker-compose down -v 2>/dev/null", "Stopping containers")
        run_cmd(f"rm -rf {INSTALL_DIR}", "Removing files")
        print(f"{Colors.GREEN}✓ SpeediT has been uninstalled{Colors.RESET}")
        time.sleep(2)
        sys.exit(0)
    else:
        print(f"\n{Colors.YELLOW}Uninstall cancelled{Colors.RESET}")
        time.sleep(2)

def manage():
    while True:
        clear_screen()
        print_header()
        
        choice = show_menu("SpeediT Management", {
            "1": ("Check Status", "📊", Colors.GREEN),
            "2": ("View Logs", "📜", Colors.BLUE),
            "3": ("Restart Bot", "🔄", Colors.YELLOW),
            "4": ("Stop Bot", "⏹️", Colors.RED),
            "5": ("Start Bot", "▶️", Colors.GREEN),
            "6": ("Update", "⬆️", Colors.CYAN),
            "7": ("Backup", "💾", Colors.PURPLE),
            "8": ("Restore", "♻️", Colors.ORANGE),
            "9": ("Uninstall", "🗑️", Colors.RED),
            "0": ("Back", "🔙", Colors.WHITE),
        })
        
        actions = {
            "1": check_status,
            "2": view_logs,
            "3": restart_bot,
            "4": stop_bot,
            "5": start_bot,
            "6": update_bot,
            "7": backup,
            "8": restore,
            "9": uninstall,
        }
        
        if choice == "0":
            break
        elif choice in actions:
            actions[choice]()

def about():
    clear_screen()
    print_header()
    print(f"""
{Colors.CYAN}{Colors.BOLD}About {PROJECT_NAME}{Colors.RESET}
{Colors.DIM}{'═' * 55}{Colors.RESET}

{Colors.BOLD}Version:{Colors.RESET} {PROJECT_VERSION}
{Colors.BOLD}Description:{Colors.RESET} {PROJECT_DESC}

{Colors.BOLD}Features:{Colors.RESET}
  ✅ Multi-Panel Support (Sanaei, Marzban, HM Panel, PasarGuard, Rebecca)
  ✅ Automated VPN Sales
  ✅ Card-to-Card Payment
  ✅ VPS Sales System
  ✅ Reseller Panel Management
  ✅ Modern Telegram Mini App
  ✅ Advanced Admin Panel

{Colors.BOLD}Links:{Colors.RESET}
  📱 Support: {Colors.CYAN}{SUPPORT_TG}{Colors.RESET}
  📢 Channel: {Colors.CYAN}{CHANNEL_TG}{Colors.RESET}
  💻 GitHub: {Colors.CYAN}{GITHUB_URL}{Colors.RESET}

{Colors.DIM}{'═' * 55}{Colors.RESET}
""")
    input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "install":
            install()
        elif command == "manage":
            manage()
        elif command == "update":
            update_bot()
        elif command == "uninstall":
            uninstall()
        else:
            print(f"Unknown command: {command}")
            print(f"Usage: sudo python3 speedit.py [install|manage|update|uninstall]")
        return
    
    while True:
        clear_screen()
        print_header()
        show_links()
        
        choice = show_menu("Main Menu", {
            "1": ("Install SpeediT", "🚀", Colors.GREEN),
            "2": ("Manage SpeediT", "⚙️", Colors.BLUE),
            "3": ("Update SpeediT", "⬆️", Colors.CYAN),
            "4": ("Uninstall SpeediT", "🗑️", Colors.RED),
            "5": ("About", "ℹ️", Colors.WHITE),
            "0": ("Exit", "👋", Colors.WHITE),
        })
        
        if choice == "1":
            install()
        elif choice == "2":
            manage()
        elif choice == "3":
            update_bot()
        elif choice == "4":
            uninstall()
        elif choice == "5":
            about()
        elif choice == "0":
            print(f"\n{Colors.CYAN}Thanks for using {PROJECT_NAME}!{Colors.RESET}")
            print(f"{Colors.DIM}Need help? {SUPPORT_TG}{Colors.RESET}\n")
            sys.exit(0)

if __name__ == "__main__":
    main()

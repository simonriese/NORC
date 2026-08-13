class Logger:
    RED = "\033[0;31m"
    YELLOW = "\033[0;33m"
    GREEN = "\033[1;32m"
    CYAN = "\033[36m"
    PINK = "\033[38;5;206m"
    RESET = "\033[0m"


    @staticmethod
    def info(msg):
        print(f"{Logger.CYAN}[INFO] {msg}{Logger.RESET}")

    @staticmethod
    def warn(msg):
        print(f"{Logger.YELLOW}[WARNING] {msg}{Logger.RESET}")

    @staticmethod
    def error(msg):
        print(f"{Logger.RED}[ERROR] {msg}{Logger.RESET}")

    @staticmethod
    def success(msg):
        print(f"{Logger.GREEN}[SUCCESS] {msg}{Logger.RESET}")

    @staticmethod
    def debug(msg):
        print(f"{Logger.PINK}[DEBUG] {msg}{Logger.RESET}")
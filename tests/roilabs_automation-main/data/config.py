from pathlib import Path


# === Options ===
HEADLESS = True

# === Common ===
ACCOUNTS_FILE = Path("./data/accounts.json")
GOLDEN_JSON_FILE = Path("./current_methods.json")

# === PalmSlots ===
# === Paths ===
PS_LOG_FILE = Path("./logs/PS_methods_diff.log")

# === URLs ===
PS_URL = "https://qt4m1wx8qym1ayz.com/bbV3Qu"

# === Selectors ===
PS_DEPOSIT_BUTTON_SELECTOR = "#deposit-button"
PS_CASHIER_MODAL_SELECTOR = "#cashierModal"
PS_CASHIER_IFRAME_SELECTOR = "#cashierFrame"
PS_LIST_OF_METHODS_SELECTOR = "[data-testid='otherMethods'] > div"
PS_METHOD_SELECTOR = "[data-testid='otherMethods']"
PS_LOGIN_BUTTON = "//button[@data-testid='login-button']"
PS_USERNAME_FIELD = "//input[@id='login_form[username]']"
PS_PASSWORD_FIELD = "//input[@id='login-modal-password-input']"
PS_SUBMIT_BUTTON = "div.popup-login-box button[type='submit']"

# === Rollino ===
# === Paths ===
RO_LOG_FILE = Path("./logs/RO_methods_diff.log")

# === URLs ===
RO_URL = "https://playmaker777.com/"
RO_DEPOSIT_URL = "**/wallet/deposit"
RO_WITHDRAWAL_URL = "**/wallet/withdrawal"

# === Selectors ===
RO_LIST_OF_METHODS_SELECTOR = "//div[contains(@class, 'walletPaymentItemJs')]"
RO_LOGIN_BUTTON = "xpath=//button[@id='headerSignInButton']"
RO_USERNAME_FIELD = "xpath=//input[@id='login']"
RO_PASSWORD_FIELD = "xpath=//input[@id='password']"
RO_SUBMIT_BUTTON = "xpath=//button[@id='popupSubmit']"
RO_DEPOSIT_BUTTON_SELECTOR = "xpath=//button[@aria-label='Deposit']"
RO_WITHDRAW_BUTTON_SELECTOR = "xpath=//a[@id='walletNavWithdraw']"

# === JettBet ===
# === Paths ===
JB_LOG_FILE = Path("./logs/JB_methods_diff.log")

# === URLs ===
JB_URL = "https://jettbet777.com/"
JB_DEPOSIT_URL = "**/wallet/deposit"
JB_WITHDRAWAL_URL = "**/wallet/withdrawal"

# === Selectors ===
JB_LIST_OF_METHODS_SELECTOR = "//div[contains(@class, 'walletPaymentItemJs')]"
JB_LOGIN_BUTTON = "xpath=//button[@id='headerSignInButton']"
JB_USERNAME_FIELD = "xpath=//input[@id='login']"
JB_PASSWORD_FIELD = "xpath=//input[@id='password']"
JB_SUBMIT_BUTTON = "xpath=//button[@id='popupSubmit']"
JB_DEPOSIT_BUTTON_SELECTOR = "xpath=//button[@aria-label='Wallet']"
JB_WITHDRAW_BUTTON_SELECTOR = "xpath=//a[@id='walletNavWithdraw']"


# === CasinoJoy ===
# === Paths ===
CJ_LOG_FILE = Path("./logs/CJ_methods_diff.log")

# === URLs ===
CJ_URL = "https://casinojoy777.com/"

# === Selectors ===
CJ_LIST_OF_METHODS_SELECTOR = "//div[contains(@class, 'walletPaymentItemJs')]"
CJ_DEPOSIT_BUTTON_SELECTOR = "xpath=//button[@id='headerDepositButton']"
CJ_LOGIN_BUTTON = "xpath=//button[@id='headerSignInButton']"
CJ_USERNAME_FIELD = "xpath=//input[@id='login']"
CJ_PASSWORD_FIELD = "xpath=//input[@id='password']"
CJ_SUBMIT_BUTTON = "xpath=//button[@id='popupSubmit']"
CJ_WITHDRAW_BUTTON_SELECTOR = "xpath=//li[@id='walletNavWithdraw']"
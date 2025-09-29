# config.py

# === General Settings ===
PDF_PATH = r"D:\Surya\Myworkspace\Project\rag-mcp-agents\data\MentalHealth.pdf"
MODEL_NAME = "mistral"  # Used by Ollama

# === Email Config ===
SENDER_NAME = "Surya Suresh"
EMAIL_SENDER = "sureshsukumaran99@gmail.com"
EMAIL_PASSWORD = "gqib xjov cpvh momp"  # Use App Password (for Gmail)
#EMAIL_RECEIVER = "sureshsooraj496@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
import os

print("PDF Path:", PDF_PATH)
print("Absolute Path:", os.path.abspath(PDF_PATH))
print("Exists:", os.path.exists(PDF_PATH))
import os

from jinja2 import Environment, FileSystemLoader

# Get configuration from environment variables
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/www")

TEMPLATE_DIR = "templates"
TEMPLATE_SETS = [
    d for d in os.listdir(TEMPLATE_DIR) if os.path.isdir(os.path.join(TEMPLATE_DIR, d))
]


def generate_html_files(state):
    """Generate HTML files from templates using the state data for each template set."""

    # Prepare data normally
    context = state.prepare_template_data()

    # ------------------------------
    # 🔥 NEW: Read honeypot logs
    # ------------------------------
    log_file = "/root/llm-honeypot/logs/honeypot.log"

    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            lines = f.readlines()[-30:]  # last 30 lines
        context["honeypot_logs"] = "<br>".join(line.strip() for line in lines)
    else:
        context["honeypot_logs"] = "No honeypot logs found."
    # ------------------------------

    for template_set in TEMPLATE_SETS:
        template_dir = os.path.join(TEMPLATE_DIR, template_set)
        output_subdir = os.path.join(OUTPUT_DIR, template_set)
        os.makedirs(output_subdir, exist_ok=True)

        env = Environment(loader=FileSystemLoader(template_dir))

        # Generate index.html
        template = env.get_template("index.html")
        output = template.render(**context)
        with open(os.path.join(output_subdir, "index.html"), "w") as f:
            f.write(output)

        # Generate explainer.html
        template = env.get_template("explainer.html")
        output = template.render(**context)
        with open(os.path.join(output_subdir, "explainer.html"), "w") as f:
            f.write(output)


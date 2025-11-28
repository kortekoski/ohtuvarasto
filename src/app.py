"""Flask web application for warehouse management."""
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash
from varasto import Varasto

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory storage for warehouses (name -> Varasto)
warehouses = {}

# In-memory storage for articles (name -> size)
articles = {}


def _parse_float(value, error_msg):
    """Parse a float value and flash error if invalid."""
    try:
        return float(value)
    except ValueError:
        flash(error_msg, "error")
        return None


@app.route("/")
def index():
    """Redirect to warehouses list."""
    return redirect(url_for("list_warehouses"))


@app.route("/warehouses")
def list_warehouses():
    """List all warehouses."""
    return render_template(
        "warehouses.html",
        warehouses=warehouses,
        articles=articles
    )


def _validate_warehouse_name(name):
    """Validate warehouse name and return error message if invalid."""
    if not name:
        return "Warehouse name is required."
    if name in warehouses:
        return f"Warehouse '{name}' already exists."
    return None


@app.route("/warehouses", methods=["POST"])
def create_warehouse():
    """Create a new warehouse."""
    name = request.form.get("name", "").strip()
    capacity = request.form.get("capacity", "0")
    error = _validate_warehouse_name(name)

    if error:
        flash(error, "error")
        return redirect(url_for("list_warehouses"))

    capacity_float = _parse_float(capacity, "Invalid capacity value.")
    if capacity_float is not None:
        warehouses[name] = Varasto(capacity_float)
        flash(f"Warehouse '{name}' created successfully.", "success")

    return redirect(url_for("list_warehouses"))


@app.route("/warehouses/<name>/add", methods=["POST"])
def add_to_warehouse(name):
    """Add content to a warehouse by name."""
    if name not in warehouses:
        flash(f"Warehouse '{name}' not found.", "error")
    else:
        amount = request.form.get("amount", "0")
        amount_float = _parse_float(amount, "Invalid amount value.")
        if amount_float is not None:
            warehouses[name].lisaa_varastoon(amount_float)
            flash(f"Added {amount_float} to '{name}'.", "success")

    return redirect(url_for("list_warehouses"))


@app.route("/warehouses/<name>/remove", methods=["POST"])
def remove_from_warehouse(name):
    """Remove content from a warehouse by name."""
    if name not in warehouses:
        flash(f"Warehouse '{name}' not found.", "error")
    else:
        amount = request.form.get("amount", "0")
        amount_float = _parse_float(amount, "Invalid amount value.")
        if amount_float is not None:
            warehouses[name].ota_varastosta(amount_float)
            flash(f"Removed {amount_float} from '{name}'.", "success")

    return redirect(url_for("list_warehouses"))


@app.route("/warehouses/<name>/delete", methods=["POST"])
def delete_warehouse(name):
    """Delete a warehouse by name."""
    if name in warehouses:
        del warehouses[name]
        flash(f"Warehouse '{name}' deleted.", "success")

    return redirect(url_for("list_warehouses"))


def _validate_article_name(name):
    """Validate article name and return error message if invalid."""
    if not name:
        return "Article name is required."
    if name in articles:
        return f"Article '{name}' already exists."
    return None


def _validate_article_size(size_float):
    """Validate article size and return error message if invalid."""
    if size_float is not None and size_float <= 0:
        return "Article size must be greater than 0."
    return None


def _save_article(name, size):
    """Parse size and save article. Return error message or None."""
    size_float = _parse_float(size, "Invalid size value.")
    size_error = _validate_article_size(size_float)
    if size_error:
        return size_error
    if size_float is not None:
        articles[name] = size_float
    return None


@app.route("/articles", methods=["POST"])
def create_article():
    """Create a new article with a name and size."""
    name = request.form.get("name", "").strip()
    error = _validate_article_name(name)

    if error:
        flash(error, "error")
        return redirect(url_for("list_warehouses"))

    size_error = _save_article(name, request.form.get("size", "0"))
    if size_error:
        flash(size_error, "error")
    elif name in articles:
        flash(f"Article '{name}' created (size: {articles[name]}).", "success")

    return redirect(url_for("list_warehouses"))


@app.route("/articles/<name>/delete", methods=["POST"])
def delete_article(name):
    """Delete an article by name."""
    if name in articles:
        del articles[name]
        flash(f"Article '{name}' deleted.", "success")

    return redirect(url_for("list_warehouses"))


def _try_add_article(wh_name, article_name):
    """Try adding article to warehouse. Returns error message or None."""
    size = articles[article_name]
    available = warehouses[wh_name].paljonko_mahtuu()
    if size > available:
        return f"Not enough space for '{article_name}' (needs {size})."
    warehouses[wh_name].lisaa_varastoon(size)
    return None


def _validate_add_article_request(wh_name, article_name):
    """Validate add-article request. Returns error message or None."""
    if wh_name not in warehouses:
        return f"Warehouse '{wh_name}' not found."
    if article_name not in articles:
        return f"Article '{article_name}' not found."
    return None


@app.route("/warehouses/<wh_name>/add-article", methods=["POST"])
def add_article_to_warehouse(wh_name):
    """Add an article to a warehouse."""
    article_name = request.form.get("article", "").strip()
    error = _validate_add_article_request(wh_name, article_name)

    if error:
        flash(error, "error")
        return redirect(url_for("list_warehouses"))

    add_error = _try_add_article(wh_name, article_name)
    if add_error:
        flash(add_error, "error")
    else:
        flash(f"Added '{article_name}' to '{wh_name}'.", "success")

    return redirect(url_for("list_warehouses"))


if __name__ == "__main__":
    app.run()

"""Flask web application for warehouse management."""
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash
from varasto import Varasto

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory storage for warehouses (name -> Varasto)
warehouses = {}


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
    return render_template("warehouses.html", warehouses=warehouses)


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


if __name__ == "__main__":
    app.run()

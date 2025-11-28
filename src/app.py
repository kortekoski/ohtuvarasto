"""Flask web application for warehouse management."""
from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto

app = Flask(__name__)

# In-memory storage for warehouses (name -> Varasto)
warehouses = {}


@app.route("/")
def index():
    """Redirect to warehouses list."""
    return redirect(url_for("list_warehouses"))


@app.route("/warehouses")
def list_warehouses():
    """List all warehouses."""
    return render_template("warehouses.html", warehouses=warehouses)


@app.route("/warehouses", methods=["POST"])
def create_warehouse():
    """Create a new warehouse."""
    name = request.form.get("name", "").strip()
    capacity = request.form.get("capacity", "0")

    if name and name not in warehouses:
        try:
            capacity_float = float(capacity)
            warehouses[name] = Varasto(capacity_float)
        except ValueError:
            pass

    return redirect(url_for("list_warehouses"))


@app.route("/warehouses/<name>/add", methods=["POST"])
def add_to_warehouse(name):
    """Add content to a warehouse by name."""
    if name in warehouses:
        amount = request.form.get("amount", "0")
        try:
            amount_float = float(amount)
            warehouses[name].lisaa_varastoon(amount_float)
        except ValueError:
            pass

    return redirect(url_for("list_warehouses"))


@app.route("/warehouses/<name>/remove", methods=["POST"])
def remove_from_warehouse(name):
    """Remove content from a warehouse by name."""
    if name in warehouses:
        amount = request.form.get("amount", "0")
        try:
            amount_float = float(amount)
            warehouses[name].ota_varastosta(amount_float)
        except ValueError:
            pass

    return redirect(url_for("list_warehouses"))


@app.route("/warehouses/<name>/delete", methods=["POST"])
def delete_warehouse(name):
    """Delete a warehouse by name."""
    if name in warehouses:
        del warehouses[name]

    return redirect(url_for("list_warehouses"))


if __name__ == "__main__":
    app.run(debug=True)

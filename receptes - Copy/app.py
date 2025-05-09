from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("welcome.html", current_year=datetime.now().year)

@app.route("/receptes")
def recipes():
    conn = get_db_connection()
    recipes = conn.execute("""
        SELECT r.rec_id, r.title, r.description, i.path AS image_path
        FROM recipes r
        LEFT JOIN image i ON r.rec_id = i.rec_id
    """).fetchall()
    conn.close()
    return render_template("recipes.html", recipes=recipes, current_year=datetime.now().year)

@app.route("/about")
def about():
    return render_template("about.html", current_year=datetime.now().year)

@app.route("/recipe/<int:recipe_id>", methods=["GET", "POST"])
def recipe_detail(recipe_id):
    conn = get_db_connection()

    if request.method == "POST":
        author = request.form["author"]
        comment = request.form["comment"]
        conn.execute(
            "INSERT INTO comments (recipe_id, author, comment, created_at) VALUES (?, ?, ?, ?)",
            (recipe_id, author, comment, datetime.now())
        )
        conn.commit()

    recipe = conn.execute("SELECT * FROM recipes WHERE rec_id = ?", (recipe_id,)).fetchone()
    ingredients = conn.execute("SELECT sastavdalas FROM ingredients WHERE rec_id = ?", (recipe_id,)).fetchall()
    comments = conn.execute("SELECT * FROM comments WHERE recipe_id = ? ORDER BY created_at DESC", (recipe_id,)).fetchall()
    conn.close()

    return render_template(
        "recipe_detail.html",
        recipe=recipe,
        ingredients=ingredients,
        comments=comments,
        current_year=datetime.now().year
    )

@app.route("/edit_comment/<int:recipe_id>/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(recipe_id, comment_id):
    conn = get_db_connection()
    comment = conn.execute("SELECT * FROM comments WHERE id = ?", (comment_id,)).fetchone()

    if request.method == "POST":
        new_text = request.form["comment"]
        conn.execute("UPDATE comments SET comment = ? WHERE id = ?", (new_text, comment_id))
        conn.commit()
        conn.close()
        return redirect(url_for("recipe_detail", recipe_id=recipe_id))

    conn.close()
    return render_template("edit_comment.html", comment=comment, recipe_id=recipe_id)

@app.route("/delete_comment/<int:recipe_id>/<int:comment_id>", methods=["POST"])
def delete_comment(recipe_id, comment_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("recipe_detail", recipe_id=recipe_id))

if __name__ == "__main__":
    app.run(debug=True)


# ... (keep your existing recipe_detail route) ...
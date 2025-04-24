from flask import Flask, request, render_template, jsonify
import pandas as pd
import json
from sentence_transformers import SentenceTransformer, util


app = Flask(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')

def categorize_expenses(df, categories):
    df["Category"] = "Uncategorized"

    # Prepare category keywords
    category_keywords = {cat: keywords for cat, keywords in categories.items()}
    all_keywords = [kw for kws in category_keywords.values() for kw in kws]
    keyword_embeddings = model.encode(all_keywords, convert_to_tensor=True)

    for idx, row in df.iterrows():
        description = row["Description"]
        if pd.isna(description):
            continue
        desc_embedding = model.encode(description, convert_to_tensor=True)
        cosine_scores = util.cos_sim(desc_embedding, keyword_embeddings)[0]
        max_score_idx = cosine_scores.argmax().item()
        max_score = cosine_scores[max_score_idx].item()
        if max_score > 0.4:  # Adjust threshold as needed
            matched_keyword = all_keywords[max_score_idx]
            # Find the category for the matched keyword
            for category, keywords in category_keywords.items():
                if matched_keyword in keywords:
                    df.at[idx, "Category"] = category
                    break
    return df

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files.get("file")  # Using get() to prevent KeyError
    if not file:
        return jsonify({"error": "No file provided"}), 400  # Returning JSON as expected

    try:
        df = pd.read_csv(file)
    except:
        return jsonify({"error": "Could not read the CSV file."}), 400  # Returning JSON for errors

    required_cols = {"Date", "Description", "Amount"}
    if not required_cols.issubset(df.columns):
        return jsonify({"error": "CSV must include Date, Description, and Amount columns"}), 400  # JSON error message

    with open("categories.json") as f:
        categories = json.load(f)

    df = categorize_expenses(df, categories)
    grouped = df.groupby("Category")["Amount"].sum().reset_index()

    # Sort categories by amount in descending order
    grouped_sorted = grouped.sort_values(by="Amount", ascending=False)

    # Extract top 3 categories
    top_categories = grouped_sorted["Category"].head(3).tolist()

    return jsonify({
        "labels": grouped["Category"].tolist(),
        "values": grouped["Amount"].tolist(),
        "top_categories": top_categories
    })

if __name__ == "__main__":
    app.run(debug=True)

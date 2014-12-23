
from flask import jsonify
from vlasisku.extensions import database

def query(query):
    db = database.root
    query = query.replace('+', ' ')
    results = db.query(query)

    # Convert all Entry objects into strings.
    for k, v in results.items():
        if isinstance(v, list) or isinstance(v, set):
            results[k] = [str(e) for e in v]

    return jsonify(results)

def valsi(query):
    db = database.root
    query = query.replace('+', ' ')
    results = db.query(query)

    if results['entry'] is None:
        return jsonify({})
    else:
        return jsonify(results['entry'].to_api_object())

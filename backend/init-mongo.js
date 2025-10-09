// MongoDB initialization script for Docker
db = db.getSiblingDB('airms');

// Create collections with validation
db.createCollection('users');
db.createCollection('sessions');
db.createCollection('risk_assessments');
db.createCollection('daily_analytics');
db.createCollection('api_keys');

print('AIRMS MongoDB database initialized successfully!');

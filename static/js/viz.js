// Define your data (replace these with your actual data)
var states = ["AL", "AK", "AZ", "AR", "CA"]; // example list of states
var fraudulent_transactions_by_state = [10, 20, 30, 40, 50]; // example list of fraudulent transactions

// Create the choropleth map using Plotly.js
var state_map = {
    type: 'choropleth',
    locationmode: 'USA-states',
    locations: states,
    z: fraudulent_transactions_by_state,
    colorscale: 'Reds',
    colorbar: {
        title: 'Fraudulent Transactions'
    }
};

// Define layout options for the map
var layout = {
    title: 'Fraudulent Transactions by State',
    geo: {
        scope: 'usa'
    }
};

// Combine data and layout and plot the map
Plotly.newPlot('map-container', [state_map], layout);
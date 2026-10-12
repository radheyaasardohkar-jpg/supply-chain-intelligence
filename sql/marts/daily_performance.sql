
SELECT
    Date,
    SUM("Units Sold") AS total_units_sold,
    SUM("Units Ordered") AS total_units_ordered,
    ROUND(AVG("Inventory Level"), 2) AS average_inventory,
    ROUND(AVG("Demand Forecast"), 2) AS average_demand_forecast,
    ROUND(AVG(Price), 2) AS average_price
FROM retail_inventory
GROUP BY Date
ORDER BY Date;

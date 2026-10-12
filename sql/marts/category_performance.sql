SELECT
    Category,
    COUNT(*) AS record_count,
    SUM("Units Sold") AS total_units_sold,
    ROUND(AVG("Units Sold"), 2) AS average_units_sold,
    ROUND(AVG("Inventory Level"), 2) AS average_inventory,
    ROUND(AVG(Price), 2) AS average_price
FROM retail_inventory
GROUP BY Category
ORDER BY total_units_sold DESC;
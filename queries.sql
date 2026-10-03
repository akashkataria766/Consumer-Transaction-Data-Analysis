-- 1. Monthly revenue summary
SELECT
    TRUNC(order_date, 'MM') AS order_month,
    COUNT(*) AS total_orders,
    SUM(amount) AS total_revenue
FROM transactions_clean
GROUP BY TRUNC(order_date, 'MM')
ORDER BY order_month;

-- 2. Revenue by category with a category lookup JOIN
WITH category_lookup AS (
    SELECT 'Electronics' AS category FROM dual
    UNION ALL SELECT 'Clothing' FROM dual
    UNION ALL SELECT 'Home & Kitchen' FROM dual
    UNION ALL SELECT 'Books' FROM dual
)
SELECT
    lookup.category,
    COUNT(transactions.txn_id) AS total_orders,
    NVL(SUM(transactions.amount), 0) AS total_revenue
FROM category_lookup lookup
LEFT JOIN transactions_clean transactions
    ON transactions.category = lookup.category
GROUP BY lookup.category
ORDER BY total_revenue DESC;

-- 3. Data discrepancy check using UNION ALL
SELECT 'MISSING_CUSTOMER_ID' AS issue_type, COUNT(*) AS issue_count
FROM transactions_clean
WHERE customer_id IS NULL
UNION ALL
SELECT 'INVALID_STATUS' AS issue_type, COUNT(*) AS issue_count
FROM transactions_clean
WHERE status NOT IN ('COMPLETED', 'PENDING', 'CANCELLED')
UNION ALL
SELECT 'NON_POSITIVE_AMOUNT' AS issue_type, COUNT(*) AS issue_count
FROM transactions_clean
WHERE amount <= 0;

-- 4. Top 10 customers using the RANK() window function
SELECT customer_id, total_spend, customer_rank
FROM (
    SELECT
        customer_id,
        SUM(amount) AS total_spend,
        RANK() OVER (ORDER BY SUM(amount) DESC) AS customer_rank
    FROM transactions_clean
    GROUP BY customer_id
)
WHERE customer_rank <= 10
ORDER BY customer_rank, customer_id;

-- 5. Order status breakdown with percentage using SUM() OVER
SELECT
    status,
    COUNT(*) AS order_count,
    ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM transactions_clean
GROUP BY status
ORDER BY order_count DESC;

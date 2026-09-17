-- POSTGRESQL SOURCE : sales_targets--

CREATE TABLE IF NOT EXISTS sales_targets (
    id SERIAL PRIMARY KEY,
    region VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    target NUMERIC(12, 2) NOT NULL,
    UNIQUE(region, year)
);

-- Objectifs annuels par région (données fictives réalistes)
INSERT INTO sales_targets (region, year, target) VALUES
    ('South', 2014, 130000.00),
    ('South', 2015, 145000.00),
    ('South', 2016, 160000.00),
    ('South', 2017, 180000.00),
    ('West', 2014, 180000.00),
    ('West', 2015, 195000.00),
    ('West', 2016, 210000.00),
    ('West', 2017, 230000.00),
    ('Central', 2014, 120000.00),
    ('Central', 2015, 135000.00),
    ('Central', 2016, 150000.00),
    ('Central', 2017, 165000.00),
    ('East', 2014, 160000.00),
    ('East', 2015, 175000.00),
    ('East', 2016, 190000.00),
    ('East', 2017, 210000.00)
ON CONFLICT (region, year) DO NOTHING;
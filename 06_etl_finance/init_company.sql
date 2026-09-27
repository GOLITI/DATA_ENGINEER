-- SOURCE : base company (référentiel entreprises)
CREATE TABLE IF NOT EXISTS companies (
    id           SERIAL PRIMARY KEY,
    ticker       VARCHAR(10) NOT NULL UNIQUE,
    name         VARCHAR(100) NOT NULL,
    sector       VARCHAR(50) NOT NULL,
    region       VARCHAR(30) NOT NULL,
    country      VARCHAR(50) NOT NULL
);

INSERT INTO companies (ticker, name, sector, region, country) VALUES
    ('AAPL',   'Apple Inc.',           'Technology',    'Americas',     'USA'),
    ('MSFT',   'Microsoft Corp.',      'Technology',    'Americas',     'USA'),
    ('GOOGL',  'Alphabet Inc.',        'Technology',    'Americas',     'USA'),
    ('AMZN',   'Amazon.com Inc.',      'Consumer',      'Americas',     'USA'),
    ('TSLA',   'Tesla Inc.',           'Automotive',    'Americas',     'USA'),
    ('NVDA',   'NVIDIA Corp.',         'Technology',    'Americas',     'USA'),
    ('JPM',    'JPMorgan Chase',       'Finance',       'Americas',     'USA'),
    ('V',      'Visa Inc.',            'Finance',       'Americas',     'USA'),
    ('JNJ',    'Johnson & Johnson',    'Healthcare',    'Americas',     'USA'),
    ('WMT',    'Walmart Inc.',         'Retail',        'Americas',     'USA'),
    ('NESN',   'Nestlé S.A.',          'Consumer',      'Europe',       'Switzerland'),
    ('ASML',   'ASML Holding',         'Technology',    'Europe',       'Netherlands'),
    ('MC',     'LVMH',                 'Luxury',        'Europe',       'France'),
    ('SAP',    'SAP SE',               'Technology',    'Europe',       'Germany'),
    ('7203',   'Toyota Motor',         'Automotive',    'Asia-Pacific', 'Japan'),
    ('9984',   'SoftBank Group',       'Technology',    'Asia-Pacific', 'Japan'),
    ('BABA',   'Alibaba Group',        'Retail',        'Asia-Pacific', 'China'),
    ('005930', 'Samsung Electronics',  'Technology',    'Asia-Pacific', 'South Korea')
ON CONFLICT (ticker) DO NOTHING;
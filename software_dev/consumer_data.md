# Consumer Data

Certainly! Here's a brief hands-on example of how you could work with data in each of these domains within a job description context:

### 1. **Retail Product Data**
**Example:**
Design and maintain a comprehensive retail product database that includes details like SKU, product name, description, price, availability, and supplier information. Implement data cleaning scripts to ensure data integrity and develop APIs for real-time inventory updates.

```sql
-- Create a table for retail products
CREATE TABLE RetailProducts (
    ProductID INT PRIMARY KEY,
    SKU VARCHAR(50) NOT NULL,
    ProductName VARCHAR(100),
    Description TEXT,
    Price DECIMAL(10, 2),
    Availability INT,
    SupplierID INT
);

-- Insert example data
INSERT INTO RetailProducts (ProductID, SKU, ProductName, Description, Price, Availability, SupplierID)
VALUES
(1, 'SKU12345', 'Laptop', '15 inch laptop with 16GB RAM', 999.99, 50, 101),
(2, 'SKU67890', 'Smartphone', 'Latest model smartphone with 128GB storage', 699.99, 30, 102);

-- Query to check inventory levels
SELECT ProductName, Availability
FROM RetailProducts
WHERE Availability < 20;
```

### 2. **Ecommerce Data**
**Example:**
Design and implement a data pipeline to collect and analyze ecommerce transactions, including order details, customer information, and payment methods. Create dashboards to track sales performance and customer purchasing trends.

```python
import pandas as pd

# Sample ecommerce transaction data
data = {
    'OrderID': [1, 2, 3],
    'CustomerID': [101, 102, 103],
    'ProductID': [1, 2, 1],
    'Quantity': [1, 2, 1],
    'Price': [999.99, 699.99, 999.99],
    'OrderDate': ['2024-06-01', '2024-06-02', '2024-06-03']
}

# Create DataFrame
df = pd.DataFrame(data)

# Calculate total sales
df['TotalSales'] = df['Quantity'] * df['Price']

# Group by product to get sales summary
sales_summary = df.groupby('ProductID').agg({'TotalSales': 'sum'})

print(sales_summary)
```

### 3. **Consumer Profile Data**
**Example:**
Create a centralized repository for consumer profile data, including demographic information, purchase history, and preferences. Implement data enrichment processes to enhance profiles with third-party data.

```sql
-- Create a table for consumer profiles
CREATE TABLE ConsumerProfiles (
    CustomerID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100),
    Age INT,
    Gender VARCHAR(10),
    PurchaseHistory JSON
);

-- Insert example data
INSERT INTO ConsumerProfiles (CustomerID, FirstName, LastName, Email, Age, Gender, PurchaseHistory)
VALUES
(101, 'John', 'Doe', 'john.doe@example.com', 30, 'Male', '[{"ProductID": 1, "PurchaseDate": "2024-06-01"}]'),
(102, 'Jane', 'Smith', 'jane.smith@example.com', 25, 'Female', '[{"ProductID": 2, "PurchaseDate": "2024-06-02"}]');

-- Query to get consumer profiles by age group
SELECT * FROM ConsumerProfiles
WHERE Age BETWEEN 25 AND 35;
```

### 4. **Clickstream Data**
**Example:**
Set up a clickstream data collection system to track user interactions on the website. Use this data to analyze user behavior, identify popular pages, and improve site navigation.

```python
import pandas as pd

# Sample clickstream data
data = {
    'SessionID': [1, 1, 2, 2, 3],
    'UserID': [101, 101, 102, 102, 103],
    'Page': ['Home', 'Product', 'Home', 'Checkout', 'Home'],
    'Timestamp': ['2024-06-01 10:00:00', '2024-06-01 10:05:00', '2024-06-02 11:00:00', '2024-06-02 11:10:00', '2024-06-03 12:00:00']
}

# Create DataFrame
df = pd.DataFrame(data)

# Analyze most visited pages
page_visits = df['Page'].value_counts()

print(page_visits)
```

### 5. **Consumer Event Data**
**Example:**
Implement an event tracking system to log consumer events such as product views, add-to-cart actions, and purchases. Use this data to trigger personalized marketing campaigns.

```javascript
// Example JavaScript code to log consumer events
function logEvent(eventType, userID, productID) {
    const event = {
        eventType: eventType,
        userID: userID,
        productID: productID,
        timestamp: new Date().toISOString()
    };

    // Send event to server (example URL)
    fetch('https://example.com/log_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(event)
    }).then(response => response.json())
      .then(data => console.log('Event logged:', data))
      .catch(error => console.error('Error logging event:', error));
}

// Log an example event
logEvent('add_to_cart', 101, 1);
```

### 6. **Marketing Channel/Campaign Data**
**Example:**
Track and analyze data from various marketing channels and campaigns. Create reports to measure the effectiveness of different campaigns and optimize marketing spend.

```sql
-- Create a table for marketing campaigns
CREATE TABLE MarketingCampaigns (
    CampaignID INT PRIMARY KEY,
    Channel VARCHAR(50),
    StartDate DATE,
    EndDate DATE,
    Budget DECIMAL(10, 2),
    Conversions INT
);

-- Insert example data
INSERT INTO MarketingCampaigns (CampaignID, Channel, StartDate, EndDate, Budget, Conversions)
VALUES
(1, 'Email', '2024-06-01', '2024-06-07', 500.00, 50),
(2, 'Social Media', '2024-06-01', '2024-06-07', 1000.00, 80);

-- Query to calculate cost per conversion
SELECT Channel, Budget / Conversions AS CostPerConversion
FROM MarketingCampaigns;
```

### 7. **Affiliate Data**
**Example:**
Set up a system to manage and track affiliate data, including affiliate IDs, referral links, and commission rates. Generate reports on affiliate performance and calculate commissions.

```sql
-- Create a table for affiliate data
CREATE TABLE Affiliates (
    AffiliateID INT PRIMARY KEY,
    AffiliateName VARCHAR(100),
    ReferralLink VARCHAR(255),
    CommissionRate DECIMAL(5, 2)
);

-- Insert example data
INSERT INTO Affiliates (AffiliateID, AffiliateName, ReferralLink, CommissionRate)
VALUES
(1, 'Affiliate A', 'https://example.com/ref/1', 0.05),
(2, 'Affiliate B', 'https://example.com/ref/2', 0.07);

-- Query to calculate total commission for an affiliate
SELECT a.AffiliateName, SUM(t.TotalAmount * a.CommissionRate) AS TotalCommission
FROM Transactions t
JOIN Affiliates a ON t.ReferralLink = a.ReferralLink
WHERE a.AffiliateID = 1
GROUP BY a.AffiliateName;
```

### 8. **Retailer/Brand Data**
**Example:**
Maintain a database of retailer and brand information, including contact details, product lines, and sales agreements. Use this data to manage relationships and track performance.

```sql
-- Create a table for retailer/brand data
CREATE TABLE Retailers (
    RetailerID INT PRIMARY KEY,
    RetailerName VARCHAR(100),
    ContactPerson VARCHAR(100),
    ContactEmail VARCHAR(100),
    ProductLines JSON
);

-- Insert example data
INSERT INTO Retailers (RetailerID, RetailerName, ContactPerson, ContactEmail, ProductLines)
VALUES
(1, 'Retailer A', 'John Doe', 'john.doe@example.com', '["Electronics", "Home Appliances"]'),
(2, 'Retailer B', 'Jane Smith', 'jane.smith@example.com', '["Clothing", "Accessories"]');

-- Query to get retailers with specific product lines
SELECT * FROM Retailers
WHERE JSON_CONTAINS(ProductLines, '"Electronics"');
```

These examples demonstrate how you could design and work with data in each of these domains, implementing various data models, performing analysis, and generating reports to support business operations and decision-making.
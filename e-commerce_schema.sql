CREATE TABLE "ecommerce_transactions" (
	"transaction_id" VARCHAR(180),
	"customer_id" VARCHAR(180),
	"transaction_amount" FLOAT,
	"transaction_date" DATE,
	"payment_method" VARCHAR(20),
	"product_category" VARCHAR(40),
	"quantity" INT,
	"customer_age" INT,
	"customer_location" VARCHAR(80),
	"device_used" VARCHAR(20),
	"IP_address" VARCHAR (30),
	"shipping_address" VARCHAR(80),
	"billing_address" VARCHAR(80),
	"is_fraudulent" INT,
	"account_age_days" INT,
	"transaction_hour" INT
);

SELECT * FROM ecommerce_transactions
LIMIT 10;
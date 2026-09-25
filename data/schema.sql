-- SmartShelf Relational Schema (Canonical DDL)
-- Generated from SQLAlchemy ORM metadata

CREATE TABLE brands (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE TABLE categories (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	parent_id INTEGER, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	FOREIGN KEY(parent_id) REFERENCES categories (id)
);

CREATE TABLE customers (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	phone VARCHAR(20), 
	email VARCHAR(120), 
	address TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE locations (
	id INTEGER NOT NULL, 
	code VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	zone VARCHAR(50), 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (code)
);

CREATE TABLE suppliers (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	contact_person VARCHAR(120), 
	email VARCHAR(120), 
	phone VARCHAR(20), 
	address TEXT, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	full_name VARCHAR(100) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	phone VARCHAR(20), 
	is_active BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	failed_attempts INTEGER, 
	locked_until DATETIME, 
	totp_secret VARCHAR(64), 
	totp_enabled BOOLEAN, 
	must_change_password BOOLEAN, 
	last_login_at DATETIME, 
	last_login_ip VARCHAR(45), 
	PRIMARY KEY (id)
);

CREATE TABLE audit_logs (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	action VARCHAR(50) NOT NULL, 
	entity_type VARCHAR(50), 
	entity_id INTEGER, 
	details TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE login_logs (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	ip_address VARCHAR(45), 
	user_agent VARCHAR(255), 
	success BOOLEAN NOT NULL, 
	method VARCHAR(20), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE products (
	id INTEGER NOT NULL, 
	sku VARCHAR(50) NOT NULL, 
	barcode VARCHAR(50), 
	name VARCHAR(150) NOT NULL, 
	description TEXT, 
	category_id INTEGER, 
	brand_id INTEGER, 
	unit VARCHAR(20), 
	unit_price FLOAT NOT NULL, 
	cost_price FLOAT NOT NULL, 
	tax_rate FLOAT, 
	shelf_life_days INTEGER, 
	storage_condition VARCHAR(20), 
	reorder_level INTEGER, 
	lead_time_days INTEGER, 
	image_url VARCHAR(255), 
	is_perishable BOOLEAN, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id), 
	FOREIGN KEY(brand_id) REFERENCES brands (id)
);

CREATE TABLE purchase_orders (
	id INTEGER NOT NULL, 
	po_number VARCHAR(50) NOT NULL, 
	supplier_id INTEGER NOT NULL, 
	order_date DATETIME, 
	expected_date DATETIME, 
	status VARCHAR(20), 
	total_amount FLOAT, 
	created_by INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (po_number), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);

CREATE TABLE sales (
	id INTEGER NOT NULL, 
	invoice_number VARCHAR(50) NOT NULL, 
	customer_id INTEGER, 
	user_id INTEGER, 
	sale_date DATETIME, 
	subtotal FLOAT, 
	discount_amount FLOAT, 
	tax_amount FLOAT, 
	total_amount FLOAT, 
	status VARCHAR(20), 
	payment_method VARCHAR(20), 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE location_transfers (
	id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	from_location_id INTEGER NOT NULL, 
	to_location_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	transferred_by INTEGER, 
	transferred_at DATETIME, 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(from_location_id) REFERENCES locations (id), 
	FOREIGN KEY(to_location_id) REFERENCES locations (id), 
	FOREIGN KEY(transferred_by) REFERENCES users (id)
);

CREATE TABLE notifications (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	title VARCHAR(120) NOT NULL, 
	message TEXT NOT NULL, 
	notification_type VARCHAR(20) NOT NULL, 
	severity VARCHAR(20), 
	product_id INTEGER, 
	link VARCHAR(120), 
	is_read INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE payments (
	id INTEGER NOT NULL, 
	sale_id INTEGER NOT NULL, 
	method VARCHAR(20), 
	amount FLOAT NOT NULL, 
	paid_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sale_id) REFERENCES sales (id)
);

CREATE TABLE promotions (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	description TEXT, 
	discount_type VARCHAR(20) NOT NULL, 
	value FLOAT NOT NULL, 
	suggested_discount FLOAT, 
	product_id INTEGER, 
	category_id INTEGER, 
	min_quantity INTEGER, 
	start_date DATETIME, 
	end_date DATETIME, 
	status VARCHAR(20), 
	created_by INTEGER, 
	approved_by INTEGER, 
	approved_at DATETIME, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id), 
	FOREIGN KEY(created_by) REFERENCES users (id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);

CREATE TABLE purchase_order_items (
	id INTEGER NOT NULL, 
	purchase_order_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	received_quantity INTEGER, 
	unit_cost FLOAT NOT NULL, 
	batch_code VARCHAR(50), 
	expiry_date DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE stock_batches (
	id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	location_id INTEGER, 
	supplier_id INTEGER, 
	batch_code VARCHAR(50) NOT NULL, 
	batch_number VARCHAR(50), 
	quantity INTEGER NOT NULL, 
	cost_price FLOAT, 
	manufactured_date DATETIME, 
	expiry_date DATETIME, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(location_id) REFERENCES locations (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id)
);

CREATE TABLE inventory_movements (
	id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	location_id INTEGER, 
	batch_id INTEGER, 
	movement_type VARCHAR(20) NOT NULL, 
	quantity INTEGER NOT NULL, 
	reference VARCHAR(50), 
	notes TEXT, 
	created_by INTEGER, 
	movement_date DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(location_id) REFERENCES locations (id), 
	FOREIGN KEY(batch_id) REFERENCES stock_batches (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);

CREATE TABLE sale_items (
	id INTEGER NOT NULL, 
	sale_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	batch_id INTEGER, 
	quantity INTEGER NOT NULL, 
	unit_price FLOAT NOT NULL, 
	discount_amount FLOAT, 
	line_total FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sale_id) REFERENCES sales (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(batch_id) REFERENCES stock_batches (id)
);

CREATE TABLE wastage (
	id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	batch_id INTEGER, 
	location_id INTEGER, 
	quantity INTEGER NOT NULL, 
	reason VARCHAR(20), 
	unit_cost FLOAT, 
	potential_loss FLOAT, 
	recovered_revenue FLOAT, 
	savings FLOAT, 
	recorded_by INTEGER, 
	recorded_at DATETIME, 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(batch_id) REFERENCES stock_batches (id), 
	FOREIGN KEY(location_id) REFERENCES locations (id), 
	FOREIGN KEY(recorded_by) REFERENCES users (id)
);

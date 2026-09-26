-- SmartShelf demo seed data.
--
-- NOTE: User accounts (admin/admin123, manager/manager123, cashier/cashier123)
-- are created by the `seed` CLI command because their bcrypt password hashes are
-- generated at runtime. Run one of:
--     flask --app app init-db && flask --app app seed
--   or
--     flask --app app init-sql   (this file requires tables to exist first)
--
-- This file inserts the non-user reference + inventory demo data.

-- Categories
INSERT INTO categories (name, description, is_active) VALUES
  ('Fresh Produce', 'Fruits and vegetables', 1),
  ('Dairy', 'Milk, curd, cheese, butter', 1),
  ('Bakery', 'Bread, buns, pastries', 1);

-- Brand
INSERT INTO brands (name, description, is_active) VALUES
  ('DemoBrand', 'Demo supplier brand', 1);

-- Products
INSERT INTO products
  (name, sku, barcode, unit, unit_price, cost_price, shelf_life_days, storage_condition,
   is_perishable, reorder_level, lead_time_days, category_id, brand_id, is_active)
VALUES
  ('Milk 1L', 'MILK1', '8901030000014', 'btl', 60.0, 40.0, 7, 'CHILLED', 1, 20, 2, 2, 1, 1),
  ('Bread Loaf', 'BRD1', '8901030000021', 'loaf', 50.0, 32.0, 5, 'AMBIENT', 1, 15, 1, 3, 1, 1),
  ('Curd 500g', 'CRD1', '8901030000038', 'cup', 52.0, 35.0, 8, 'CHILLED', 1, 18, 2, 2, 1, 1),
  ('Tomatoes 500g', 'TOM500', '8901030000045', 'pk', 45.0, 28.0, 5, 'AMBIENT', 1, 30, 1, 1, 1, 1);

-- Locations
INSERT INTO locations (code, name, zone) VALUES
  ('A1', 'Shelf A1', 'Dairy'),
  ('B2', 'Shelf B2', 'Fresh'),
  ('C3', 'Shelf C3', 'Bakery');

-- Supplier
INSERT INTO suppliers (name, contact_person, phone, is_active) VALUES
  ('Acme Foods', 'Jane', '555-0100', 1);

-- Note: Stock batches depend on uploaded/incoming goods with runtime expiry dates,
-- so they are inserted by the `seed` CLI command (which also computes dates
-- relative to today). See app/cli seed in `cli.py`.

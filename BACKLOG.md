# ShuttleSync Capstone — Development Backlog

Complete task list to rebuild this capstone website from scratch, organized by phase.

---

## Phase 1 — Project Foundation

- [ ] Set up hosting + domain (hipowerbc.xyz), HTTPS
- [ ] `.htaccess` — URL rewriting, extensionless URLs, security headers, protect `.env`/`.ini`/`.sql`, disable directory listing
- [ ] `.env` config loader class (`includes/config.php`) — DB credentials, payment keys, app URL
- [ ] PDO database connection (`includes/database_connect.php`) with prepared statements
- [ ] Create MySQL database tables: `Users`, `Courts`, `Bookings`, `Products`, `Orders`, `Cart_Items`, `Order_Items`, `Announcements`, `Payments`, `Password_Resets`
- [ ] Tailwind CSS + config (CDN, color tokens, fonts — Geist, Material Symbols)
- [ ] Shared UI: `nav_bar.php`, `mobile_nav.php`, `footer.php`, `header.php`
- [ ] Logo + favicon + product/court seed images

## Phase 2 — Authentication

- [ ] `register.php` — account creation with validation + password hashing
- [ ] `login.php` — session-based login, role check (Player / Admin / Head Manager)
- [ ] `logout.php`
- [ ] `forgot_password.php` — request password reset
- [ ] `send_code.php` — generate 6-digit code + use PHPMailer (currently broken, uses plain `mail()`)
- [ ] `verify_code.php` — code verification
- [ ] `reset_password.php` — set new password
- [ ] CSRF protection helper (`includes/csrf_helper.php`)
- [ ] Session security (regenerate ID, expiry)

## Phase 3 — Court Booking

- [ ] `courtbooking.php` — calendar/date picker, court grid (open/booked/maintenance), overlap detection
- [ ] Court list rendered from `Courts` table
- [ ] Booking creation → status `Pending Payment`, player count, duration-based pricing (₱300/hr), booking reference `#B-XXXXX`
- [ ] `book_and_pay.php` — booking summary + payment method selection
- [ ] Double-booking prevention (transaction + overlap SQL check)
- [ ] Confirmed booking updates court availability

## Phase 4 — E-commerce

- [ ] `ecommerce.php` — product grid, search, category filter, sort (price/name/newest)
- [ ] `products/product.php` — product detail page
- [ ] `cart.php` — cart items, quantity update, remove, cart → checkout flow
- [ ] `Cart_Items` DB table with user binding
- [ ] Order creation with order number `ORD-YYYYMMDD-XXXXXX` + tax (8% via `PAYMENT_TAX_RATE`)
- [ ] Order status lifecycle: Pending → Confirmed → Completed/Cancelled
- [ ] Stock inventory (deduct on order)

## Phase 5 — AI Movement Analysis

- [ ] `aimovementanalysis.php` — upload/video UI, analysis states (idle/processing/telemetry)
- [ ] Python backend: `ai/analysis_engine.py` — MediaPipe pose detection
- [ ] `ai/requirements.txt` + `ai/install.sh` + Python virtualenv setup (`ai/venv/`)
- [ ] PHP↔Python bridge (upload → exec script → JSON results)
- [ ] Biomechanics scoring: accuracy, form, stroke telemetry, telemetry metrics
- [ ] Result persistence + history per user
- [ ] Error handling when Python/MediaPipe unavailable

## Phase 6 — Admin Panel

- [ ] `admin/index.php` / `dashboard.php` — revenue, bookings, orders, user counts, recent activity
- [ ] `admin/court_status.php` — manage court availability/maintenance
- [ ] `admin/inventory.php` — product CRUD, stock management, active/inactive
- [ ] `admin/user_bookings.php` — view/manage all bookings
- [ ] `admin/user_orders.php` — manage orders
- [ ] `admin/analytics.php` — reports/charts
- [ ] `admin/announcements.php` — create announcements with audience targeting
- [ ] `admin/ai_lab.php` — AI analysis admin view
- [ ] `admin/includes/admin_header.php` — sidebar layout
- [ ] Role-based access control (Admin/Head Manager only)

## Phase 7 — Payments

- [ ] `paypal_handler.php` — PayPal Orders v2 API, token, capture, sandbox/live mode
- [ ] `paymongo_handler.php` — GCash via PayMongo Checkout Sessions
- [ ] `booking_handler.php` — single-booking direct pay (PayPal + GCash)
- [ ] `payment/webhook.php` — payment confirmation webhooks → update Bookings/Orders
- [ ] Polling-based status checks (`check_status`)
- [ ] Pay with Maya — on hold until Maya Business account/API keys approved (sandbox → production)
- [ ] Tax computation & line items per gateway

## Phase 8 — Player Dashboard & Support

- [ ] `playerdashboard.php` — profile, skill level update, booking history, cancel booking, timers, order history
- [ ] `support.php` — contact, help center/FAQ, terms, privacy (4 tabs)
- [ ] Tidio live chat integration (navbar)
- [ ] Announcements notifications dropdown (targeted by role/skill)

## Phase 9 — Polish, Testing & Launch

- [ ] Responsive/mobile QA on all pages (bottom mobile nav)
- [ ] Empty states, error handling, input validation
- [ ] PHP lint across all files + Python syntax check
- [ ] Security review (XSS escaping, SQL injection, CSRF)
- [ ] Live session counts, dashboard metrics sanity check
- [ ] Seed/test data + final screenshot documentation for capstone submission

---

## Blockers / Known Risks

- **`send_code.php`** uses plain `mail()` — replace with PHPMailer for reliable delivery
- **Pay with Maya** — blocked pending Maya Business account + API key approval (sandbox → production)
- **AI module** — depends on Python venv + MediaPipe working on the server